import os
import unittest
import time

import numpy as np

from mvextractor.videocap import VideoCap


PROJECT_ROOT = os.getenv("PROJECT_ROOT", "")


class TestMotionVectorExtraction(unittest.TestCase):

    def validate_timestamp(self, timestamp, tolerance=10.0):
        self.assertIsInstance(timestamp, float)
        self.assertLessEqual(timestamp, time.time())
        self.assertGreaterEqual(timestamp+tolerance, time.time())


    def validate_frame(self, frame):
        self.assertEqual(type(frame), np.ndarray)
        self.assertEqual(frame.dtype, np.uint8)
        self.assertEqual(frame.shape, (720, 1280, 3))


    def validate_motion_vectors(self, motion_vectors, shape=(0, 10)):
        self.assertEqual(type(motion_vectors), np.ndarray)
        self.assertEqual(motion_vectors.dtype, np.int32)
        self.assertEqual(motion_vectors.shape, shape)

    # run before every test
    def setUp(self):
        self.cap = VideoCap()


    # run after every test regardless of success
    def tearDown(self):
        self.cap.release()


    def open_video(self):
        return self.cap.open(os.path.join(PROJECT_ROOT, "vid_h264.mp4"))


    def test_init_cap(self):
        self.cap = VideoCap()
        self.assertIn('open', dir(self.cap))
        self.assertIn('grab', dir(self.cap))
        self.assertIn('read', dir(self.cap))
        self.assertIn('release', dir(self.cap))
        self.assertIn('retrieve', dir(self.cap))


    def test_open_video(self):
        ret = self.open_video()
        self.assertTrue(ret)

    
    def test_open_invalid_video(self):
        ret = self.cap.open("vid_not_existent.mp4")
        self.assertFalse(ret)


    def test_read_not_opened_cap(self):
        ret = self.cap.open("vid_not_existent.mp4")
        self.assertFalse(ret)
        ret, frame, motion_vectors, frame_type, timestamp = self.cap.read()
        self.assertEqual(frame_type, "?")
        self.assertEqual(timestamp, 0.0)
        self.assertFalse(ret)
        self.assertIsNone(frame)
        self.validate_motion_vectors(motion_vectors)


    def test_read_first_I_frame(self):
        self.open_video()
        ret, frame, motion_vectors, frame_type, timestamp = self.cap.read()
        self.assertTrue(ret)
        self.assertEqual(frame_type, "I")
        self.validate_timestamp(timestamp)        
        self.validate_frame(frame)
        self.validate_motion_vectors(motion_vectors)


    def test_read_first_P_frame(self):
        self.open_video()
        self.cap.read()  # skip first frame (I frame)
        ret, frame, motion_vectors, frame_type, timestamp = self.cap.read()
        self.assertTrue(ret)
        self.assertEqual(frame_type, "P")
        self.validate_timestamp(timestamp)        
        self.validate_frame(frame)
        self.validate_motion_vectors(motion_vectors, shape=(3665, 10))
        self.assertTrue(np.all(motion_vectors[:10, :] == np.array([
            [-1, 16, 16,   8, 8,   8, 8, 0, 0, 4],
            [-1, 16, 16,  24, 8,  24, 8, 0, 0, 4],
            [-1, 16, 16,  40, 8,  40, 8, 0, 0, 4],
            [-1, 16, 16,  56, 8,  56, 8, 0, 0, 4],
            [-1, 16, 16,  72, 8,  72, 8, 0, 0, 4],
            [-1, 16, 16,  88, 8,  88, 8, 0, 0, 4],
            [-1, 16, 16, 104, 8, 104, 8, 0, 0, 4],
            [-1, 16, 16, 120, 8, 120, 8, 0, 0, 4],
            [-1, 16, 16, 136, 8, 136, 8, 0, 0, 4],
            [-1, 16, 16, 152, 8, 152, 8, 0, 0, 4],
        ])))


    def test_read_first_ten_frames(self):
        rets = []
        frames = []
        motion_vectors = []
        frame_types = []
        timestamps = []
        self.open_video()
        for _ in range(10):
            ret, frame, motion_vector, frame_type, timestamp = self.cap.read()
            rets.append(ret)
            frames.append(frame)
            motion_vectors.append(motion_vector)
            frame_types.append(frame_type)
            timestamps.append(timestamp)

        self.assertTrue(all(rets))
        self.assertEqual(frame_types, ['I', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'])
        [self.validate_timestamp(timestamp) for timestamp in timestamps]
        [self.validate_frame(frame) for frame in frames]
        shapes = [
            (0, 10), (3665, 10), (3696, 10), (3722, 10), (3807, 10), 
            (3953, 10), (4155, 10), (3617, 10), (4115, 10), (4192, 10)
        ]
        [self.validate_motion_vectors(motion_vector, shape) for motion_vector, shape in zip(motion_vectors, shapes)]


    def test_frame_count(self):
        self.open_video()
        frame_count = 0
        while True:
            ret, _, _, _, _ = self.cap.read()
            if not ret:
                break
            frame_count += 1
        self.assertEqual(frame_count, 337)


    def test_timings(self):
        self.open_video()
        times = []
        while True:
            tstart = time.perf_counter()
            ret, _, _, _, _ = self.cap.read()
            if not ret:
                break
            tend = time.perf_counter()
            telapsed = tend - tstart
            times.append(telapsed)
        dt_mean = np.mean(times)
        dt_std = np.std(times)
        print(f"Timings: mean {dt_mean} s -- std: {dt_std} s")
        self.assertGreater(dt_mean, 0)
        self.assertGreater(dt_std, 0)
        self.assertLess(dt_mean, 0.01, msg=f"Mean of frame read duration exceeds maximum ({dt_mean} s > {0.01} s)")
        self.assertLess(dt_std, 0.001, msg=f"Standard deviation of frame read duration exceeds maximum ({dt_std} s > {0.001} s)")



if __name__ == '__main__':
    unittest.main()
