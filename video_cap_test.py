import time

import numpy as np
import cv2

from video_cap import VideoCap

def draw_motion_vectors(frame, motion_vectors):
    if len(motion_vectors) > 0:
        num_mvs = np.shape(motion_vectors)[0]
        for mv in np.split(motion_vectors, num_mvs):
            start_pt = (mv[0, 3], mv[0, 4])
            end_pt = (mv[0, 5], mv[0, 6])
            cv2.arrowedLine(frame, start_pt, end_pt, (0, 0, 255), 1, cv2.LINE_AA, 0, 0.1)
    return frame


if __name__ == "__main__":

    # filename of the video file
    url = "vid.mp4"

    cap = VideoCap()

    # open the video file
    ret = cap.open(url)

    if not ret:
        raise RuntimeError("Could not open the video url")

    print("Sucessfully opened video file")

    step = 0
    times = []

    # continuously read and display video frames and motion vectors
    while True:
        print("Frame: ", step, end=" ")
        step += 1

        tstart = time.perf_counter()

        # read next video frame and corresponding motion vectors
        ret, frame, motion_vectors, frame_type, timestamp = cap.read()

        tend = time.perf_counter()
        telapsed = tend - tstart
        times.append(telapsed)

        # if there is an error reading the frame
        if not ret:
            print("No frame read. Stopping.")
            break;

        # print results
        print("timestamp: {} | ".format(timestamp), end=" ")
        print("frame type: {} | ".format(frame_type), end=" ")

        print("frame size: {} | ".format(np.shape(frame)), end=" ")
        print("motion vectors: {} | ".format(np.shape(motion_vectors)), end=" ")
        print("elapsed time: {} s".format(telapsed))

        frame = draw_motion_vectors(frame, motion_vectors)

        # show frame
        cv2.imshow("Frame", frame)

        # if user presses "q" key stop program
        if cv2.waitKey(1) & 0xFF == ord('q'):
           break

    print("average dt: ", np.mean(times))

    cap.release()

    # close the GUI window
    cv2.destroyAllWindows()
