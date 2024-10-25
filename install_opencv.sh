#!/bin/bash

INSTALL_BASE_DIR="$PWD/.."
INSTALL_DIR="$PWD"

echo "Installing OpenCV into: $INSTALL_DIR"

# Install opencv dependencies
echo "Installing OpenCV dependencies"
yum update -y && \
yum install -y \
    gtk3-devel \
    libjpeg-turbo-devel \
    libpng-devel \
    libtiff-devel \
    libv4l-devel \
    gcc-gfortran \
    openexr-devel \
    tbb-devel \
    gtk2-devel && \
    yum clean all

# Download OpenCV and build from source
OPENCV_VERSION="4.5.5"
echo "Downloading OpenCV source"
cd "$INSTALL_BASE_DIR"
wget -O "$INSTALL_BASE_DIR"/opencv.zip https://github.com/opencv/opencv/archive/"$OPENCV_VERSION".zip
unzip "$INSTALL_BASE_DIR"/opencv.zip
mv "$INSTALL_BASE_DIR"/opencv-"$OPENCV_VERSION"/ "$INSTALL_BASE_DIR"/opencv/
rm -rf "$INSTALL_BASE_DIR"/opencv.zip

echo "Configuring OpenCV"
cd "$INSTALL_BASE_DIR"/opencv
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
      -D OPENCV_GENERATE_PKGCONFIG=YES \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D OPENCV_ENABLE_NONFREE=OFF \
      -D BUILD_LIST=core,imgproc ..
echo "Compiling OpenCV"
make -j $(nproc)
make install
ldconfig
