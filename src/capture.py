"""
Class storing configuration data about a capture
"""

import numpy as np


class Capture:
    """
    Manages a capture's configuration and data
    """
    def __init__(self, name: str):
        """
        Sets initial name and default values
        """
        self._can_edit = True  # whether the capture's config can be changed
        self.name = name
        self.set_area(0, 0, 0, 0)  # default values

    def set_area(self, x_min: int, y_min: int, x_max: int, y_max: int):
        """
        Sets the capture area
        """
        if self._can_edit:
            self.x_min = x_min
            self.y_min = y_min
            self.x_max = x_max
            self.y_max = y_max

    def slice_area(self, array: np.ndarray) -> np.ndarray:
        """
        Slices a Numpy array according to the capture area coordinates, along
        the first two dimensions (the third dimension onwards is untouched)
        """
        slices = (
            slice(self.x_min, self.x_max + 1, 1),
            slice(self.y_min, self.y_max + 1, 1),
        ) + (slice(None),) * (array.ndim - 2)

        return array[slices]

    def toggle_edit(self, can_edit: bool):
        """
        Sets whether the config can be updated
        Can be used to temporarily disable the influence of any callback
        """
        self._can_edit = can_edit


class Captures:
    """
    Manages all captures
    """
    def __init__(self):
        self._captures = []
        self.add_capture()

    def add_capture(self) -> Capture:
        """
        Creates a new capture with default name, and returns it
        """
        self._captures.append(Capture(f"New capture {len(self._captures)}"))
        return self._captures[-1]

    def remove_capture(self, key: str):
        """
        Removes a capture given by its name
        If the capture doesn't exist, doesn't do anything
        If there is no capture left, creates a new default one
        """
        for k in range(len(self._captures)):
            if self._captures[k].name == key:
                del self._captures[k]
                break

        if len(self._captures) == 0:
            self.add_capture()

    def __getitem__(self, key: str) -> None | Capture:
        """
        Accesses a capture by its name
        Returns None if the capture doesn't exist
        """
        for capture in self._captures:
            if capture.name == key:
                return capture

        return None

    def get_first(self) -> Capture:
        """
        Returns the first capture in the list
        """
        return self._captures[0]

    def get_names(self) -> list[str]:
        """
        Returns the list of names of the all captures
        """
        return [capture.name for capture in self._captures]

    def rename(self, capture: Capture, name: str) -> bool:
        """
        Renames a capture, if the name hasn't been already taken

        Returns whether the renaming was successful
        """
        if name not in self.get_names():
            capture.name = name
            return True

        return False

