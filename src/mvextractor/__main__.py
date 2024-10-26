import sys
import os
import time
from datetime import datetime
import argparse

import numpy as np
import cv2

from mvextractor.videocap import VideoCap


def draw_motion_vectors(frame, motion_vectors):
    if len(motion_vectors) > 0:
        num_mvs = np.shape(motion_vectors)[0]
        for mv in np.split(motion_vectors, num_mvs):
            start_pt = (mv[0, 3], mv[0, 4])
            end_pt = (mv[0, 5], mv[0, 6])
            cv2.arrowedLine(frame, start_pt, end_pt, (0, 0, 255), 1, cv2.LINE_AA, 0, 0.1)
    return frame


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser(description='Extract motion vectors from video.')
    parser.add_argument('video_url', type=str, nargs='?', help='File path or url of the video stream')
    parser.add_argument('-p', '--preview', action='store_true', help='Show a preview video with overlaid motion vectors')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show detailled text output')
    parser.add_argument('-d', '--dump', nargs='?', const=True,
        help='Dump frames, motion vectors, frame types, and timestamps to output directory. Optionally specify the output directory.')
    args = parser.parse_args()

    if args.dump:
        if isinstance(args.dump, str):
            dumpdir = args.dump
        else:
            dumpdir = f"out-{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}"
        for child in ["frames", "motion_vectors"]:
            os.makedirs(os.path.join(dumpdir, child), exist_ok=True)

    cap = VideoCap()

    # open the video file
    ret = cap.open(args.video_url)

    if not ret:
        raise RuntimeError(f"Could not open {args.video_url}")
    
    if args.verbose:
        print("Sucessfully opened video file")

    step = 0
    times = []

    # continuously read and display video frames and motion vectors
    while True:
        if args.verbose:
            print("Frame: ", step, end=" ")

        tstart = time.perf_counter()

        # read next video frame and corresponding motion vectors
        ret, frame, motion_vectors, frame_type, timestamp = cap.read()

        tend = time.perf_counter()
        telapsed = tend - tstart
        times.append(telapsed)

        # if there is an error reading the frame
        if not ret:
            if args.verbose:
                print("No frame read. Stopping.")
            break

        # print results
        if args.verbose:
            print("timestamp: {} | ".format(timestamp), end=" ")
            print("frame type: {} | ".format(frame_type), end=" ")

            print("frame size: {} | ".format(np.shape(frame)), end=" ")
            print("motion vectors: {} | ".format(np.shape(motion_vectors)), end=" ")
            print("elapsed time: {} s".format(telapsed))

        frame = draw_motion_vectors(frame, motion_vectors)

        # store motion vectors, frames, etc. in output directory
        if args.dump:
            cv2.imwrite(os.path.join(dumpdir, "frames", f"frame-{step}.jpg"), frame)
            np.save(os.path.join(dumpdir, "motion_vectors", f"mvs-{step}.npy"), motion_vectors)
            with open(os.path.join(dumpdir, "timestamps.txt"), "a") as f:
                f.write(str(timestamp)+"\n")
            with open(os.path.join(dumpdir, "frame_types.txt"), "a") as f:
                f.write(frame_type+"\n")

        step += 1

        if args.preview:
            cv2.imshow("Frame", frame)

            # if user presses "q" key stop program
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    if args.verbose:
        print("average dt: ", np.mean(times))

    cap.release()

    # close the GUI window
    if args.preview:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    sys.exit(main())
