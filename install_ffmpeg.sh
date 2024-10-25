#!/bin/bash

INSTALL_BASE_DIR="$PWD/.."
INSTALL_DIR="$PWD"

echo "Installing FFMPEG into: $INSTALL_DIR"

mkdir -p "$INSTALL_BASE_DIR/bin"
mkdir -p "$INSTALL_BASE_DIR/ffmpeg_sources"
mkdir -p "$INSTALL_BASE_DIR/ffmpeg_build"
PATH="$PATH:$INSTALL_BASE_DIR/bin"

# Build and install NASM
echo "Building and installing NASM"
cd "$INSTALL_BASE_DIR/ffmpeg_sources"
curl -O -L https://www.nasm.us/pub/nasm/releasebuilds/2.15.05/nasm-2.15.05.tar.bz2
tar xjvf nasm-2.15.05.tar.bz2
cd nasm-2.15.05
./autogen.sh
./configure --prefix="$INSTALL_BASE_DIR/ffmpeg_build" --bindir="$INSTALL_BASE_DIR/bin"
make -j $(nproc)
make install

# Build and install Yasm
echo "Building and installing Yasm"
cd "$INSTALL_BASE_DIR/ffmpeg_sources"
curl -O -L https://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz
tar xzvf yasm-1.3.0.tar.gz
cd yasm-1.3.0
./configure --prefix="$INSTALL_BASE_DIR/ffmpeg_build" --bindir="$INSTALL_BASE_DIR/bin"
make -j $(nproc)
make install

# Build and install libx264
echo "Building and installing libx264"
cd "$INSTALL_BASE_DIR/ffmpeg_sources"
git clone --branch stable --depth 1 https://code.videolan.org/videolan/x264.git
cd x264
PKG_CONFIG_PATH="$INSTALL_BASE_DIR/ffmpeg_build/lib/pkgconfig" ./configure --prefix="$INSTALL_BASE_DIR/ffmpeg_build" --bindir="$INSTALL_BASE_DIR/bin" --enable-static --enable-pic
make -j $(nproc)
make install

# Download FFMPEG source
FFMPEG_VERSION="4.1.3"
echo "Downloading FFMPEG source"
mkdir -p "$INSTALL_BASE_DIR"/ffmpeg_sources/ffmpeg
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
cd "$INSTALL_BASE_DIR"/ffmpeg_sources/ffmpeg
PATH="$INSTALL_BASE_DIR/bin:$PATH" PKG_CONFIG_PATH="$INSTALL_BASE_DIR/ffmpeg_build/lib/pkgconfig" ./configure \
--prefix="$INSTALL_BASE_DIR/ffmpeg_build" \
--pkg-config-flags="--static" \
--extra-cflags="-I$INSTALL_BASE_DIR/ffmpeg_build/include" \
--extra-ldflags="-L$INSTALL_BASE_DIR/ffmpeg_build/lib" \
--extra-libs=-lpthread \
--extra-libs=-lm \
--bindir="$INSTALL_BASE_DIR/bin" \
--enable-gpl \
--enable-libfreetype \
--enable-libx264 \
--enable-nonfree \
--enable-pic

echo "Compiling FFMPEG"
make -j $(nproc)
make install
hash -r
