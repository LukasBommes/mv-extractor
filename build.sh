#!/bin/bash

export CIBW_PLATFORM='linux'
#export CIBW_BUILD='cp${{ matrix.python }}-${{ matrix.platform_id }}'
export CIBW_BUILD='cp310-manylinux_x86_64'
export CIBW_SKIP='pp*'
export CIBW_ARCHS='x86_64'
#export CIBW_MANYLINUX_X86_64_IMAGE='${{ matrix.manylinux_image }}'
export CIBW_MANYLINUX_X86_64_IMAGE='lubo1994/mv-extractor:latest'
export CIBW_BUILD_FRONTEND='build'
export CIBW_TEST_COMMAND='VIDEO_URL={project}/vid.mp4 python3 {project}/tests/tests.py'
export CIBW_BUILD_VERBOSITY=1

pip install cibuildwheel==2.8.1
cibuildwheel --platform linux