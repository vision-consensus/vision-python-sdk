from eth_abi import encoding, decoding
from eth_abi.registry import (
    ABIRegistry,
    BaseEquals,
    registry as default_registry,
)

from visionpy.keys import to_base58check_address


class AddressEncoder(encoding.AddressEncoder):
    encode_fn = staticmethod(to_base58check_address)


class AddressDecoder(decoding.AddressDecoder):
    decoder_fn = staticmethod(to_base58check_address)


def build_default_registry() -> ABIRegistry:
    # We make a copy here just to make sure that eth-abi's default registry is not
    # affected by our custom encoder subclasses
    registry = default_registry.copy()

    registry.unregister('address')

    registry.register(
        BaseEquals('address'),
        AddressEncoder, AddressDecoder,
        label='address',
    )

    return registry
