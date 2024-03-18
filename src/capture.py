"""
Class storing configuration data about a capture
"""

from src.gui_elements import TkImage2
from src.ocr import BaseOcrEngine, TesseractOcrEngine
import customtkinter as ctk
import numpy as np


class Capture:
    """
    Manages a capture's configuration and data
    """
    def __init__(self, name: str, img_root: ctk.CTkBaseClass):
        """
        Sets initial name and default values

        Args:
            - name:     Name of the capture
            - img_root: Root of the displayed image
        """
        self.name = name
        self._can_edit = True  # whether the capture's config can be changed
        self.set_area(0, 0, 0, 0)  # default values

        self.is_enabled = True  # whether to compute its output and display it
        self._output_img = TkImage2(img_root)  # displayed output image
        self._output_txt = ctk.CTkLabel(img_root, text="-")

        self._ocr_engine = TesseractOcrEngine()

    def set_area(self, x_min: int, y_min: int, x_max: int, y_max: int):
        """
        Sets the capture area
        """
        if self._can_edit:
            self.x_min = x_min
            self.y_min = y_min
            self.x_max = x_max
            self.y_max = y_max

    def display(self, column_idx: int):
        """
        Adds the output image and text to the root widget
        """
        self._output_img.get_tk_canvas().grid(row=0, column=column_idx, sticky="nsew")
        self._output_txt.grid(row=1, column=column_idx, sticky="nsew")

    def update(self, screen_img: np.ndarray) -> float | None:
        """
        Processes the full screen image and displays its outputs

        Args:
            - screen_img: Full screen image
        Returns:
            - computed output (displayed image on the screen)
            OR
            - None if output not enabled
        """
        if not self.is_enabled:
            return None

        img = self.slice_area(screen_img)
        output, processed_img = self._ocr_engine.process(img)

        self._output_img.update(processed_img)
        self._output_txt.configure(text=f"{self.name}: {output}")

        return 0.0

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

    def set_pre_process_config(self, config: BaseOcrEngine.PreProcessConfig):
        """
        Updates the configuration for the image pre-processing
        """
        self._ocr_engine.set_pre_process_config(config)

    def get_pre_process_config(self) -> BaseOcrEngine.PreProcessConfig:
        """
        Returns the configuration for the OCR image pre-processing
        """
        return self._ocr_engine.get_pre_process_config()


class Captures:
    """
    Manages all captures
    """

    def __init__(self, root: ctk.CTkBaseClass):
        self._captures: list[Capture] = []
        self._root = root
        self.add_capture()

    def add_capture(self) -> Capture:
        """
        Creates a new capture with default name, and returns it
        """
        self._captures.append(Capture(f"New capture {len(self._captures)}", self._root))
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

    def update_layout(self):
        """
        Updates the tk layout to display all enabled outputs
        """
        for slave in self._root.grid_slaves():
            slave.grid_forget()

        k = 0

        for capture in self._captures:
            if capture.is_enabled:
                capture.display(k)
                k += 1

    def update(self, screen_img: np.ndarray):
        """
        Processes the full screen image and displays all enabled outputs

        Args:
            - screen_img: Full screen image
        """
        for capture in self._captures:
            if not capture.is_enabled:
                continue

            capture.update(screen_img)
