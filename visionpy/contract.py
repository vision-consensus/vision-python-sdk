import itertools
from Crypto.Hash import keccak
from typing import Union, Optional, Any, List

from eth_utils import decode_hex

import visionpy
from visionpy import keys
from visionpy.abi import vs_abi


def keccak256(data: bytes) -> bytes:
    hasher = keccak.new(digest_bits=256)
    hasher.update(data)
    return hasher.digest()


def assure_bytes(value: Union[str, bytes]) -> bytes:
    if isinstance(value, (str,)):
        return bytes.fromhex(value)
    if isinstance(value, (bytes,)):
        return value
    raise ValueError("bad bytes format")


class Contract(object):
    """A smart contract object."""

    def __init__(
        self,
        addr=None,
        *,
        bytecode: Union[str, bytes] = '',
        name: str = None,
        abi: Optional[List[dict]] = None,
        user_resource_percent: int = 100,
        origin_entropy_limit: int = 1,
        origin_address: str = None,
        owner_address: str = "460000000000000000000000000000000000000000",
        client=None,
    ):
        self.contract_address = addr
        """Address of the contract"""

        self._bytecode = assure_bytes(bytecode)

        self.name = name
        """Name of the contract"""

        self.abi = abi or []
        """ABI list of the contract"""

        self.user_resource_percent = user_resource_percent
        """User resource percent, default 100"""

        self.origin_entropy_limit = origin_entropy_limit
        """Origin entropy limit, default 1"""

        self.origin_address = origin_address
        """Origin address of the contract, i.e. contract creator"""

        self.owner_address = owner_address
        """Current transaction owner's address, to call or trigger contract"""

        self._functions = None
        self._events = None
        self._client = client

    def __str__(self):
        return "<Contract {} {}>".format(self.name, self.contract_address)

    @property
    def bytecode(self):
        """Bytecode of the contract, in ``hex`` format"""
        return self._bytecode.hex()

    @bytecode.setter
    def bytecode(self, value):
        self._bytecode = assure_bytes(value)

    def deploy(self) -> Any:
        if self.contract_address:
            raise RuntimeError("this contract has already deployed to {}".format(self.contract_address))

        if self.origin_address != self.owner_address:
            raise RuntimeError("origin address and owner address mismatch")

        return self._client.vs._build_transaction(
            "CreateSmartContract",
            {
                "owner_address": keys.to_hex_address(self.owner_address),
                "new_contract": {
                    "origin_address": keys.to_hex_address(self.origin_address),
                    "abi": {"entrys": self.abi},
                    "bytecode": self.bytecode,
                    "call_value": 0,  # TODO
                    "name": self.name,
                    "consume_user_resource_percent": self.user_resource_percent,
                    "origin_entropy_limit": self.origin_entropy_limit,
                },
            },
        )

    def update_user_resource_percent(self, percent: int) -> "visionpy.vision.TransactionBuilder":
        """Create a Transaction to update user resource percent."""
        if self.origin_address != self.owner_address:
            raise RuntimeError("origin address and owner address mismatch")

        return self._client.vs._build_transaction(
            "UpdateSettingContract",
            {
                "owner_address": keys.to_hex_address(self.owner_address),
                "contract_address": keys.to_hex_address(self.contract_address),
                "consume_user_resource_percent": percent,
            },
        )

    def update_origin_entropy_limit(self, limit: int) -> "visionpy.vision.TransactionBuilder":
        """Create a Transaction to update origin entropy limit."""
        if self.origin_address != self.owner_address:
            raise RuntimeError("origin address and owner address mismatch")

        return self._client.vs._build_transaction(
            "UpdateEntropyLimitContract",
            {
                "owner_address": keys.to_hex_address(self.owner_address),
                "contract_address": keys.to_hex_address(self.contract_address),
                "origin_entropy_limit": limit,
            },
        )

    def clear_abi(self) -> "visionpy.vision.TransactionBuilder":
        """Clear contract ABI."""
        if self.origin_address != self.owner_address:
            raise RuntimeError("origin address and owner address mismatch")

        return self._client.vs._build_transaction(
            "ClearAbiContract",
            {
                "owner_address": keys.to_hex_address(self.owner_address),
                "contract_address": keys.to_hex_address(self.contract_address),
            },
        )

    @property
    def functions(self) -> "ContractFunctions":
        """The :class:`~ContractFunctions` object, wraps all contract methods."""
        if self._functions is None:
            if self.abi:
                self._functions = ContractFunctions(self)
                return self._functions
            raise ValueError("can not call a contract without ABI")
        return self._functions

    @property
    def constructor(self) -> "ContractConstructor":
        """The constructor of the contract."""
        for method_abi in self.abi:
            if method_abi['type'] == 'Constructor':
                return ContractConstructor(method_abi, self)

        raise NameError("Contract has no constructor")

    @property
    def events(self) -> "ContractEvents":
        """The :class:`~ContractEvents` object, wraps all contract events."""
        if self._events is None:
            if self.abi:
                self._events = ContractEvents(self)
                return self._events
            raise ValueError("can not call a contract without ABI")
        return self._events


class ContractEvents(object):
    def __init__(self, contract):
        self._contract = contract

    def __getitem__(self, event_name: str):
        for _abi in self._contract.abi:
            if _abi["type"].lower() == "event" and _abi["name"] == event_name:
                return ContractEvent(_abi, self._contract, event_name)

        raise KeyError("contract has no event named '{}'".format(event_name))

    def __getattr__(self, event: str):
        """Get the actual contract event object."""
        try:
            return self[event]
        except KeyError:
            raise AttributeError("contract has no method named '{}'".format(event))

    def __dir__(self):
        return [event["name"] for event in self._contract.abi if event["type"].lower() == "event"]

    def __iter__(self):
        yield from [self[event] for event in dir(self)]


class ContractEvent(object):
    def __init__(self, abi: dict, contract: "Contract", event_name: str):
        self._abi = abi
        self._contract = contract
        self._event_name = event_name

    def process_receipt(self, txn_receipt: dict):
        return self.parse_logs(txn_receipt['log'])

    def parse_logs(self, logs: List[dict]):
        for log in logs:
            yield self.get_event_data(log)

    def get_event_data(self, log: dict):
        data_types, data_names, topic_types, topic_names = [], [], [], []
        for arg in self._abi['inputs']:
            if arg.get('indexed', False) is False:
                data_types.append(arg['type'])
                data_names.append(arg['name'])
            else:
                topic_types.append(arg['type'])
                topic_names.append(arg['name'])

        topics = log['topics'][1:]
        decoded_topic_data = [
            vs_abi.decode_single(topic_type, decode_hex(topic_data))
            for topic_type, topic_data
            in zip(topic_types, topics)
        ]

        data = decode_hex(log['data'])
        decoded_data = vs_abi.decode_abi(data_types, data)

        event_args = dict(itertools.chain(
            zip(topic_names, decoded_topic_data),
            zip(data_names, decoded_data),
        ))
        return {
            'args': event_args,
            'event': self._event_name,
            'address': log['address'],
        }


class ContractFunctions(object):
    def __init__(self, contract):
        self._contract = contract

    def __getitem__(self, method: str):
        for method_abi in self._contract.abi:
            if method_abi["type"].lower() == "function" and method_abi["name"] == method:
                return ContractMethod(method_abi, self._contract)

        raise KeyError("contract has no method named '{}'".format(method))

    def __getattr__(self, method: str):
        """Get the actual contract method object."""
        try:
            return self[method]
        except KeyError:
            raise AttributeError("contract has no method named '{}'".format(method))

    def __dir__(self):
        return [method["name"] for method in self._contract.abi if method["type"].lower() == "function"]

    def __iter__(self):
        yield from [self[method] for method in dir(self)]


class ContractConstructor(object):
    """The constructor method of a contract."""

    def __init__(self, abi: dict, contract: Contract):

        self._abi = abi
        self._contract = contract

        self.inputs = abi.get("inputs", [])
        self.outputs = abi.get("outputs", [])

    def __str__(self):
        types = ", ".join(arg["type"] + " " + arg.get("name", "") for arg in self.inputs)
        ret = "construct({})".format(types)
        return ret

    @property
    def input_type(self) -> str:
        return "(" + (",".join(arg["type"] for arg in self.inputs)) + ")"

    def encode_parameter(self, *args, **kwargs) -> str:
        """Encode constructor parameters according to ABI."""
        parameter = ""

        if args and kwargs:
            raise ValueError("do not mix positional arguments and keyword arguments")

        if len(self.inputs) == 0:
            if args or kwargs:
                raise TypeError("{} constructor requires {} arguments".format(self._contract.name, len(self.inputs)))
        elif args:
            if len(args) != len(self.inputs):
                raise TypeError("wrong number of arguments, require {} got {}".format(len(self.inputs), len(args)))
            parameter = vs_abi.encode_single(self.input_type, args).hex()
        elif kwargs:
            if len(kwargs) != len(self.inputs):
                raise TypeError("wrong number of arguments, require {} got {}".format(len(self.inputs), len(args)))
            args = []
            for arg in self.inputs:
                try:
                    args.append(kwargs[arg["name"]])
                except KeyError:
                    raise TypeError("missing argument '{}'".format(arg["name"]))
            parameter = vs_abi.encode_single(self.input_type, args).hex()

        return parameter


class ContractMethod(object):
    def __init__(self, abi: dict, contract: Contract):

        self._abi = abi
        self._contract = contract
        self._owner_address = contract.owner_address
        self._client = contract._client

        self.inputs = abi.get("inputs", [])
        self.outputs = abi.get("outputs", [])

        self.call_value = 0
        self.call_token_value = 0
        self.call_token_id = 0

    def __str__(self):
        return self.function_type

    def with_owner(self, addr: str) -> "ContractMethod":
        """Set the calling owner address.

        Can also be changed through :meth:`TransactionBuilder.with_owner() <visionpy.vision.TransactionBuilder.with_owner>`.
        """
        self._owner_address = addr
        return self

    def with_transfer(self, amount: int) -> "ContractMethod":
        """Call a contract function with VS transfer. ``amount`` in `VDT`."""
        self.call_value = amount
        return self

    def with_asset_transfer(self, amount: int, token_id: int) -> "ContractMethod":
        """Call a contract function with VRC10 token transfer."""
        self.call_token_value = amount
        self.call_token_id = token_id
        return self

    def call(self, *args, **kwargs) -> "visionpy.vision.TransactionBuilder":
        """Call the contract method."""
        return self.__call__(*args, **kwargs)

    def parse_output(self, raw: str) -> Any:
        """Parse contract result as result."""
        parsed_result = vs_abi.decode_single(self.output_type, bytes.fromhex(raw))
        if len(self.outputs) == 1:
            return parsed_result[0]
        if len(self.outputs) == 0:
            return None
        return parsed_result

    def __call__(self, *args, **kwargs) -> "visionpy.vision.TransactionBuilder":
        """Call the contract method."""
        parameter = self._prepare_parameter(*args, **kwargs)
        return self._trigger_contract(parameter)

    def _prepare_parameter(self, *args, **kwargs) -> "visionpy.vision.TransactionBuilder":
        """Prepare parameter."""
        parameter = ""

        if args and kwargs:
            raise ValueError("do not mix positional arguments and keyword arguments")

        if len(self.inputs) == 0:
            if args or kwargs:
                raise TypeError("{} expected {} arguments".format(self.name, len(self.inputs)))
        elif args:
            if len(args) != len(self.inputs):
                raise TypeError("wrong number of arguments, require {} got {}".format(len(self.inputs), len(args)))
            parameter = vs_abi.encode_single(self.input_type, args).hex()
        elif kwargs:
            if len(kwargs) != len(self.inputs):
                raise TypeError("wrong number of arguments, require {} got {}".format(len(self.inputs), len(args)))
            args = []
            for arg in self.inputs:
                try:
                    args.append(kwargs[arg["name"]])
                except KeyError:
                    raise TypeError("missing argument '{}'".format(arg["name"]))
            parameter = vs_abi.encode_single(self.input_type, args).hex()
        else:
            raise TypeError("wrong number of arguments, require {}".format(len(self.inputs)))
        return parameter

    def _trigger_contract(self, parameter):
        if self._abi.get("stateMutability", None).lower() in ["view", "pure"]:
            # const call, contract ret
            ret = self._client.trigger_const_smart_contract_function(
                self._owner_address, self._contract.contract_address, self.function_signature, parameter,
            )

            return self.parse_output(ret)

        else:
            return self._client.vs._build_transaction(
                "TriggerSmartContract",
                {
                    "owner_address": keys.to_hex_address(self._owner_address),
                    "contract_address": keys.to_hex_address(self._contract.contract_address),
                    "data": self.function_signature_hash + parameter,
                    "call_token_value": self.call_token_value,
                    "call_value": self.call_value,
                    "token_id": self.call_token_id,
                },
                method=self,
            )

    @property
    def name(self) -> str:
        return self._abi["name"]

    @property
    def input_type(self) -> str:
        return "(" + (",".join(self.__format_json_abi_type_entry(arg) for arg in self.inputs)) + ")"

    @property
    def output_type(self) -> str:
        return "({})".format(",".join(self.__format_json_abi_type_entry(arg) for arg in self.outputs))

    def __format_json_abi_type_entry(self, entry) -> str:
        if entry['type'].startswith('tuple'):
            surfix = entry['type'][5:]
            if 'components' not in entry:
                raise ValueError("ABIEncoderV2 used, ABI should be set by hand")
            return "({}){}".format(
                ",".join(self.__format_json_abi_type_entry(arg) for arg in entry['components']), surfix
            )
        else:
            return entry['type']

    @property
    def function_signature(self) -> str:
        return self.name + self.input_type

    @property
    def function_signature_hash(self) -> str:
        return keccak256(self.function_signature.encode())[:4].hex()

    @property
    def function_type(self) -> str:
        types = ", ".join(arg["type"] + " " + arg.get("name", "") for arg in self.inputs)
        ret = "function {}({})".format(self.name, types)
        if self._abi.get("stateMutability", None).lower() == "view":
            ret += " view"
        elif self._abi.get("stateMutability", None).lower() == "pure":
            ret += " pure"
        if self.outputs:
            ret += " returns ({})".format(", ".join(arg["type"] + " " + arg.get("name", "") for arg in self.outputs))
        return ret


if __name__ == '__main__':
    from visionpy import Vision
    vp = Vision(network='vpioneer')
    txi = vp.get_transaction_info('31e2cac2866d976c4c532542624ac55f8141f6c516407393d0c94caaca9c2c94')
    cnr = vp.get_contract('VE2sE7iXbSyESQKMPLav5Q84EXEHZCnaRX')
    logs = list(cnr.events.Transfer.parse_logs(txi['log']))
    print(logs)