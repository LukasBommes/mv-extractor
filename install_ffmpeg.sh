#!/bin/bash

INSTALL_BASE_DIR="$PWD/.."
INSTALL_DIR="$PWD"

echo "Installing FFMPEG into: $INSTALL_DIR"

# Install FFMPEG dependencies
echo "Installing FFMPEG dependencies"
apt-get update -qq --fix-missing && \
apt-get upgrade -y && \
apt-get -y install \
    libass-dev \
    libfreetype6-dev \
    libsdl2-dev \
    libtool \
    libva-dev \
    libvdpau-dev \
    libvorbis-dev \
    libxcb1-dev \
    libxcb-shm0-dev \
    libxcb-xfixes0-dev \
    texinfo \
    zlib1g-dev \
    nasm \
    yasm \
    libx264-dev \
    libx265-dev \
    libnuma-dev \
    libvpx-dev \
    libfdk-aac-dev \
    libmp3lame-dev \
    libopus-dev


# Download FFMPEG source
FFMPEG_VERSION="4.1.3"
echo "Downloading FFMPEG source"
mkdir -p "$INSTALL_BASE_DIR"/ffmpeg_sources/ffmpeg "$INSTALL_BASE_DIR"/bin
cd "$INSTALL_BASE_DIR"/ffmpeg_sources
wget -O ffmpeg-snapshot.tar.bz2 https://ffmpeg.org/releases/ffmpeg-"$FFMPEG_VERSION".tar.bz2
tar xjvf ffmpeg-snapshot.tar.bz2 -C "$INSTALL_BASE_DIR"/ffmpeg_sources/ffmpeg --strip-components=1
rm -rf "$INSTALL_BASE_DIR"/ffmpeg_sources/ffmpeg-snapshot.tar.bz2
cd "$INSTALL_BASE_DIR"/ffmpeg_sources/ffmpeg


# Install patch for FFMPEG which exposes timestamp in AVPacket
echo "Patching FFMPEG"
export FFMPEG_INSTALL_DIR="$INSTALL_BASE_DIR/ffmpeg_sources/ffmpeg"
export FFMPEG_PATCH_DIR="$INSTALL_DIR/ffmpeg_patch"

chmod +x "$FFMPEG_PATCH_DIR"/patch.sh
"$FFMPEG_PATCH_DIR"/patch.sh


# Compile FFMPEG
echo "Configuring FFMPEG"
cd "$INSTALL_BASE_DIR"/ffmpeg_sources/ffmpeg && \
./configure \
--prefix="$INSTALL_BASE_DIR/ffmpeg_build" \
--pkg-config-flags="--static" \
--extra-cflags="-I$INSTALL_BASE_DIR/ffmpeg_build/include -static" \
--extra-ldflags="-L$INSTALL_BASE_DIR/ffmpeg_build/lib -static" \
--extra-libs="-lpthread -lm" \
--bindir="$INSTALL_BASE_DIR/bin" \
--enable-gpl \
--enable-libfreetype \
--enable-libmp3lame \
--enable-libopus \
--enable-libvorbis \
--enable-libvpx \
--enable-libx264 \
--enable-nonfree \
--enable-pic

echo "Compiling FFMPEG"
make -j $(nproc) && \
make install && \
hash -r