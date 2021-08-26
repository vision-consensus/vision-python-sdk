import pytest

from visionpy import Vision, Contract
from visionpy import AsyncVision, AsyncContract
from visionpy.keys import PrivateKey

# vtest addr and key
PRIVATE_KEY = PrivateKey(bytes.fromhex("a39ad1e46936f730c411184134365188cfb4497d17352a582e316edfcf9e4710"))
FROM_ADDR = 'VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F'
TO_ADDR = 'VZDLsQX25r6og58gfRcxSANYfLRmDV3gE3'
VRC20_CONTRACT_ADDR = 'VYKDHeQfG38C62Xo8tHLrGWiw5o9hL3QEK'


def test_const_functions():
    client = Vision(network='vtest')

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
    async with AsyncVision(network='vtest') as client:
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
    client = Vision(network='vtest')

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
    async with AsyncVision(network='vtest') as client:
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
    client = Vision(network='vtest')

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
    async with AsyncVision(network='vtest') as client:
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

        txb = client.vs.deploy_contract('VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F', cntr).fee_limit(1_000_000)
        txn = await txb.build()
        txn = txn.sign(PRIVATE_KEY).inspect()
        txn_ret = await txn.broadcast()

        print(txn_ret)
        result = await txn_ret.wait()
        print(result)
        print('Created:', result['contract_address'])
