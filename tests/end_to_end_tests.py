import os
import time
import tempfile
import unittest
import subprocess

import cv2
import numpy as np


PROJECT_ROOT = os.getenv("PROJECT_ROOT", "")


class TestEndToEnd(unittest.TestCase):

    def motions_vectors_valid(self, outdir, refdir):
        equal = []
        num_mvs = len(os.listdir(os.path.join(refdir, "motion_vectors")))
        for i in range(num_mvs):
            mvs = np.load(os.path.join(outdir, "motion_vectors", f"mvs-{i}.npy"))
            mvs_ref = np.load(os.path.join(refdir, "motion_vectors", f"mvs-{i}.npy"))
            equal.append(np.all(mvs == mvs_ref))
        return all(equal)


    def frame_types_valid(self, outdir, refdir):
        with open(os.path.join(outdir, "frame_types.txt"), "r") as file:
            frame_types = [line.strip() for line in file]
        with open(os.path.join(refdir, "frame_types.txt"), "r") as file:
            frame_types_ref = [line.strip() for line in file]
        return frame_types == frame_types_ref


    def frames_valid(self, outdir, refdir):
        equal = []
        num_frames = len(os.listdir(os.path.join(refdir, "frames")))
        for i in range(num_frames):
            frame = cv2.imread(os.path.join(outdir, "frames", f"frame-{i}.jpg"))
            frame_ref = cv2.imread(os.path.join(refdir, "frames", f"frame-{i}.jpg"))
            equal.append(np.all(frame == frame_ref))
        return all(equal)


    def test_end_to_end_h264(self):
        with tempfile.TemporaryDirectory() as outdir:
            print("Running extraction for H.264")
            subprocess.run(f"extract_mvs {os.path.join(PROJECT_ROOT, 'vid_h264.mp4')} --dump {outdir}", shell=True, check=True)
            refdir = os.path.join(PROJECT_ROOT, "tests/reference/h264")

            self.assertTrue(self.motions_vectors_valid(outdir, refdir), msg="motion vectors are invalid")
            self.assertTrue(self.frame_types_valid(outdir, refdir), msg="frame types are invalid")
            self.assertTrue(self.frames_valid(outdir, refdir), msg="frames are invalid")


    def test_end_to_end_mpeg4_part2(self):
        with tempfile.TemporaryDirectory() as outdir:
            print("Running extraction for MPEG-4 Part 2")
            subprocess.run(f"extract_mvs {os.path.join(PROJECT_ROOT, 'vid_mpeg4_part2.mp4')} --dump {outdir}", shell=True, check=True)
            refdir = os.path.join(PROJECT_ROOT, "tests/reference/mpeg4_part2")

            self.assertTrue(self.motions_vectors_valid(outdir, refdir), msg="motion vectors are invalid")
            self.assertTrue(self.frame_types_valid(outdir, refdir), msg="frame types are invalid")
            self.assertTrue(self.frames_valid(outdir, refdir), msg="frames are invalid")


    def test_end_to_end_rtsp(self):
        with tempfile.TemporaryDirectory() as outdir:
            print("Setting up end to end test for RTSP")
            rtsp_server = subprocess.Popen(os.path.join(PROJECT_ROOT, "live555MediaServer"))
            try:
                time.sleep(1)
                print("Running extraction for RTSP stream")
                rtsp_url = "rtsp://localhost:554/vid_h264.264"
                subprocess.run(f"extract_mvs {rtsp_url} --dump {outdir}", shell=True, check=True)
                refdir = os.path.join(PROJECT_ROOT, "tests/reference/rtsp")

                self.assertTrue(self.motions_vectors_valid(outdir, refdir), msg="motion vectors are invalid")
                self.assertTrue(self.frame_types_valid(outdir, refdir), msg="frame types are invalid")
                self.assertTrue(self.frames_valid(outdir, refdir), msg="frames are invalid")
            finally:
                rtsp_server.terminate()


if __name__ == '__main__':
    unittest.main()
            