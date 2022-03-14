from typing import Union, Any, List, cast, Dict

from eth_typing import HexStr
from eth_utils import function_abi_to_4byte_selector, encode_hex, to_bytes, hexstr_if_str, remove_0x_prefix, \
    add_0x_prefix
from eth_utils.abi import collapse_if_tuple


def pad_hex(value: Any, bit_size: int) -> HexStr:
    """
    Pads a hex string up to the given bit_size
    """
    value = remove_0x_prefix(value)
    return add_0x_prefix(value.zfill(int(bit_size / 4)))


def to_4byte_hex(hex_or_str_or_bytes: Union[HexStr, str, bytes, int]) -> HexStr:
    size_of_4bytes = 4 * 8
    byte_str = hexstr_if_str(to_bytes, hex_or_str_or_bytes)
    if len(byte_str) > 4:
        raise ValueError(
            'expected value of size 4 bytes. Got: %d bytes' % len(byte_str)
        )
    hex_str = encode_hex(byte_str)
    return pad_hex(hex_str, size_of_4bytes)


def get_function_by_selector(abi, selector: str):
    for fns in abi:
        if fns['type'] == 'Function':
            if encode_hex(function_abi_to_4byte_selector(fns)) == to_4byte_hex(selector):
                return fns


def get_abi_input_names(fns_abi):
    if 'inputs' not in fns_abi and fns_abi['type'] == 'fallback':
        return []
    else:
        return [arg['name'] for arg in fns_abi['inputs']]


def get_abi_input_types(fns_abi) -> List[str]:
    if 'inputs' not in fns_abi and (fns_abi['type'] == 'fallback' or fns_abi['type'] == 'receive'):
        return []
    else:
        return [collapse_if_tuple(cast(Dict[str, Any], arg)) for arg in fns_abi['inputs']]