# -*- coding: utf-8 -*-
from setuptools import setup
"""
# to generate setup.py automatically
rm -r dist/
poetry build
tar -xvf dist/*.tar.gz --wildcards --no-anchored '*/setup.py' --strip=1
"""

packages = \
['visionpy', 'visionpy.keys', 'visionpy.providers']

package_data = \
{'': ['*']}

install_requires = \
['base58>=2.0.0,<3.0.0',
 'ecdsa>=0.15',
 'eth_abi>=2.1.1,<3.0.0',
 'httpx>=0.16.1',
 'pycryptodome>=3.9.7,<4.0.0']

setup_kwargs = {
    'name': 'visionpy',
    'version': '0.0.3',
    'description': 'Vision Python client library',
    'long_description': '# vision-python-sdk (visionpy)\n[![PyPI version](https://badge.fury.io/py/visionpy.svg)](https://badge.fury.io/py/visionpy)\n\nVision Python Client Library.\n\n## Features\n1. Get Block, Transaction, TransactionInfo, Node;\n2. Build and transfer VS, VRC10, VRC20;\n3. Parse event logs of TransactionInfo;\n4. Asyncio support;\n5. Python 3.7.2 and late version required;\n6. Poetry for package management.\n\n## How to use\nMore examples please check `example` folder.\n```python\nfrom visionpy import Vision\nfrom visionpy.keys import PrivateKey\n\n\n# Private key of VDGXn73Qgf6V1aGbm8eigoHyPJRJpALN9F\npriv_key = PrivateKey(bytes.fromhex("eed06aebdef88683ff5678b353d1281bb2b730113c9283f7ea96600a0d2c104f"))\ndef transfer():\n    client = Vision(network=\'vpioneer\')\n    txn_ret = (\n        client.vs.transfer("VTCYvEK2ZuWvZ5LXqrLpU2GoRkFeJ1NrD2", "VSfD1o6FPChqdqLgwJaztjckyyo2GSM1KP", 1_000)\n        .memo("test memo")\n        .build()\n        .inspect()\n        .sign(priv_key)\n        .broadcast()\n    )\n    print(txn_ret)\n    print(txn_ret.result())\n```\n\n#### Async Client\n\n```python\nimport asyncio\n\nfrom visionpy import AsyncVision\nfrom visionpy.keys import PrivateKey\n\n# private key of VTCYvEK2ZuWvZ5LXqrLpU2GoRkFeJ1NrD2\npriv_key = PrivateKey(bytes.fromhex("eed06aebdef88683ff5678b353d1281bb2b730113c9283f7ea96600a0d2c104f"))\n\nasync def transfer():\n    async with AsyncVision(network=\'vpioneer\') as client:\n        print(client)\n\n        txb = (\n            client.trx.transfer("VTCYvEK2ZuWvZ5LXqrLpU2GoRkFeJ1NrD2", "VSfD1o6FPChqdqLgwJaztjckyyo2GSM1KP", 1_000)\n            .memo("test memo")\n            .fee_limit(100_000_000)\n        )\n        txn = await txb.build()\n        print(txn)\n        txn_ret = await txn.sign(priv_key).broadcast()\n        print(txn_ret)\n        print(await txn_ret.wait())\n\nif __name__ == \'__main__\':\n    asyncio.run(transfer())\n```',
    'author': 'mio',
    'author_email': 'liurusi.101@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vision-consensus/vision-python-sdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>3.7.1,<4.0',
}


setup(**setup_kwargs)
