# vision-python-sdk (visionpy)
[![PyPI version](https://badge.fury.io/py/visionpy.svg)](https://badge.fury.io/py/visionpy)

Vision Python Client Library.

## Features
1. Get Block, Transaction, TransactionInfo, Node;
2. Build and transfer VS, VRC10, VRC20;
3. Parse event logs of TransactionInfo;
4. Asyncio support;
5. Python 3.7.2 and late version required;
6. Poetry for package management.

## How to use
More examples please check `example` folder.
```python
from visionpy import Vision
from visionpy.keys import PrivateKey


# Private key of VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F
priv_key = PrivateKey(bytes.fromhex("eed06aebdef88683ff5678b353d1281bb2b730113c9283f7ea96600a0d2c104f"))
def transfer():
    client = Vision(network='vpioneer')
    txn_ret = (
        client.vs.transfer("VTCYvEK2ZuWvZ5LXqrLpU2GoRkFeJ1NrD2", "VSfD1o6FPChqdqLgwJaztjckyyo2GSM1KP", 1_000)
        .memo("test memo")
        .build()
        .inspect()
        .sign(priv_key)
        .broadcast()
    )
    print(txn_ret)
    print(txn_ret.result())
```

#### Async Client

```python
import asyncio

from visionpy import AsyncVision
from visionpy.keys import PrivateKey

# private key of VTCYvEK2ZuWvZ5LXqrLpU2GoRkFeJ1NrD2
priv_key = PrivateKey(bytes.fromhex("eed06aebdef88683ff5678b353d1281bb2b730113c9283f7ea96600a0d2c104f"))

async def transfer():
    async with AsyncVision(network='vpioneer') as client:
        print(client)

        txb = (
            client.trx.transfer("VTCYvEK2ZuWvZ5LXqrLpU2GoRkFeJ1NrD2", "VSfD1o6FPChqdqLgwJaztjckyyo2GSM1KP", 1_000)
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