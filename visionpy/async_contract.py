import visionpy
from visionpy import keys
from visionpy.contract import Contract, ContractFunctions, ContractMethod


# noinspection PyProtectedMember
class AsyncContract(Contract):
    """A smart contract object."""

    @property
    def functions(self) -> "ContractFunctions":
        """The :class:`~ContractFunctions` object, wraps all contract methods."""
        if self._functions is None:
            if self.abi:
                self._functions = AsyncContractFunctions(self)
                return self._functions
            raise ValueError("can not call a contract without ABI")
        return self._functions


class AsyncContractFunctions(ContractFunctions):
    def __getitem__(self, method: str):
        for method_abi in self._contract.abi:
            if method_abi["type"].lower() == "function" and method_abi["name"] == method:
                return AsyncContractMethod(method_abi, self._contract)

        raise KeyError("contract has no method named '{}'".format(method))


# noinspection PyProtectedMember
class AsyncContractMethod(ContractMethod):
    async def call(self, *args, **kwargs) -> "visionpy.async_vision.AsyncTransactionBuilder":
        """Call the contract method."""
        return await self.__call__(*args, **kwargs)

    async def __call__(self, *args, **kwargs) -> "visionpy.async_vision.AsyncTransactionBuilder":
        """Call the contract method."""
        parameter = self._prepare_parameter(*args, **kwargs)
        return await self._async_trigger_contract(parameter)

    async def _async_trigger_contract(self, parameter):
        if self._abi.get("stateMutability", None).lower() in ["view", "pure"]:
            # const call, contract ret
            ret = await self._client.trigger_const_smart_contract_function(
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
