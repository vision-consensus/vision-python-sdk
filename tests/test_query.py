from visionpy import Vision, AsyncVision, Contract
import pytest


ADDR = "VSfD1o6FPChqdqLgwJaztjckyyo2GSM1KP"


def test_query_account():
    client = Vision(network='vpioneer')

    # There are many VRC10 token named `tt`
    with pytest.raises(Exception):
        btt = client.get_asset_from_name("VW49EUhDa6G2LqSDpzvprCAGPJjU7FwAWK")  # never match
        print(btt)
    # BNBVRC10(BVC) : VW49EUhDa6G2LqSDpzvprCAGPJjU7FwAWK
    bals = client.get_account_asset_balances('VW49EUhDa6G2LqSDpzvprCAGPJjU7FwAWK')
    print(bals)
    assert len(bals) > 0
    # BNBVRC10(BVC) : VW49EUhDa6G2LqSDpzvprCAGPJjU7FwAWK
    bal = client.get_account_asset_balance('VW49EUhDa6G2LqSDpzvprCAGPJjU7FwAWK', 1000001)
    print(bal)
    assert bal > 0


@pytest.mark.asyncio
async def test_async_query_account():
    async with AsyncVision(network='vpioneer') as client:
        # There are many VRC10 token named `tt`
        with pytest.raises(Exception):
            btt = await client.get_asset_from_name("tttttttttttt")
            print(btt)

        bals = await client.get_account_asset_balances(ADDR)
        print(bals)
        assert len(bals) > 0

        bal = await client.get_account_asset_balance(ADDR, 1000007)
        print(bal)
        assert bal > 0


@pytest.mark.asyncio
async def test_async_query_hash():
    async with AsyncVision(network='vpioneer') as client:
        # There are many VRC10 token named `tt`
        with pytest.raises(Exception):
            btt = await client.get_transaction("tttttttttttt")
            print(btt)

        txn = await client.get_transaction('31e2cac2866d976c4c532542624ac55f8141f6c516407393d0c94caaca9c2c94')
        print(txn)
        assert txn['ret'] == [{'contractRet': 'SUCCESS'}]
        assert txn['txID'] == '31e2cac2866d976c4c532542624ac55f8141f6c516407393d0c94caaca9c2c94'

        txi = await client.get_transaction_info('31e2cac2866d976c4c532542624ac55f8141f6c516407393d0c94caaca9c2c94')
        assert txi['id'] == '31e2cac2866d976c4c532542624ac55f8141f6c516407393d0c94caaca9c2c94'
        assert txi['blockNumber'] == 3897439
        assert txi['receipt']['result'] == 'SUCCESS'

        # USDT Contract address: VE2sE7iXbSyESQKMPLav5Q84EXEHZCnaRX
        cnr: Contract = await client.get_contract('VE2sE7iXbSyESQKMPLav5Q84EXEHZCnaRX')
        events = list(cnr.events.Transfer.process_receipt(txi))
        assert events
        assert events[0]['event'] == 'Transfer'
        assert events[0]['address'] == 'VE2sE7iXbSyESQKMPLav5Q84EXEHZCnaRX'
        assert events[0]['args'] == {
            'src': 'VZYRFirUP5fDRNpUpCRAjPfFjappSQvsCQ',
            'dst': 'VSfD1o6FPChqdqLgwJaztjckyyo2GSM1KP',
            'wad': 20000000000000
        }
