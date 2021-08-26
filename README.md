# vision-python-sdk (visionpy)

[![PyPI version](https://badge.fury.io/py/visionpy.svg)](https://pypi.org/project/visionpy/)

Vision Python Client Library.

## How to use

```python
from visionpy import Vision
from visionpy.keys import PrivateKey

client = Vision(network='vtest')
# Private key of VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F
priv_key = PrivateKey(bytes.fromhex("a39ad1e46936f730c411184134365188cfb4497d17352a582e316edfcf9e4710"))

txn = (
    client.vs.transfer("VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F", "VZDLsQX25r6og58gfRcxSANYfLRmDV3gE3", 1_000)
    .memo("test memo")
    .build()
    .inspect()
    .sign(priv_key)
    .broadcast()
)

print(txn)
print(txn.wait())
```

### Async Client

```python
import asyncio

from visionpy import AsyncVision
from visionpy.keys import PrivateKey

# private key of VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F
priv_key = PrivateKey(bytes.fromhex("a39ad1e46936f730c411184134365188cfb4497d17352a582e316edfcf9e4710"))

async def transfer():
    async with AsyncVision(network='vtest') as client:
        print(client)

        txb = (
            client.trx.transfer("VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F", "VZDLsQX25r6og58gfRcxSANYfLRmDV3gE3", 1_000)
            .memo("test memo")
            .fee_limit(100_000_000)
        )
        txn = await txb.build()
        print(txn)
        txn_ret = await txn.sign(priv_key).broadcast()
        print(txn_ret)
        print(await txn_ret.wait())

if __name__ == '__main__':
    asyncio.run(transfer())
```

Or close async client manually:

```python
import asyncio

from httpx import AsyncClient, Timeout, Limits
from visionpy import AsyncVision
from visionpy.keys import PrivateKey
from visionpy.providers.async_http import AsyncHTTPProvider
from visionpy.defaults import CONF_VTEST


async def transfer():
    _http_client = AsyncClient(limits=Limits(max_connections=100, max_keepalive_connections=20),
                               timeout=Timeout(timeout=10, connect=5, read=5))
    provider = AsyncHTTPProvider(CONF_VTEST, client=_http_client)
    client = AsyncVision(provider=provider)
    print(client)

    priv_key = PrivateKey(bytes.fromhex("a39ad1e46936f730c411184134365188cfb4497d17352a582e316edfcf9e4710"))
    txb = (
        client.vs.transfer("VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F", "VZDLsQX25r6og58gfRcxSANYfLRmDV3gE3", 1_000)
        .memo("test memo")
        .fee_limit(100_000_000)
    )
    txn = await txb.build()
    print(txn)
    txn_ret = await txn.sign(priv_key).broadcast()

    print(txn_ret)
    print(await txn_ret.wait())
    await client.close()

if __name__ == '__main__':
    asyncio.run(transfer())
```
