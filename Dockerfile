FROM ubuntu:18.04

WORKDIR /home/video_cap

COPY install.sh /home/video_cap
COPY ffmpeg_patch /home/video_cap/ffmpeg_patch/

# Install dependencies
RUN mkdir -p /home/video_cap && \
  cd /home/video_cap && \
  chmod +x install.sh && \
  ./install.sh

# Set environment variables
ENV PATH="$PATH:/home/bin"
ENV PKG_CONFIG_PATH="$PKG_CONFIG_PATH:/home/ffmpeg_build/lib/pkgconfig"

COPY setup.py /home/video_cap
COPY src /home/video_cap/src/

# Install video_cap Python module
RUN cd /home/video_cap && \
  python3 setup.py install

# Install debugging tools
RUN apt-get update && \
  apt-get -y install \
  gdb \
  python3-dbg

CMD ["sh", "-c", "tail -f /dev/null"]
