import os
import unittest
import time

import numpy as np

from mvextractor.videocap import VideoCap


PROJECT_ROOT = os.getenv("PROJECT_ROOT", "")


class TestMotionVectorExtraction(unittest.TestCase):

    def validate_frame(self, frame):
        self.assertEqual(type(frame), np.ndarray, "Frame should be numpy array")
        self.assertEqual(frame.dtype, np.uint8, "Frame dtype should be uint8")
        self.assertEqual(frame.shape, (720, 1280, 3), "Frams hape should be (720, 1280, 3)")


    def validate_motion_vectors(self, motion_vectors, shape=(0, 10)):
        self.assertEqual(type(motion_vectors), np.ndarray, "Motion vectors should be numpy array")
        self.assertEqual(motion_vectors.dtype, np.int32, "Motion vectors dtype should be int32")
        self.assertEqual(motion_vectors.shape, shape, "Motion vectors shape not matching expected shape")


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
        self.assertIn('set_decode_frames', dir(self.cap))
        self.assertIn('decode_frames', dir(self.cap))


    def test_decode_frames_mode(self):
        self.cap = VideoCap()
        self.assertTrue(self.cap.decode_frames, "Frame decoding is expected to be actived by default")
        self.cap.set_decode_frames(True)
        self.assertTrue(self.cap.decode_frames, "Frame decoding is expected to be active")
        self.cap.set_decode_frames(False)
        self.assertFalse(self.cap.decode_frames, "Frame decoding is expected to be inactive")
        self.open_video()
        self.assertTrue(self.cap.decode_frames, "Frame decoding is expected to be actived after opening a video")
        self.cap.set_decode_frames(False)
        self.assertFalse(self.cap.decode_frames, "Frame decoding is expected to be inactive")
        self.cap.release()
        self.assertTrue(self.cap.decode_frames, "Frame decoding is expected to be active")


    def test_open_video(self):
        ret = self.open_video()
        self.assertTrue(ret, "Should open video file successfully")

    
    def test_open_invalid_video(self):
        ret = self.cap.open("vid_not_existent.mp4")
        self.assertFalse(ret, "Should fail to open non-existent video file")


    def test_read_not_opened_cap(self):
        ret = self.cap.open("vid_not_existent.mp4")
        self.assertFalse(ret, "Should fail to open non-existent video file")
        ret, frame, motion_vectors, frame_type = self.cap.read()
        self.assertEqual(frame_type, "?", "Frame type should be ?")
        self.assertFalse(ret, "Should fail to read from non-existent video file")
        self.assertIsNone(frame, "Frame read from non-existent video should be None")
        self.validate_motion_vectors(motion_vectors)


    def test_read_first_I_frame(self):
        self.open_video()
        ret, frame, motion_vectors, frame_type = self.cap.read()
        self.assertTrue(ret, "Should succeed to read from video file")
        self.assertEqual(frame_type, "I", "Frame type of first frame should be I")      
        self.validate_frame(frame)
        self.validate_motion_vectors(motion_vectors)


    def test_read_first_P_frame(self):
        self.open_video()
        self.cap.read()  # skip first frame (I frame)
        ret, frame, motion_vectors, frame_type = self.cap.read()
        self.assertTrue(ret, "Should succeed to read from video file")
        self.assertEqual(frame_type, "P", "Frame type of second frame should be P")      
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
        ])), "Motion vectors should match the expected values")


    def test_read_first_ten_frames(self):
        rets = []
        frames = []
        motion_vectors = []
        frame_types = []
        self.open_video()
        for _ in range(10):
            ret, frame, motion_vector, frame_type = self.cap.read()
            rets.append(ret)
            frames.append(frame)
            motion_vectors.append(motion_vector)
            frame_types.append(frame_type)

        self.assertTrue(all(rets), "All frames should be read successfully")
        self.assertEqual(frame_types, ['I', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'])
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
            ret, _, _, _ = self.cap.read()
            if not ret:
                break
            frame_count += 1
        self.assertEqual(frame_count, 337, "Video file is expected to have 337 frames")


    def test_timings(self):
        self.open_video()
        times = []
        while True:
            tstart = time.perf_counter()
            ret, _, _, _ = self.cap.read()
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
        self.assertLess(dt_std, 0.003, msg=f"Standard deviation of frame read duration exceeds maximum ({dt_std} s > {0.003} s)")


    def test_skipping_frame_decoding_does_not_raise(self):
        self.cap.set_decode_frames(False)
        self.cap.set_decode_frames(True)


    def test_read_first_I_frame_skipping_frame_decoding(self):
        self.open_video()
        self.cap.set_decode_frames(False)
        ret, frame, motion_vectors, frame_type = self.cap.read()
        self.assertTrue(ret, "Should succeed to read from video file")
        self.assertEqual(frame_type, "I", "Frame type of first frame should be I")
        self.assertIsNone(frame, "Frame should be None when skipping frame decoding")
        self.validate_motion_vectors(motion_vectors)
        

    def test_read_first_P_frame_skipping_frame_decoding(self):
        self.open_video()
        self.cap.set_decode_frames(False)
        self.cap.read()  # skip first frame (I frame)
        ret, frame, motion_vectors, frame_type = self.cap.read()
        self.assertTrue(ret, "Should succeed to read from video file")
        self.assertEqual(frame_type, "P", "Frame type of second frame should be P")      
        self.assertIsNone(frame, "Frame should be None when skipping frame decoding")
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
        ])), "Motion vectors should match the expected values")


    def test_read_first_ten_frames_skipping_frame_decoding(self):
        rets = []
        frames = []
        motion_vectors = []
        frame_types = []
        self.open_video()
        self.cap.set_decode_frames(False)
        for _ in range(10):
            ret, frame, motion_vector, frame_type = self.cap.read()
            rets.append(ret)
            frames.append(frame)
            motion_vectors.append(motion_vector)
            frame_types.append(frame_type)

        self.assertTrue(all(rets), "All frames should be read successfully")
        self.assertEqual(frame_types, ['I', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'])
        [self.assertIsNone(frame) for frame in frames]
        shapes = [
            (0, 10), (3665, 10), (3696, 10), (3722, 10), (3807, 10), 
            (3953, 10), (4155, 10), (3617, 10), (4115, 10), (4192, 10)
        ]
        [self.validate_motion_vectors(motion_vector, shape) for motion_vector, shape in zip(motion_vectors, shapes)]


    def test_frame_count_skipping_frame_decoding(self):
        self.open_video()
        self.cap.set_decode_frames(False)
        frame_count = 0
        while True:
            ret, _, _, _ = self.cap.read()
            if not ret:
                break
            frame_count += 1
        self.assertEqual(frame_count, 337, "Video file is expected to have 337 frames")


    def test_skipping_frame_decoding_is_faster_than_not_skipping(self):
        self.open_video()
        # skip frame decoding
        self.cap.set_decode_frames(False)
        start_time = time.perf_counter()
        frame_count = 0
        for _ in range(50):  # read 50 frames
            ret, _, _, _ = self.cap.read()
            if not ret:
                break
            frame_count += 1
        mvo_time = time.perf_counter() - start_time
        
        # do not skip frame decoding
        self.cap.set_decode_frames(True)
        start_time = time.perf_counter()
        frame_count_full = 0
        for i in range(50):  # Read 50 frames
            ret, _, _, _ = self.cap.read()
            if not ret:
                break
            frame_count_full += 1
        full_time = time.perf_counter() - start_time
        
        self.assertEqual(frame_count, 50, "Should read 50 frames")
        self.assertEqual(frame_count_full, 50, "Should read 50 frames")
        
        # Performance comparison (skipping decoding should be at least as fast as not skipping decoding mode)
        if mvo_time > 0 and full_time > 0:
            speedup = full_time / mvo_time
            print(f"Speedup by skipping frame decoding: {speedup:.2f}x")
            self.assertGreaterEqual(speedup, 1.0, "Skipping frame decoding should be reasonably fast")


if __name__ == '__main__':
    unittest.main()
