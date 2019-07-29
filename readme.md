# H.264 Motion Vector Capture

This modules provides a `VideoCap` C++ class (with a Python wrapper) for reading frames, motion vectors and frame types (I, P, B, etc.) from H.264 encoded video streams. Both video files and RTSP streams (e.g. from an IP camera) are supported. Under the hood [FFMPEG](https://github.com/FFmpeg/FFmpeg) is used and the interface and functionality are similar to the OpenCV [VideoCapture](https://docs.opencv.org/4.1.0/d8/dfe/classcv_1_1VideoCapture.html) class.

![motion_vector_demo_image](mvs.png)

A usage example can be found in `video_cap_test.py`.


## Installation

Prebuild binaries are not available. The library needs to be installed and build from source following the instructions below.

<details>
  <summary>Installation on host (Ubuntu 18.04)</summary>

Install wget and git.
```
apt-get update && apt-get install -y wget git
```
Clone the git repository and run the installer script for installing dependencies.
```
mkdir -p /home && cd home && \
git clone https://xxx:xxx@github.com/LukasBommes/h264-videocap.git video_cap && \
cd video_cap && \
chmod +x install.sh && \
./install.sh
```
Set environment variables (to permanently store them, append to `~/.profile` and source `~/.profile`)
```
export PATH="$PATH:$/home/bin"
export PKG_CONFIG_PATH="$PKG_CONFIG_PATH:/home/ffmpeg_build/lib/pkgconfig"
```
Compile the source and make the python wrapper
```
cd /home/video_cap && python3 setup.py install
```
</details>

<details>
  <summary>Installation in Docker image</summary>

```
FROM ubuntu:18.04

RUN apt-get update && \
  apt-get install -y \
    wget \
    git && \
    rm -rf /var/lib/apt/lists/*

# Build h264-videocap from source
RUN mkdir -p /home && cd home && \
  git clone https://LukasBommes:d0a87a5495a6e87ee2b835d6a1150fa430333e92@github.com/LukasBommes/h264-videocap.git video_cap && \
  cd video_cap && \
  chmod +x install.sh && \
  ./install.sh

# Set environment variables
ENV PATH="$PATH:/home/bin"
ENV PKG_CONFIG_PATH="$PKG_CONFIG_PATH:/home/ffmpeg_build/lib/pkgconfig"

RUN cd /home/video_cap && \
  python3 setup.py install

WORKDIR /home

CMD ["sh", "-c", "tail -f /dev/null"]

```
</details>

## Usage

For a usage example of the library refer to `video_cap_test.py`. To run the example, simply type
```
python3 video_cap_test.py
```
In the example a H.264 encoded video file is opened by `VideoCap.open` and frames, motion vectors, frame types and timestamps are read by calling `VideoCap.read` repeatedly. Extracted motion vectors are drawn onto the video frame (see image above). Before exiting the program, the video file is closed by `VideoCap.release`.

## Explanation










What follows is a short explanation of the data returned by the `VideoCap` class. Apart from this less obvious data the current video frame is returned.

##### Motion Vectors

H.264 uses different techniques to reduce the size of a raw video frame prior to sending it over a network or storing it into a file. One of those techniques is motion estimation and prediction of future frames based on previous or future frames. Each frame is split into 16 pixel x 16 pixel large macroblocks. During encoding motion estimation matches every macroblock to a similar looking macroblock in a previously encoded frame (note that this frame can also be a future frame since encoding and playout order might differ). This allows to transmit only those motion vectors and the reference macroblock instead of all macroblocks, effectively reducing the amount of transmitted or stored data. <br>
Motion vectors correlate strong with motion in the video scene and are useful for various computer vision tasks, such as optical tracking.

##### Frame Types

The frame type is either "P", "B" or "I" and refers to the H.264 encoding mode of the current frame.  Each frame

Note that for "I" frames

##### Timestamps

In addition to extracting motion vectors and frame types, the video capture class also outputs a UNIX timestamp representing UTC wall time for each frame. If the stream originates from a video, this timestamp is simply derived from the current system time. However, when an RTSP stream is used as input, the timestamp calculation is more intricate as the timestamps represents not the time when the frame was received, but the time when the frame was send by the sender. Thus, this timestamp can later be used for accurate synchronization of multiple video streams.








## Python API

#### Class :: VideoCap()

| Methods | Description |
| --- | --- |
| VideoCap() | Constructor |
| open() | Open a video file or url |
| read() | Get the next frame and motion vectors from the stream |
| release() | Close a video file or url and release all ressources |

##### Method :: VideoCap()

Constructor. Takes no input arguments.

##### Method :: open()

Open a video file or url. The stream must be H264 encoded. Otherwise, undesired behaviour is
likely.

| Parameter | Type | Description |
| --- | --- | --- |
| url | string | Relative or fully specified file path or an url specifying the location of the video stream. Example "vid.flv" for a video file located in the same directory as the source files. Or "rtsp://xxx.xxx.xxx.xxx:554" for an IP camera streaming via RTSP. |

| Returns | Type | Description |
| --- | --- | --- |
| success | bool | True if video file or url could be opened sucessfully, false otherwise. |


##### Method :: read()

Get the next frame and motion vectors from the stream. Requires the media file to be open. This function should be called in a loop and break the loop once the end of the stream is reached.

Takes no input arguments and returns a boost::python::tuple with four elements as in the table below.

| Index | Name | Type | Description |
| --- | --- | --- | --- |
| 0 | success | bool | False in case the read did not succeed or the end of stream is reached, true if a frame could be decoded successfully. When false, the other tuple elements are set to 0. |
| 1 | frame | boost::python::ndarray | Array of dtype uint8_t shape (w, h, 3) containing the decoded video frame. w and h are the width and height of this frame in pixels. If no frame could be decoded an empty numpy ndarray of shape (0, 0, 3) and dtype uint8_t is returned. |
| 2 | motion vectors | boost::python::ndarray | Array of dtype int64 and shape (N, 11) containing the N motion vectors of the frame returned in ret[1]. Each row in the array is a single motion vector. The columns contain the following data: <br>- 0: source: Where the current macroblock comes from. Negative value when it comes from the past, positive value when it comes from the future.<br>- 1: w: Width and height of the vector's macroblock.<br>- 2: h: Height of the vector's macroblock.<br>- 3: src_x: x-location of the vector's origin in source frame (in pixels).<br>- 4: src_y: y-location of the vector's origin in source frame (in pixels).<br>- 5: dst_x: x-location of the vector's destination in the current frame (in pixels).<br>- 6: dst_y: y-location of the vector's destination in the current frame (in pixels).<br>- 7: motion_x: src_x = dst_x + motion_x / motion_scale<br>- 8: motion_y: src_y = dst_y + motion_y / motion_scale<br>- 9: motion_scale: see definiton of columns 7 and 8<br>- 10: flags: currently unused<br>This data is equivalent to FFMPEG's [AVMotionVector](https://ffmpeg.org/doxygen/4.1/structAVMotionVector.html) class. If no motion vectors are present in a frame, e.g. if the frame is an `I` frame an empty numpy array of shape (0, 11) and dtype int64 is returned. |
| 3 | frame_type | char | single character representing the type of frame. Can be `I` for a keyframe, `P` for a frame with references to only past frames and `B` for a frame with references to both past and future frames. A value of `?` indicates an unknown frame type. |


##### Method :: release()

Close a video file or url and release all ressources. Takes no input arguments and returns nothing.


## C++ API

The C++ API differs from the Python API in what parameters the methods expect and what values they return. Refer to the demo in `main.cpp` for examples how to use the API.


## What are Frame Types and Motion Vectors in H264?

Refer to this [excellent book](http://last.hit.bme.hu/download/vidtech/k%C3%B6nyvek/Iain%20E.%20Richardson%20-%20H264%20%282nd%20edition%29.pdf) by Iain E. Richardson.


## About

This software is written by **Lukas Bommes, M.Sc.** - [A*Star SIMTech, Singapore](https://www.a-star.edu.sg/simtech)<br>
It is based on [MV-Tractus](https://github.com/jishnujayakumar/MV-Tractus/tree/master/include) and OpenCV's [videoio module](https://github.com/opencv/opencv/tree/master/modules/videoio).


#### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
