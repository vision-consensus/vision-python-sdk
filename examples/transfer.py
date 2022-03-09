from pprint import pprint

from visionpy import AsyncVision, Vision, VS
from visionpy.async_vision import AsyncTransaction
from visionpy.keys import PrivateKey
from visionpy.vision import Transaction
from visionpy.providers.async_http import AsyncHTTPProvider
from visionpy.defaults import CONF_VIPONEER
import httpx

PRIVATE_KEY = PrivateKey(bytes.fromhex("a318cb4f1f3b87d604163e4a854312555d57158d78aef26797482d3038c4018b"))
FROM_ADDR = 'VSfD1o6FPChqdqLgwJaztjckyyo2GSM1KP'
TO_ADDR = 'VTCYvEK2ZuWvZ5LXqrLpU2GoRkFeJ1NrD2'
# TO_ADDR private_key: eed06aebdef88683ff5678b353d1281bb2b730113c9283f7ea96600a0d2c104f
VRC20_CONTRACT_ADDR = 'VE2sE7iXbSyESQKMPLav5Q84EXEHZCnaRX'


def vs_transfer():
    client = Vision(network='vpioneer')
    txn = (
        client.vs.transfer(FROM_ADDR, TO_ADDR, 1_000)
        .memo("test memo")
        .fee_limit(100_000_000)
        .build()
        .inspect()
        .sign(PRIVATE_KEY)
        .broadcast()
    )
    pprint(txn)


async def async_vs_transfer():
    async with AsyncVision(network='vpioneer') as client:
        txb = (
            client.vs.transfer(FROM_ADDR, TO_ADDR, int(VS*0.1))
            .memo("test memo")
            .fee_limit(100_000_000)
        )
        txn = await txb.build()
        txn.inspect()
        txn_ret = await txn.sign(PRIVATE_KEY).broadcast()
        print(await txn_ret.wait())


async def async_vs_transfer_custom_httpx_client():
    """
    Manual control httpx client.
    """
    custom_http_client = httpx.AsyncClient(
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
        timeout=httpx.Timeout(timeout=10, connect=5, read=5)
    )
    provider = AsyncHTTPProvider(CONF_VIPONEER, client=custom_http_client)
    client = AsyncVision(provider=provider)

    txb = (
        client.vs.transfer(FROM_ADDR, TO_ADDR, 0.01 * VS)
        .memo("test memo")
        .fee_limit(1_000_000)
    )
    txn = await txb.build()
    txn_ret = await txn.sign(PRIVATE_KEY).broadcast()

    print(txn_ret)
    print(await txn_ret.wait())

    await client.close()    # must call `.close` at end to release connections.


def vs_transfer_sign_offline():
    """
    Microservice is more popular in modern server architecture and also have advantages in the financial field.
    It can isolate public services which connected to public network and internal services which manage keys.
    Visionpy can deliver txb in JSON format and restore back to txb to support this case.
    """
    client = Vision(network='vpioneer')
    tx = (         # build tx without signature
        client.vs.transfer(FROM_ADDR, TO_ADDR, 1)
        .memo("test memo")
        .fee_limit(100_000_000)
        .build()
    )
    tx_j = tx.to_json()
    # deliver JSON data to offline service.
    tx_offline = Transaction.from_json(tx_j)    # restore tx from JSON.
    tx_offline.sign(PRIVATE_KEY)    # sign
    tx_j2 = tx_offline.to_json()
    # deliver JSON data to online service.
    tx_2 = Transaction.from_json(tx_j2, client=client)  # restore tx from JSON.
    tx_2.broadcast()


async def async_vs_transfer_sign_offline():
    """
    Same as vs_transfer_sign_offline but using asyncio.
    """
    async with AsyncVision(network='vpioneer') as client:
        tx = await (
            client.vs.transfer(FROM_ADDR, TO_ADDR, 1)
            .memo("test memo")
            .fee_limit(100_000_000)
            .build()
        )
        tx_j = tx.to_json()
        tx_offline = await AsyncTransaction.from_json(tx_j)
        tx_offline.sign(PRIVATE_KEY)
        tx_j2 = tx_offline.to_json()
        tx_2 = await AsyncTransaction.from_json(tx_j2, client=client)
        await tx_2.broadcast()


def vrc20_transfer():
    client = Vision(network='vpioneer')
    contract = client.get_contract(VRC20_CONTRACT_ADDR)
    print('Balance:', contract.functions.balanceOf(FROM_ADDR) / contract.functions.decimals())
    txn = (
        contract.functions.transfer(TO_ADDR, 1)
        .with_owner(FROM_ADDR)
        .fee_limit(5_000_000)
        .build()
        .sign(PRIVATE_KEY)
        .inspect()
        .broadcast()
    )

    print(txn)
    # wait
    receipt = txn.wait()
    print(receipt)
    if 'contractResult' in receipt:
        print('result:', contract.functions.transfer.parse_output(receipt['contractResult'][0]))

    # result
    print(txn.result())


async def async_vrc20_transfer():
    async with AsyncVision(network='vpioneer') as client:
        contract = await client.get_contract(VRC20_CONTRACT_ADDR)
        print('Balance', await contract.functions.balanceOf(FROM_ADDR) / await contract.functions.decimals())
        txb = await contract.functions.transfer(TO_ADDR, 1_000)
        txb = txb.with_owner(FROM_ADDR).fee_limit(5_000_000)
        txn = await txb.build()
        txn = txn.sign(PRIVATE_KEY).inspect()
        txn_ret = await txn.broadcast()

        # wait
        receipt = await txn_ret.wait()
        print(receipt)
        if 'contractResult' in receipt:
            print('result:', contract.functions.transfer.parse_output(receipt['contractResult'][0]))

        # result
        print(await txn_ret.result())


def client_timeout():
    client = Vision(network='vpioneer', conf={'timeout': 0.001})  # too strict timeout setting
    try:
        client.get_block()
    except httpx.TimeoutException as e:
        pprint(f'Timeout: {e}')

    client = Vision(network='vpioneer', conf={'timeout': 10})   # normal
    client.get_block()  # not timeout


async def async_client_timeout():
    async with AsyncVision(network='vpioneer', conf={'timeout': 0.001}) as client:  # too strict timeout setting
        try:
            await client.get_block()
        except httpx.TimeoutException as e:
            pprint(f'Timeout: {e}')

    async with AsyncVision(network='vpioneer', conf={'timeout': 10}) as client:     # normal
        await client.get_block()

