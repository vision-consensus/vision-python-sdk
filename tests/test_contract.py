import pytest

from visionpy import Vision, Contract
from visionpy import AsyncVision, AsyncContract
from visionpy.keys import PrivateKey

# vpioneer addr and key
PRIVATE_KEY = PrivateKey(bytes.fromhex("a318cb4f1f3b87d604163e4a854312555d57158d78aef26797482d3038c4018b"))
FROM_ADDR = 'VSfD1o6FPChqdqLgwJaztjckyyo2GSM1KP'
TO_ADDR = 'VTCYvEK2ZuWvZ5LXqrLpU2GoRkFeJ1NrD2'      # private_key: eed06aebdef88683ff5678b353d1281bb2b730113c9283f7ea96600a0d2c104f
VRC20_CONTRACT_ADDR = 'VE2sE7iXbSyESQKMPLav5Q84EXEHZCnaRX'


def test_const_functions():
    client = Vision(network='vpioneer')

    contract = client.get_contract(VRC20_CONTRACT_ADDR)
    assert contract

    assert 'name' in dir(contract.functions)

    print(dir(contract.functions))
    print(repr(contract.functions.name()))
    print(repr(contract.functions.decimals()))

    assert contract.functions.totalSupply() > 0

    for f in contract.functions:
        print(f)


@pytest.mark.asyncio
async def test_async_const_functions():
    async with AsyncVision(network='vpioneer') as client:
        contract = await client.get_contract(VRC20_CONTRACT_ADDR)
        assert contract

        assert 'name' in dir(contract.functions)

        print(dir(contract.functions))
        print(repr(await contract.functions.name()))
        print(repr(await contract.functions.decimals()))

        assert await contract.functions.totalSupply() > 0

        for f in contract.functions:
            print(f)


def test_vrc20_transfer():
    # VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F
    client = Vision(network='vpioneer')

    contract = client.get_contract(VRC20_CONTRACT_ADDR)
    print('Balance', contract.functions.balanceOf(FROM_ADDR))
    txn = (
        contract.functions.transfer(TO_ADDR, 1_000)
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


@pytest.mark.asyncio
async def test_async_vrc20_transfer():
    async with AsyncVision(network='vpioneer') as client:
        contract = await client.get_contract(VRC20_CONTRACT_ADDR)
        print('Balance', await contract.functions.balanceOf(FROM_ADDR))
        txb = await contract.functions.transfer(TO_ADDR, 1_000)
        txb = txb.with_owner(FROM_ADDR).fee_limit(5_000_000)
        txn = await txb.build()
        txn = txn.sign(PRIVATE_KEY).inspect()
        txn_ret = await txn.broadcast()

        print(txn)
        # wait
        receipt = await txn_ret.wait()
        print(receipt)
        if 'contractResult' in receipt:
            print('result:', contract.functions.transfer.parse_output(receipt['contractResult'][0]))

        # result
        print(await txn_ret.result())


def test_contract_create():
    # VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F
    client = Vision(network='vpioneer')

    bytecode = "608060405234801561001057600080fd5b5060c78061001f6000396000f3fe6080604052348015600f57600080fd5b506004361060325760003560e01c806360fe47b11460375780636d4ce63c146062575b600080fd5b606060048036036020811015604b57600080fd5b8101908080359060200190929190505050607e565b005b60686088565b6040518082815260200191505060405180910390f35b8060008190555050565b6000805490509056fea2646970667358221220c8daade51f673e96205b4a991ab6b94af82edea0f4b57be087ab123f03fc40f264736f6c63430006000033"
    abi = [
        {
            "inputs": [],
            "name": "get",
            "outputs": [{"internalType": "uint256", "name": "retVal", "type": "uint256"}],
            "stateMutability": "view",
            "type": "function",
        }
    ]

    cntr = Contract(name="SimpleStore", bytecode=bytecode, abi=abi)

    txn = (
        client.vs.deploy_contract(FROM_ADDR, cntr)
        .fee_limit(5_000_000)
        .build()
        .sign(PRIVATE_KEY)
        .inspect()
        .broadcast()
    )
    print(txn)
    result = txn.wait()
    print(result)
    print('Created:', result['contract_address'])


@pytest.mark.asyncio
async def test_async_contract_create():
    # TGQgfK497YXmjdgvun9Bg5Zu3xE15v17cu
    async with AsyncVision(network='vpioneer') as client:
        bytecode = "608060405234801561001057600080fd5b5060c78061001f6000396000f3fe6080604052348015600f57600080fd5b506004361060325760003560e01c806360fe47b11460375780636d4ce63c146062575b600080fd5b606060048036036020811015604b57600080fd5b8101908080359060200190929190505050607e565b005b60686088565b6040518082815260200191505060405180910390f35b8060008190555050565b6000805490509056fea2646970667358221220c8daade51f673e96205b4a991ab6b94af82edea0f4b57be087ab123f03fc40f264736f6c63430006000033"
        abi = [
            {
                "inputs": [],
                "name": "get",
                "outputs": [{"internalType": "uint256", "name": "retVal", "type": "uint256"}],
                "stateMutability": "view",
                "type": "function",
            }
        ]

        cntr = AsyncContract(name="SimpleStore", bytecode=bytecode, abi=abi)

        txb = client.vs.deploy_contract(FROM_ADDR, cntr).fee_limit(1_000_000)
        txn = await txb.build()
        txn = txn.sign(PRIVATE_KEY).inspect()
        txn_ret = await txn.broadcast()

        print(txn_ret)
        result = await txn_ret.wait()
        print(f"Created: {result['contract_address']}")
        assert result['receipt']['result'] == 'SUCCESS'


def test_contract_decode_function_input():
    client = Vision(network='vpioneer')
    txn = client.get_transaction('61df64ad3b50583a8ed139ba4f3e44cbfc38156b4ce06e35b7fadb9466289122')
    cnr = client.get_contract(txn['raw_data']['contract'][0]['parameter']['value']['contract_address'])
    decoded_data = cnr.decode_function_input(txn['raw_data']['contract'][0]['parameter']['value']['data'])
    assert decoded_data == {
        'amountOutMin': 88396066,
        'path': ('VQokda3GiAfACiiPrHJed2dk1uRTgFVjYS', 'VVNLcKQBgywFWDCVAB6Hh5JMtSJk3NAy2c'),
        'to': 'VK6zWsRuXfS682qSaHjqGkFM178XLWdSiT',
        'deadline': 1647252114
    }

