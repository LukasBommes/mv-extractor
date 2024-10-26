import os
import tempfile
import unittest
import subprocess

import cv2
import numpy as np


video_url_h264 = "/home/video_cap/vid_h264.mp4"
video_url_mpeg4_part2 = "/home/video_cap/vid_mpeg4_part2.mp4"
reference_output_h264 = "/home/video_cap/tests/reference/h264"
reference_output_mpeg4_part2 = "/home/video_cap/tests/reference/mpeg4_part2"


def motions_vectors_valid(outdir):
    equal = []
    for i in range(336):
        mvs = np.load(os.path.join(outdir, "motion_vectors", f"mvs-{i}.npy"))
        mvs_ref = np.load(os.path.join(reference_output_h264, "motion_vectors", f"mvs-{i}.npy"))
        equal.append(np.all(mvs == mvs_ref))
    return all(equal)


def frame_types_valid(outdir):
    with open(os.path.join(outdir, "frame_types.txt"), "r") as file:
        frame_types = [line.strip() for line in file]
    with open(os.path.join(reference_output_h264, "frame_types.txt"), "r") as file:
        frame_types_ref = [line.strip() for line in file]
    return frame_types == frame_types_ref


def frames_valid(outdir):
    equal = []
    for i in range(336):
        frame = cv2.imread(os.path.join(outdir, "frames", f"frame-{i}.jpg"))
        frame_ref = cv2.imread(os.path.join(reference_output_h264, "frames", f"frame-{i}.jpg"))
        equal.append(np.all(frame == frame_ref))
    return all(equal)


class TestEndToEnd(unittest.TestCase):

    def test_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            print("Running extraction")
            subprocess.run(f"extract_mvs {video_url_h264} --dump", cwd=tmp_dir, shell=True, check=True)
            outdir = os.path.join(tmp_dir, os.listdir(tmp_dir)[0])

            assert motions_vectors_valid(outdir), "motion vectors are invalid"
            assert frame_types_valid(outdir), "frame types are invalid"
            assert frames_valid(outdir), "frames are invalid"


if __name__ == '__main__':
    unittest.main()
            