import time

from visionpy import Vision, AsyncVision, VS
from visionpy.keys import PrivateKey
from visionpy.vision import Transaction
from visionpy.async_vision import AsyncTransaction
import pytest

# vpioneer addr and key
PRIVATE_KEY = PrivateKey(bytes.fromhex("a318cb4f1f3b87d604163e4a854312555d57158d78aef26797482d3038c4018b"))
FROM_ADDR = 'VSfD1o6FPChqdqLgwJaztjckyyo2GSM1KP'
TO_ADDR = 'VTCYvEK2ZuWvZ5LXqrLpU2GoRkFeJ1NrD2'      # private_key: eed06aebdef88683ff5678b353d1281bb2b730113c9283f7ea96600a0d2c104f
VRC20_CONTRACT_ADDR = 'VE2sE7iXbSyESQKMPLav5Q84EXEHZCnaRX'


def test_client_keygen():
    client = Vision()
    print(client.generate_address())
    print(client.get_address_from_passphrase('A'))


@pytest.mark.asyncio
def test_async_client_keygen():
    client = AsyncVision()
    print(client.generate_address())
    print(client.get_address_from_passphrase('A'))


def test_client():
    client = Vision(network='vpioneer')

    print(client)

    txn = (
        client.vs.transfer(FROM_ADDR, TO_ADDR, 1_000)
        .memo("test memo")
        .fee_limit(100_000_000)
        .build()
        .inspect()
        .sign(PRIVATE_KEY)
        .broadcast()
    )

    print(txn)


def test_client_sign_offline():
    client = Vision(network='vpioneer')
    tx = client.vs.transfer(FROM_ADDR, TO_ADDR, 1).memo("test memo").fee_limit(100_000_000).build()
    tx_j = tx.to_json()
    # offline
    tx_offline = Transaction.from_json(tx_j)    # tx_offline._client is None so it's offline
    tx_offline.sign(PRIVATE_KEY)
    tx_j2 = tx_offline.to_json()
    # online
    tx_2 = Transaction.from_json(tx_j2, client=client)
    tx_2.broadcast()


@pytest.mark.asyncio
async def test_async_client_sign_offline():
    async with AsyncVision(network='vpioneer') as client:
        tx = await client.vs.transfer(FROM_ADDR, TO_ADDR, 1).memo("test memo").fee_limit(100_000_000).build()
        tx_j = tx.to_json()
        # offline
        tx_offline = await AsyncTransaction.from_json(tx_j)    # tx_offline._client is None so it's offline
        tx_offline.sign(PRIVATE_KEY)
        tx_j2 = tx_offline.to_json()
        # online
        tx_2 = await AsyncTransaction.from_json(tx_j2, client=client)
        await tx_2.broadcast()


def test_client_update_tx():
    client = Vision(network='vpioneer')
    tx: Transaction = client.vs.transfer(FROM_ADDR, TO_ADDR, 1).memo("test memo").fee_limit(100_000_000).build()
    tx.sign(PRIVATE_KEY)
    tx.broadcast()
    tx_id = tx.txid
    # update and transfer again
    time.sleep(0.01)
    tx.update()
    assert tx_id != tx.txid
    assert tx._signature == []
    tx.sign(PRIVATE_KEY)
    tx.broadcast()


@pytest.mark.asyncio
async def test_async_client():
    async with AsyncVision(network='vpioneer') as client:
        print(client)

        txb = (
            client.vs.transfer(FROM_ADDR, TO_ADDR, int(VS*0.1))
            .memo("test memo")
            .fee_limit(100_000_000)
        )
        txn = await txb.build()
        txn.inspect()
        txn_ret = await txn.sign(PRIVATE_KEY).broadcast()

        print(txn_ret)
        print(await txn_ret.wait())


@pytest.mark.asyncio
async def test_async_manual_client():
    from httpx import AsyncClient, Timeout, Limits
    from visionpy.providers.async_http import AsyncHTTPProvider
    from visionpy.defaults import CONF_VIPONEER

    _http_client = AsyncClient(
        limits=Limits(max_connections=100, max_keepalive_connections=20), timeout=Timeout(timeout=10, connect=5, read=5)
    )
    provider = AsyncHTTPProvider(CONF_VIPONEER, client=_http_client)
    client = AsyncVision(provider=provider)

    txb = (
        client.vs.transfer(FROM_ADDR, TO_ADDR, 1_000)
        .memo("test memo")
        .fee_limit(1_000_000)
    )
    txn = await txb.build()
    txn_ret = await txn.sign(PRIVATE_KEY).broadcast()

    print(txn_ret)
    print(await txn_ret.wait())

    # must call .close at end to release connections
    await client.close()


def test_client_get_contract():
    client = Vision(network='vpioneer')
    """
    txn = (
        client.vs.asset_issue(
            "TGxv9UXRNMh4E6b33iuH1pqJfBffz6hXnV", "BTCC", 1_0000_0000_000000, url="https://www.example.com"
        )
        .memo("test issue BTCC coin")
        .fee_limit(0)
        .build()
        .inspect()
        .sign(priv_key)
        # .broadcast()
    )

    print(txn)
    """

    # print(client.get_account_permission("TGxv9UXRNMh4E6b33iuH1pqJfBffz6hXnV"))

    # very old address, of mainnet
    # print(client.get_account_resource("TTjacDH5PL8hpWirqU7HQQNZDyF723PuCg"))
    # "TGj1Ej1qRzL9feLTLhjwgxXF4Ct6GTWg2U"))

    cntr = client.get_contract(VRC20_CONTRACT_ADDR)
    print(cntr)

    print(cntr.abi)
    # print(client.get_contract("TTjacDH5PL8hpWirqU7HQQNZDyF723PuCg"))

    cntr.functions.name()


@pytest.mark.asyncio
async def test_async_client_get_contract():
    async with AsyncVision(network='vpioneer') as client:
        cntr = await client.get_contract(VRC20_CONTRACT_ADDR)
        print(cntr)

        print(cntr.abi)

        print(await cntr.functions.name())


def test_client_transfer_vrc10():
    client = Vision(network='vpioneer')

    txn = (
        client.vs.asset_transfer(
            FROM_ADDR, TO_ADDR, 1000, token_id=1000007
        )
        .memo("test transfer coin")
        .fee_limit(0)
        .build()
        .inspect()
        .sign(PRIVATE_KEY)
        .broadcast()
    )

    print(txn)


@pytest.mark.asyncio
async def test_client_transfer_vrc10():
    async with AsyncVision(network='vpioneer') as client:
        txb = (
            client.vs.asset_transfer(
                FROM_ADDR, TO_ADDR, 1000, token_id=1000007
            )
            .memo("test transfer coin")
            .fee_limit(0)
        )
        txn = await txb.build()
        txn.inspect()
        txn = txn.sign(PRIVATE_KEY)
        txn_ret = await txn.broadcast()
        print(txn_ret)


def test_client_timeout():
    from httpx import TimeoutException

    # must be a timeout
    client = Vision(network='vpioneer', conf={'timeout': 0.3})

    with pytest.raises(TimeoutException):
        client.get_block()

    client = Vision(network='vpioneer', conf={'timeout': 10})
    client.get_block()


@pytest.mark.asyncio
async def test_async_client_timeout():
    from httpx import TimeoutException

    # must be a timeout
    async with AsyncVision(network='vpioneer', conf={'timeout': 0.0001}) as client:
        with pytest.raises(TimeoutException):
            await client.get_block()

    async with AsyncVision(network='vpioneer', conf={'timeout': 10}) as client:
        await client.get_block()
