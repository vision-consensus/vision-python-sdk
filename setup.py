# -*- coding: utf-8 -*-
from pathlib import Path

from setuptools import setup

packages = ['visionpy', 'visionpy.keys', 'visionpy.providers']

package_data = {'': ['*']}

install_requires = [
    'base58>=2.0.0,<3.0.0',
    'ecdsa>=0.15,<0.16',
    'eth_abi>=2.1.1,<3.0.0',
    'pycryptodome>=3.9.7,<4.0.0',
    'httpx==0.16.1',
]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open(Path('visionpy/version.py'), "r", encoding="utf-8") as fh:
    version = fh.read()
    VERSION = version[version.find('VERSION'):].strip().split('=')[-1].strip().replace('"', '')
    print(VERSION)

setup_kwargs = {
    'name': 'visionpy',
    'version': VERSION,
    'description': 'VISION Python client library',
    'long_description': long_description,
    'author': 'MioYvo',
    'author_email': 'liurusi.101@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/vision-consensus/vision-python-sdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
