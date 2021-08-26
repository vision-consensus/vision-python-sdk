from visionpy.abi import vs_abi


def test_abi_encode():
    assert (
        vs_abi.encode_single("address", "VYKDHeQfG38C62Xo8tHLrGWiw5o9hL3QEK").hex()
        == '000000000000000000000000ed89ea86dcc4ab17e7b803de95571e259a935774'
    )

    assert vs_abi.encode_single("(address,uint256)", ["VYKDHeQfG38C62Xo8tHLrGWiw5o9hL3QEK", 100_000_000]).hex() == (
        '000000000000000000000000ed89ea86dcc4ab17e7b803de95571e259a935774'
        + '0000000000000000000000000000000000000000000000000000000005f5e100'
    )


def test_abi_decode():
    assert vs_abi.decode_abi(
        ['address', 'uint256'],
        bytes.fromhex(
            '000000000000000000000000ed89ea86dcc4ab17e7b803de95571e259a935774'
            + '0000000000000000000000000000000000000000000000000000000005f5e100'
        ),
    ) == ('VYKDHeQfG38C62Xo8tHLrGWiw5o9hL3QEK', 100000000)
