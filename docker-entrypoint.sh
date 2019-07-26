#!/bin/sh
set -e

python3 setup.py install

exec "$@"
