FROM ubuntu:18.04

# Copy files into the container
COPY . /home/video_cap

# Debugging tools
RUN apt-get update && \
  apt-get -y install \
  gdb \
  python3-dbg

WORKDIR /home

# Install VideoCap and it's dependencies
RUN mkdir -p /home/video_cap && \
  cd /home/video_cap && \
  chmod +x install.sh && \
  ./install.sh

RUN cd /home/video_cap && \
  python3 setup.py install

CMD ["sh", "-c", "tail -f /dev/null"]
