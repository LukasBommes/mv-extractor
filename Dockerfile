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
  rm -rf opencv.zip
WORKDIR /opt/opencv/build
RUN cmake \
  -D CMAKE_BUILD_TYPE=RELEASE \
  -D OPENCV_GENERATE_PKGCONFIG=YES \
  -D CMAKE_INSTALL_PREFIX=/usr/local \
  -D OPENCV_ENABLE_NONFREE=OFF \
  -D BUILD_LIST=core,imgproc \
  ..
RUN make -j $(nproc) && \
  make install && \
  ldconfig

# # Install FFMPEG
# COPY install_ffmpeg.sh /home/video_cap
# COPY ffmpeg_patch /home/video_cap/ffmpeg_patch/
# RUN mkdir -p /home/video_cap && \
#   cd /home/video_cap && \
#   chmod +x install_ffmpeg.sh && \
#   ./install_ffmpeg.sh

# FROM quay.io/pypa/manylinux_2_28_x86_64

# RUN yum update -y && \
#   yum install -y \
#     pkgconfig \
#     gtk3-devel \
#     zlib-devel \
#     SDL2-devel \
#     libvpx-devel \
#     libvorbis-devel \
#     opus-devel \
#     xz-devel && \
#   yum clean all

# # copy libraries
# WORKDIR /usr/local/lib
# COPY --from=builder /usr/local/lib .
# WORKDIR /usr/local/lib64
# COPY --from=builder /usr/local/lib64 .
# WORKDIR /usr/local/include
# COPY --from=builder /home/ffmpeg_build/include .
# WORKDIR /home/ffmpeg_build/lib
# COPY --from=builder /home/ffmpeg_build/lib .
# WORKDIR /usr/local/include/opencv4/
# COPY --from=builder /usr/local/include/opencv4/ .
# WORKDIR /opt/opencv/build/lib
# COPY --from=builder /home/opencv/build/lib .

# # Set environment variables
# ENV PATH="$PATH:/home/bin"
# ENV PKG_CONFIG_PATH="$PKG_CONFIG_PATH:/home/ffmpeg_build/lib/pkgconfig:/usr/local/lib64/pkgconfig"
# ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/home/opencv/build/lib"

# WORKDIR /home/video_cap

# COPY pyproject.toml /home/video_cap
# COPY setup.py /home/video_cap
# COPY src /home/video_cap/src/

# # Install Python package
# RUN python3.12 -m pip install .

# # Location of the "extract_mvs" script
# ENV PATH="$PATH:/opt/_internal/cpython-3.12.7/bin"

# CMD ["sh", "-c", "tail -f /dev/null"]
