"""
    Class to record real time data, and keep track of time
"""

import numpy as np
from time import time


class DataRecorder:
    """
    Records real time unidimensional, and keeps track of time (even when not
    recording)
    """

    def __init__(self):
        self._data = {}  # recorded data ("field1": [[t0, x0], [t1, x1], ...]}
        self._is_recording = False  # whether data is currently being recorded
        self._start_time = None  # time at which the recording started
        self._last_times = []  # last times the recorder was called

    def add_field(self, name: str):
        """
        Adds a data field to record, given its name
        """
        if name in self._data:
            print(
                f"[Recorder] Adding a field that already exists ({name}), cancelling"
            )
            return

        self._data[name] = [[]]

    def rename_field(self, old_name: str, new_name: str):
        """
        Rename a data field
        """
        if old_name not in self._data:
            print(
                f"[Recorder] Renaming a field that doesn't exist ({old_name}), cancelling"
            )
            return

        if new_name in self._data:
            print(
                f"[Recorder] Adding a field that already exists ({new_name}), cancelling"
            )
            return

        self._data[new_name] = self._data.pop(old_name)

    def delete_field(self, name: str):
        """
        Removing a data field given its name
        """
        if name not in self._data:
            print(
                f"[Recorder] Removing a field that doesn't exist ({name}), cancelling"
            )
            return

        self._data.pop(name)

    def toggle_recording(self, is_recording: bool):
        """
        Starts or stops the data recording
        """
        if is_recording:
            self._data = {key: [] for key in self._data}
            self._start_time = time()
            self._last_times = []

        self._is_recording = is_recording

    def record(self, new_data: dict):
        """
        Records new data for the current time, if currently in recording mode

        The keys in `new_data` should correspond to data field names.
        If some data fields are missing, they will be recorded as None.
        """
        t = time()
        self._last_times.append(t)

        if not self._is_recording:
            return

        for key in self._data:
            if key in new_data:
                self._data[key].append([t, new_data[key]])
            else:
                self._data[key].append([t, None])

    def get_is_recording(self) -> bool:
        return self._is_recording

    def get_recording_time(self) -> float:
        if not self._is_recording or self._start_time is None:
            return 0.0
        else:
            return time() - self._start_time

    def get_average_fps(self) -> float:
        """
        Returns the average update frequency of the last data points
        It works even when not in recording mode.
        """
        dt = np.average(np.diff(self._last_times[-10:]))
        return 1.0 / dt


