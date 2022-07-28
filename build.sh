#!/bin/bash

./run.sh python3.10 -m build && \
  auditwheel repair dist/mv_extractor-0.0.0-cp310-cp310-linux_x86_64.whl

#TODO: run for other python versions 
#TODO: upload to PyPI via twine

