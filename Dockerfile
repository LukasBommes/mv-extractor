FROM ubuntu:18.04

# Copy files into the container
COPY src /videocap
COPY ffmpeg_patch /home
COPY install.sh /videocap

# Run installer script to setup dependencies
COPY install.sh /videocap
RUN chmod +x /videocap/install.sh && \
    install.sh


# Debugging tools
RUN apt-get update -qq && \
  apt-get -y install \
  gdb \
  python3-dbg


# Install Python packages
COPY requirements.txt /
RUN pip3 install --upgrade pip
RUN pip3 install -r /requirements.txt

WORKDIR /videocap

COPY docker-entrypoint.sh /videocap
RUN chmod +x /videocap/docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]

CMD ["sh", "-c", "tail -f /dev/null"]
