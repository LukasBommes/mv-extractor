FROM quay.io/pypa/manylinux_2_28_x86_64 AS builder

# Install build tools
RUN yum update -y && \
  yum install -y \
    wget \
    unzip \
    git \
    make \
    cmake \
    gcc \
    gcc-c++ \
    pkgconfig \
    libtool && \
  yum clean all

# Install OpenCV
ARG OPENCV_VERSION="4.10.0"
WORKDIR /opt
RUN wget -O opencv.zip https://github.com/opencv/opencv/archive/"$OPENCV_VERSION".zip && \
  unzip opencv.zip && \
  mv opencv-"$OPENCV_VERSION" opencv && \
  mkdir opencv/build && \
  cd opencv/build && \
  cmake \
  -D CMAKE_BUILD_TYPE=RELEASE \
  -D OPENCV_GENERATE_PKGCONFIG=YES \
  -D CMAKE_INSTALL_PREFIX=/usr/local \
  -D OPENCV_ENABLE_NONFREE=OFF \
  -D BUILD_LIST=core,imgproc \
  .. && \
  make -j $(nproc) && \
  make install && \
  ldconfig && \
  rm -rf ../../opencv.zip && \
  rm -rf ../../opencv

# Install FFMPEG
WORKDIR /opt/ffmpeg_sources
RUN curl -O -L https://www.nasm.us/pub/nasm/releasebuilds/2.15.05/nasm-2.15.05.tar.bz2 && \
  tar xjvf nasm-2.15.05.tar.bz2 && \
  cd nasm-2.15.05 && \
  ./autogen.sh && \
  ./configure --disable-shared --enable-static && \
  make -j $(nproc) && \
  make install && \
  rm -rf ../nasm-2.15.05.tar.bz2 && \
  rm -rf ../nasm-2.15.05

WORKDIR /opt/ffmpeg_sources
RUN curl -O -L https://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz && \
  tar xzvf yasm-1.3.0.tar.gz && \
  cd yasm-1.3.0 && \
  ./configure --disable-shared --enable-static && \
  make -j $(nproc) && \
  make install && \
  rm -rf ../yasm-1.3.0.tar.gz && \
  rm -rf ../yasm-1.3.0

WORKDIR /opt/ffmpeg_sources
RUN git clone --branch stable --depth 1 https://code.videolan.org/videolan/x264.git && \
  cd x264 && \
  ./configure --disable-shared --enable-static --enable-pic && \
  make -j $(nproc) && \
  make install && \
  rm -rf ../x264

ARG FFMPEG_VERSION="4.1.3"
WORKDIR /opt/ffmpeg_sources
RUN wget -O ffmpeg-snapshot.tar.bz2 https://ffmpeg.org/releases/ffmpeg-"$FFMPEG_VERSION".tar.bz2 && \
  mkdir -p ffmpeg && \
  tar xjvf ffmpeg-snapshot.tar.bz2 -C ffmpeg --strip-components=1 && \
  rm -rf ffmpeg-snapshot.tar.bz2

COPY ./ffmpeg_patch /opt/ffmpeg_sources/ffmpeg_patch
ENV FFMPEG_INSTALL_DIR=/opt/ffmpeg_sources/ffmpeg
ENV FFMPEG_PATCH_DIR=/opt/ffmpeg_sources/ffmpeg_patch

WORKDIR /opt/ffmpeg_sources
RUN ffmpeg_patch/patch.sh && \
  cd ffmpeg && \
  ./configure \
  --pkg-config-flags="--static" \
  --extra-cflags="-I/usr/local/include" \
  --extra-ldflags="-L/usr/local/lib" \
  --extra-libs=-lpthread \
  --extra-libs=-lm \
  --enable-static \
  --disable-shared \
  --enable-gpl \
  --enable-libx264 \
  --enable-nonfree \
  --enable-pic && \
  make -j $(nproc) && \
  make install && \
  rm -rf ../ffmpeg

FROM quay.io/pypa/manylinux_2_28_x86_64

# copy libraries
WORKDIR /usr/local/lib
COPY --from=builder /usr/local/lib .
WORKDIR /usr/local/lib64
COPY --from=builder /usr/local/lib64 .
WORKDIR /usr/local/include
COPY --from=builder /usr/local/include .
WORKDIR /usr/local/lib
COPY --from=builder /usr/local/lib .

# Set environment variables
ENV PKG_CONFIG_PATH="$PKG_CONFIG_PATH:/usr/local/lib64/pkgconfig"
ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/lib64"

WORKDIR /home/video_cap

COPY pyproject.toml /home/video_cap/
COPY setup.py /home/video_cap/
COPY src /home/video_cap/src/
COPY README.md /home/video_cap/

# Install Python package
RUN python3.12 -m pip install .

# Location of the "extract_mvs" script
ENV PATH="$PATH:/opt/_internal/cpython-3.12.7/bin"

CMD ["sh", "-c", "tail -f /dev/null"]
