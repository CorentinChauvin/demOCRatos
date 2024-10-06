"""
Processes a video and runs OCR on it
"""

from src.data_recorder import DataRecorder
from cv2.typing import MatLike
from src.capture import Captures
import cv2
from typing import Callable


class VideoProcessor:
    """
    Processes a video and runs OCR on it
    """
    def __init__(self, data_recorder: DataRecorder):
        self._data_recorder = data_recorder
        self._video_path = None  # path for the video file to process
        self._captures = None  # captures configuration and processing
        self._preview_frame = None  # preview frame of the video
        self._fps = 1.0  # how many frames per second need to be processed in the video

    def set_video_path(self, video_path: str):
        """
        Sets the path of the video file to process
        """
        # Gets the preview frame of the video (in the middle of the video)
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2)
        ret, self._preview_frame = cap.read()

        if not ret:
            print("[VideoProcessor] ERROR: Couldn't read video")
            cap.release()
            return

        # from matplotlib import pyplot as plt
        # plt.imshow(self._preview_frame)
        # plt.show()

        self._video_path = video_path
        cap.release()

    def set_fps(self, fps: float):
        """
        Sets how many frames per seconds need to be processed in the video
        """
        self._fps = fps

    def get_preview_frame(self) -> None | MatLike:
        """
        Returns a preview frame of the currently loaded video (None if not available)
        """
        return self._preview_frame

    def set_captures(self, captures: Captures):
        """
        Sets a reference to the captures to process
        """
        self._captures = captures

    def process_video(self, frame_cb: Callable) -> str:
        """
        Processes the video file

        Args:
            - frame_cb: Will be called at each processed frame
        Returns:
            Path of the saved CSV file

        frame_cb(output, progress):
            - output: dictionary of detected values for each capture
            - progress: [current_frame, total_frame_count]
        """
        if self._video_path is None:
            print("[VideoProcessor] No valid video selected")
            return ""

        assert self._captures is not None

        cap = cv2.VideoCapture(self._video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_offset = max(1, int(cap.get(cv2.CAP_PROP_FPS) / self._fps))
        frame_idx = 0
        self._data_recorder.toggle_recording(True)

        while cap.isOpened():
            ret, frame = cap.read()
            frame_idx += 1

            if not ret:
                break

            if frame_idx % frame_offset != 0:
                continue

            if frame is None:
                continue

            output = self._captures.update(frame)
            print(
                f"[{frame_idx}/{frame_count}][{int(frame_idx / frame_count * 100)} %] {output}"
            )
            self._data_recorder.record(output)
            frame_cb(output, [frame_idx, frame_count])

        path = self._data_recorder.toggle_recording(False)
        cap.release()

        return path
