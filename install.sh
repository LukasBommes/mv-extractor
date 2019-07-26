#!/bin/bash

BASE="$PWD/.."

# Install build tools
apt-get update && \
apt-get upgrade -y && \
apt-get install -y \
    wget \
    unzip \
    build-essential \
    cmake \
    git \
    pkg-config \
    git-core \
    python3-dev \
    python3-pip \
    python3-numpy \
    python-pkgconfig && \
    rm -rf /var/lib/apt/lists/*

# Install opencv dependencies
apt-get update && \
apt-get install -y \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran && \
    rm -rf /var/lib/apt/lists/*


# Download OpenCV and build from source
cd "${BASE}"
wget -O "${BASE}"/opencv.zip https://github.com/opencv/opencv/archive/4.1.0.zip
unzip "${BASE}"/opencv.zip
mv "${BASE}"/opencv-4.1.0/ "${BASE}"/opencv/
rm -rf "${BASE}"/opencv.zip
wget -O "${BASE}"/opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.1.0.zip
unzip "${BASE}"/opencv_contrib.zip
mv "${BASE}"/opencv_contrib-4.1.0/ "${BASE}"/opencv_contrib/
rm -rf "${BASE}"/opencv_contrib.zip

# cd "${BASE}"/opencv
# mkdir build
# cd build
# cmake -D CMAKE_BUILD_TYPE=RELEASE \
#       -D OPENCV_GENERATE_PKGCONFIG=YES \
#       -D CMAKE_INSTALL_PREFIX=/usr/local \
#       -D OPENCV_ENABLE_NONFREE=ON \
#       -D OPENCV_EXTRA_MODULES_PATH="${BASE}"/opencv_contrib/modules ..
#
# cd "${BASE}"/opencv/build
# make -j $(nproc)
# make install
# ldconfig
#
#
# # Install FFMPEG dependencies
# apt-get update && \
# apt-get -y install \
#     libass-dev \
#     libfreetype6-dev \
#     libsdl2-dev \
#     libtool \
#     libva-dev \
#     libvdpau-dev \
#     libvorbis-dev \
#     libxcb1-dev \
#     libxcb-shm0-dev \
#     libxcb-xfixes0-dev \
#     texinfo \
#     zlib1g-dev \
#     nasm \
#     yasm \
#     libx264-dev \
#     libx265-dev \
#     libnuma-dev \
#     libvpx-dev \
#     libfdk-aac-dev \
#     libmp3lame-dev \
#     libopus-dev
#
#
# # Download FFMPEG source
# FFMPEG_VERSION="4.1.3"
# PATH="$BASE/bin:${PATH}"
# PKG_CONFIG_PATH='"${BASE}"/ffmpeg_build/lib/pkgconfig'
#
# mkdir -p "${BASE}"/ffmpeg_sources/ffmpeg "${BASE}"/bin
# cd "${BASE}"/ffmpeg_sources
# wget -O ffmpeg-snapshot.tar.bz2 https://ffmpeg.org/releases/ffmpeg-"${FFMPEG_VERSION}".tar.bz2
# tar xjvf ffmpeg-snapshot.tar.bz2 -C "${BASE}"/ffmpeg_sources/ffmpeg --strip-components=1
# rm -rf "${BASE}"/ffmpeg_sources/ffmpeg-snapshot.tar.bz2
# cd "${BASE}"/ffmpeg_sources/ffmpeg
#
#
# # Install patch for FFMPEG which exposes timestamp in AVPacket
# export FFMPEG_INSTALL_DIR='"${BASE}"/ffmpeg_sources/ffmpeg'
# export FFMPEG_PATCH_DIR='"${BASE}"/ffmpeg_patch'
#
# #COPY ffmpeg_patch/ "${FFMPEG_PATCH_DIR}"/
# chmod +x "${FFMPEG_PATCH_DIR}"/patch.sh
# "${FFMPEG_PATCH_DIR}"/patch.sh
#
#
# # Compile FFMPEG
# cd "${BASE}"/ffmpeg_sources/ffmpeg && \
# ./configure \
# --prefix="${BASE}/ffmpeg_build" \
# --pkg-config-flags="--static" \
# --extra-cflags='-I"${BASE}"/ffmpeg_build/include' \
# --extra-ldflags='-L$"{BASE}"/ffmpeg_build/lib' \
# --extra-libs="-lpthread -lm" \
# --bindir='"${BASE}"/bin' \
# --enable-gpl \
# --enable-libass \
# --enable-libfdk-aac \
# --enable-libfreetype \
# --enable-libmp3lame \
# --enable-libopus \
# --enable-libvorbis \
# --enable-libvpx \
# --enable-libx264 \
# --enable-libx265 \
# --enable-nonfree \
# --enable-pic && \
# make -j $(nproc) && \
# make install && \
# hash -r
#
# # Build python package
# python3 setup.py install
