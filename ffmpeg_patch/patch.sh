#!/bin/bash

# before running the script, set FFMPEG_PATCH_DIR and FFMPEG_INSTALL_DIR

if [[ -z "${FFMPEG_INSTALL_DIR}" ]] || [[ -z "${FFMPEG_PATCH_DIR}" ]]; then
    echo "Please set the environment variables FFMPEG_INSTALL_DIR and FFMPEG_PATCH_DIR to an appropiate value"
    exit 1
else
    yes | cp -rf "$FFMPEG_PATCH_DIR"/avcodec.h "$FFMPEG_INSTALL_DIR"/libavcodec/
    yes | cp -rf "$FFMPEG_PATCH_DIR"/rtpdec.c "$FFMPEG_INSTALL_DIR"/libavformat/
    yes | cp -rf "$FFMPEG_PATCH_DIR"/utils.c "$FFMPEG_INSTALL_DIR"/libavformat/
fi
