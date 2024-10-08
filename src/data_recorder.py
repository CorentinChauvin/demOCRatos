"""
    Class to record real time data, and keep track of time
"""

import numpy as np
import csv
from datetime import datetime
from time import time
from typing import List


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

        self._fps_avg_len = 10  # how many points used to average the fps output

    def add_field(self, name: str):
        """
        Adds a data field to record, given its name
        """
        if name in self._data:
            print(
                f"[Recorder] Adding a field that already exists ({name}), cancelling"
            )
            return

        self._data[name] = [[t, None] for t in self._last_times]

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

    def reset_fields(self, names: List[str]):
        """
        Resets all the field names, and stop any recording
        """
        self._data = {}
        self._is_recording = False

        for name in names:
            self.add_field(name)

    def toggle_recording(self, is_recording: bool) -> str:
        """
        Starts or stops the data recording

        Returns
            Name of the saved file, if stopping the recording (otherwise "")
        """
        path = ""

        if is_recording:
            self._data = {key: [] for key in self._data}
            self._start_time = time()
            self._last_times = []
        else:
            path = self._save_data()

        self._is_recording = is_recording

        return path

    def record(self, new_data: dict, t: float | None = None):
        """
        Records new data for a given time, if currently in recording mode

        The keys in `new_data` should correspond to data field names.
        If some data fields are missing, they will be recorded as None.

        If t is not given (or None), the current system time is taken
        """
        if t is None:
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
        if len(self._last_times) <= 1:
            return 0.0

        n = min(self._fps_avg_len, len(self._last_times))
        dt = np.average(np.diff(self._last_times[-n:]))
        return 1.0 / dt

    def _save_data(self, file_path: str = "") -> str:
        """
        Saves the data in a CSV file and returns the name of the file
        """
        if file_path == "":
            date_str = datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
            file_name = f"data_{date_str}.csv"
            file_path = f"/tmp/{file_name}"

        with open(file_path, "w") as f:
            csv_writer = csv.writer(
                f, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
            )

            csv_writer.writerow(["t"] + list(self._data.keys()))

            for k in range(len(self._last_times)):
                row = [self._last_times[k]] + [
                    self._data[key][k][1] for key in self._data
                ]
                csv_writer.writerow(row)

        print(f"[Recorder] Saved data at {file_path}")

        return file_path
