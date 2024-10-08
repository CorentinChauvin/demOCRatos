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
        self._stop_processing = False  # whether a request to stop processing was received

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
        frame_idx = 0
        dt = 1.0 / cap.get(cv2.CAP_PROP_FPS)
        record_offset_t = 1.0 / self._fps
        t = 0.0
        last_t = 0.0

        self._data_recorder.toggle_recording(True)

        while cap.isOpened() and not self._stop_processing:
            ret, frame = cap.read()
            t += dt
            frame_idx += 1

            if not ret:
                break

            if t - last_t < record_offset_t or frame is None:
                continue

            last_t = t
            output = self._captures.update(frame)
            print(
                f"[{frame_idx}/{frame_count}][{int(frame_idx / frame_count * 100)} %] {output}"
            )
            self._data_recorder.record(output, t)
            frame_cb(output, [frame_idx, frame_count])

        path = self._data_recorder.toggle_recording(False)
        self._stop_processing = False
        cap.release()

        return path

    def stop_processing(self):
        """
        Requests the processor to stop any current processing
        """
        self._stop_processing = True
