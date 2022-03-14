#!/bin/bash

rm -r dist/
poetry build
tar -xvf dist/*.tar.gz --wildcards --no-anchored '*/setup.py' --strip=1
