#!/bin/bash

INSTALL_BASE_DIR="$PWD/.."
INSTALL_DIR="$PWD"

echo "Installing OpenCV into: $INSTALL_DIR"

# Install opencv dependencies
echo "Installing OpenCV dependencies"
apt-get update -qq --fix-missing && \
apt-get upgrade -y && \
apt-get install -y \
    libgtk-3-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libx265-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libatlas-base-dev \
    gfortran \
    openexr \
    libtbb2 \
    libtbb-dev \
    libdc1394-dev \
    libgtk2.0-dev && \
    rm -rf /var/lib/apt/lists/*


# Download OpenCV and build from source
echo "Downloading OpenCV source"
cd "$INSTALL_BASE_DIR"
wget -O "$INSTALL_BASE_DIR"/opencv.zip https://github.com/opencv/opencv/archive/4.1.0.zip
unzip "$INSTALL_BASE_DIR"/opencv.zip
mv "$INSTALL_BASE_DIR"/opencv-4.1.0/ "$INSTALL_BASE_DIR"/opencv/
rm -rf "$INSTALL_BASE_DIR"/opencv.zip
wget -O "$INSTALL_BASE_DIR"/opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.1.0.zip
unzip "$INSTALL_BASE_DIR"/opencv_contrib.zip
mv "$INSTALL_BASE_DIR"/opencv_contrib-4.1.0/ "$INSTALL_BASE_DIR"/opencv_contrib/
rm -rf "$INSTALL_BASE_DIR"/opencv_contrib.zip

echo "Configuring OpenCV"
cd "$INSTALL_BASE_DIR"/opencv
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
      -D OPENCV_GENERATE_PKGCONFIG=YES \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D OPENCV_ENABLE_NONFREE=ON \
      -D OPENCV_EXTRA_MODULES_PATH="$INSTALL_BASE_DIR"/opencv_contrib/modules ..
echo "Compiling OpenCV"
make -j $(nproc)
make install
ldconfig