This is a patched version of FFMPEG library.
The patch exposes several fields of the internal RTPDemuxContext class to the
AVPacket class which is accessible through public APIs. This allows to read out
for example timestamp and sequence number of an RTSP packet.

The following files have been patched:

libavcodec/avcodec.h
libavformat/rtpdec.c
libavformat/utils.c

For a detailed description of the changes refer to "patch_description.docx".
