FROM quay.io/pypa/manylinux_2_24_x86_64 AS builder

WORKDIR /home/video_cap

# Install build tools
RUN apt-get update -qq --fix-missing && \
  apt-get upgrade -y && \
  apt-get install -y \
    wget \
    unzip \
    build-essential \
    cmake \
    git \
    pkg-config \
    autoconf \
    automake \
    git-core && \
    rm -rf /var/lib/apt/lists/*

# Install OpenCV
COPY install_opencv.sh /home/video_cap
RUN mkdir -p /home/video_cap && \
  cd /home/video_cap && \
  chmod +x install_opencv.sh && \
  ./install_opencv.sh

# Install FFMPEG
COPY install_ffmpeg.sh /home/video_cap
COPY ffmpeg_patch /home/video_cap/ffmpeg_patch/
RUN mkdir -p /home/video_cap && \
  cd /home/video_cap && \
  chmod +x install_ffmpeg.sh && \
  ./install_ffmpeg.sh

FROM quay.io/pypa/manylinux_2_24_x86_64

RUN apt-get update && \
  apt-get -y install \
    pkg-config \
    libgtk-3-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libmp3lame-dev \
    zlib1g-dev \
    libx264-dev \
    libsdl2-dev \
    libvpx-dev \
    libvdpau-dev \
    libvorbis-dev \
    libopus-dev \
    libdc1394-22-dev \
    liblzma-dev && \
    rm -rf /var/lib/apt/lists/*

# copy libraries
WORKDIR /usr/local/lib
COPY --from=builder /usr/local/lib .
WORKDIR /usr/local/include
COPY --from=builder /home/ffmpeg_build/include .
WORKDIR /home/ffmpeg_build/lib
COPY --from=builder /home/ffmpeg_build/lib .
WORKDIR /usr/local/include/opencv4/
COPY --from=builder /usr/local/include/opencv4/ .
WORKDIR /home/opencv/build/lib
COPY --from=builder /home/opencv/build/lib .

# Set environment variables
ENV PATH="$PATH:/home/bin"
ENV PKG_CONFIG_PATH="$PKG_CONFIG_PATH:/home/ffmpeg_build/lib/pkgconfig"
ENV LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/home/opencv/build/lib"

WORKDIR /home/video_cap

COPY setup.py /home/video_cap
COPY src /home/video_cap/src/

# Install Python package
COPY vid.mp4 /home/video_cap
RUN python3.10 -m pip install --upgrade pip build && \
  python3.10 -m pip install 'pkgconfig>=1.5.1' 'numpy>=1.17.0'

RUN python3.10 -m pip install .

# that is where the "extract_mvs" script is located
ENV PATH="$PATH:/opt/_internal/cpython-3.10.2/bin"

CMD ["sh", "-c", "tail -f /dev/null"]
