#!/bin/bash

xhost +

docker run \
    -it \
    --ipc=host \
    --env="DISPLAY" \
    -v $(pwd):/home/video_cap \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    lubo1994/mv-extractor:latest \
    "$@"