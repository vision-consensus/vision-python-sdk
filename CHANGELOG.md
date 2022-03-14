# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## 0.04 (2022-03-14)
### Added
* `Contract.decode_function_input` inspired from [web3py](https://web3py.readthedocs.io/en/stable/contracts.html#utils)
* `generate_set_up_py.sh` auto generate `setup.py` from `pyproject.toml`

### changed
* `pyproject.toml`, loose the range version of httpx for more compatibility

## 0.03 (2022-03-11)
### Changed
* `pyproject.toml`, loose the range version of ecdsa for more compatibility

## 0.02 (2022-03-09)

### Added
* Add TransactionInfo event logs parser `ContractEvent.process_receipt` .
* More examples.

### Changed
* `README.md`
* Clear `async_contract.py`, `contract.py` and tests in `tests/`
