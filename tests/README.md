# Tests

## Run Tests

You can run the test suite either directly on your machine or (easier) within the provided Docker container. Both methods require you to first clone the repository. To this end, change into the desired installation directory on your machine and run
```bash
git clone https://github.com/LukasBommes/mv-extractor.git mv_extractor
```

### In Docker Container

To run the tests in the Docker container, change into the `mv_extractor` directory, and run
```bash
./run.sh /bin/bash -c 'yum install -y compat-openssl10 && python3.12 -m unittest discover -s tests -p "*tests.py"'
```

### On Host

To run the tests directly on your machine, you need to install the motion vector extractor as explained [above](#step-1-install).

Now, change into the `mv_extractor` directory and run the tests with
```bash
python3.12 -m unittest discover -s tests -p "*tests.py"
```
Confirm that all tests pass.

Some tests run the [LIVE555 Media Server](http://www.live555.com/mediaServer/), which has dependencies on its own, such as OpenSSL. Make sure these dependencies are installed correctly on your machine, or otherwise you will get test failures with messages, such as "error while loading shared libraries: libssl.so.10: cannot open shared object file: No such file or directory". E.g. in Alma Linux you could fix this issue by installing OpenSSL with
```bash
yum install -y compat-openssl10
```
For other operating systems you may be lacking additional dependencies, and the package names and installation command may differ.


## Reference Test Data

This directory contains reference test data for validating mv-extractor output. The test suite compares current output against this reference data to ensure no regressions. More specifically the test suite verifies that:
1. Motion vector extraction produces consistent results
2. Frame decoding works correctly
3. Frame types are correctly identified

### Structure

- `h264/` - H.264 test video reference data
- `mpeg4_part2/` - MPEG-4 Part 2 test video reference data  
- `rtsp/` - RTSP stream reference data

### Data Format

Each subdirectory contains:
- `motion_vectors/` - Motion vector .npy files
- `frames/` - Frame image .jpg files
- `frame_types.txt` - Frame type information

### Reference Data Creation

Reference datasets for H.264 and MPEG-4 PART 2 were obtained by running the `extract_mvs` command of a manually verified version of the mvextractor on the provided video files `vid_h264.mp4` and `vid_mpeg4_part2.mp4`

RTSP reference data was obtained by streaming one of the video files with the [LIVE555 Media Server](http://www.live555.com/mediaServer/) and then reading the RTSP stream with the motion vector extractor. To reproduce the reference data, follow the steps below.

#### Convert input file into H.264 video elementary stream

First, convert the `vid_h264.mp4` file into a H.264 video elementary stream file. To this end, run
```
ffmpeg -i vid_h264.mp4 -vf scale=640:360 -vcodec libx264 -f h264 vid_h264.264
```
in the project's root directory.

The conversion is needed, because the LIVE555 Media Server cannot directly serve MP4 files. I also tried converting and serving both input videos as Matroska, which did not work well, and WebM, which did not work at all. Hence, I decided to stick with an H.264 video elementary stream.

The command also scales down the input video from 720p to 360p because the default `OutPacketBuffer::maxSize` in the media server is set too low to handle the 720p video. The server logs warnings like
```text
MultiFramedRTPSink::afterGettingFrame1(): The input frame data was too large for our buffer size (100176).  10743 bytes of trailing data was dropped!  Correct this by increasing "OutPacketBuffer::maxSize" to at least 110743, *before* creating this 'RTPSink'.  (Current value is 100000.)
```
and the resulting video frame is truncated at the bottom.

#### Serve the video with LIVE555 Media Server

Now, we serve the file `vid_h264.264` with LIVE555 Media Server. Place the file in a folder named `data`
```
mkdir -p data
cp vid_h264.264 ./data/vid_h264.264
```
and then run a frash manylinux Docker container, in which you mount the `data` folder as a volume
```
docker run -it -v $(pwd)/data:/data quay.io/pypa/manylinux_2_28_x86_64 /bin/bash
```
In the container install and start the LIVE555 Media Server
```
yum install -y wget compat-openssl10
wget -qP /usr/local/bin/ http://www.live555.com/mediaServer/linux/live555MediaServer
chmod +x /usr/local/bin/live555MediaServer
cd /data
live555MediaServer &
```
You may have to hit `CTRL+C` now to dismiss the log of the server. The server will continue running in the background.

#### Consume the RTSP stream with the motion vector extractor

Still in the Docker container, install the motion vector extractor
```
python3.12 -m pip install "motion-vector-extractor==1.1.0"
```
and run it to read and dump the RTSP stream to a folder named `out-reference`
```
/opt/python/cp312-cp312/bin/extract_mvs 'rtsp://localhost:554/vid_h264.264' --verbose --dump out-reference
```

#### Preserve reference data and cleanup

Finally, exist the container with
```
exit
```
Now, copy the folder `out-reference` into the `tests/reference/rtsp` folder.
```
cp -r data/out-reference tests/reference/rtsp
```
and cleanup
```
rm -rf data
```
