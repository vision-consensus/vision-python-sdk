from visionpy import Vision, AsyncVision
import pytest


def test_query_account():
    client = Vision(network='vtest')

    # There are many VRC10 token named `tt`
    with pytest.raises(Exception):
        btt = client.get_asset_from_name("tt")
        print(btt)

    bals = client.get_account_asset_balances("VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F")
    print(bals)
    assert len(bals) > 0

    bal = client.get_account_asset_balance("VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F", 1000007)
    print(bal)
    assert bal > 0


@pytest.mark.asyncio
async def test_async_query_account():
    async with AsyncVision(network='vtest') as client:
        # There are many VRC10 token named `tt`
        with pytest.raises(Exception):
            btt = await client.get_asset_from_name("tt")
            print(btt)

        bals = await client.get_account_asset_balances("VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F")
        print(bals)
        assert len(bals) > 0

        bal = await client.get_account_asset_balance("VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F", 1000007)
        print(bal)
        assert bal > 0
