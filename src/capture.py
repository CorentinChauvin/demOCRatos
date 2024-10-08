"""
Class storing configuration data about a capture
"""

from src.gui_elements import TkImage2
from src.ocr import BaseOcrEngine, TesseractOcrEngine, EasyOcrEngine, OcrMethod
import customtkinter as ctk
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple


class Capture:
    """
    Manages a capture's configuration and data
    """
    def __init__(self, name: str, img_root: ctk.CTkBaseClass, ocr_method: OcrMethod):
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
        self.show_preview = True  # whether to draw a preview of the captured area
        self._output_img = TkImage2(img_root)  # displayed output image
        self._output_txt = ctk.CTkLabel(img_root, text="-")
        self._min_value = None  # minimum acceptable value for post-processing (not used if None)
        self._max_value = None  # maximum acceptable value for post-processing (not used if None)

        self.set_ocr_method(ocr_method)

    def set_area(self, x_min: int, y_min: int, x_max: int, y_max: int):
        """
        Sets the capture area
        """
        if self._can_edit:
            self.x_min = x_min
            self.y_min = y_min
            self.x_max = x_max
            self.y_max = y_max

    def set_min_max_values(self, min_value: float | None, max_value: float | None):
        """
        Sets the extremum acceptable values of the number to detect with OCR

        If None, the extremum won't be used.
        """
        self._min_value = min_value
        self._max_value = max_value

    def display(self, column_idx: int):
        """
        Adds the output image and text to the root widget
        """
        self._output_img.get_tk_canvas().grid(row=0, column=column_idx, sticky="nsew")
        self._output_txt.grid(row=1, column=column_idx, sticky="nsew")

    def ocr(self, screen_img: np.ndarray) -> Tuple[str, np.ndarray] | Tuple[None, None]:
        """
        Processes the full screen image and displays its outputs

        Args:
            - screen_img: Full screen image
        Returns:
            - [computed output, preprocessed image to preview]
            OR
            - [None, None] if no output
        """
        if not self.is_enabled:
            return None, None

        img = self.slice_area(screen_img)
        shape = np.shape(img)

        if shape[0] == 0 or shape[1] == 0:
            return None, None

        output, processed_img = self._ocr_engine.process(img)

        return output, processed_img


    def update(self, output: str, processed_img: np.ndarray):
        """
        Updates the image and text previews on the GUI
        """
        if self.show_preview:
            self._output_img.update(processed_img)
            self._output_txt.configure(text=f"{self.name}: {output}")


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

    def set_ocr_method(self, method: OcrMethod):
        """
        Sets the method used to perform OCR
        """
        if hasattr(self, "_ocr_engine"):
            pre_config = self._ocr_engine.get_pre_process_config()
        else:
            pre_config = None

        if method == OcrMethod.TESSERACT:
            self._ocr_engine = TesseractOcrEngine()
        elif method == OcrMethod.EASY_OCR:
            self._ocr_engine = EasyOcrEngine()

        if pre_config is not None:
            self._ocr_engine.set_pre_process_config(pre_config)

    def post_process(self, output_str: str | None):
        """
        Turns the OCR output into a float. Returns None if it failed.
        """
        if output_str is None:
            return None

        try:
            value = float(output_str)
        except ValueError:
            return None

        if self._min_value is not None and value < self._min_value:
            return None

        if self._max_value is not None and value > self._max_value:
            return None

        return value


class Captures:
    """
    Manages all captures
    """

    def __init__(self, root: ctk.CTkBaseClass):
        self._ocr_method = OcrMethod.TESSERACT
        self._captures: list[Capture] = []
        self._root = root
        self._max_threads = 1
        self.add_capture()

    def add_capture(self) -> Capture:
        """
        Creates a new capture with default name, and returns it
        """
        self._captures.append(
            Capture(f"New capture {len(self._captures)}", self._root, self._ocr_method)
        )
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

    def get_config(self):
        """
        Returns a dictionary with configuration for all captures
        """
        config = {}

        for capture in self._captures:
            name = capture.name
            ocr_conf = capture.get_pre_process_config()

            config[name] = {}
            config[name]["area"] = [capture.x_min, capture.y_min, capture.x_max, capture.y_max]
            config[name]["is_enabled"] = capture.is_enabled
            config[name]["show_preview"] = capture.show_preview
            config[name]["ocr"] = {}

            for key in dir(ocr_conf):
                if key[0:2] != "__":
                    config[name]["ocr"][key] = getattr(ocr_conf, key)

        return config

    def load_config(self, config):
        """
        Resets all captures with given configuration provided as a dictionary
        """
        self._captures = []

        for name in config:
            capture = self.add_capture()
            capture.name = name
            capture.set_area(*config[name]["area"])
            capture.show_preview = config[name]["show_preview"]
            ocr = BaseOcrEngine.PreProcessConfig()

            for key in config[name]["ocr"]:
                setattr(ocr, key, config[name]["ocr"][key])

            capture.set_pre_process_config(ocr)

        if len(self._captures) == 0:
            self.add_capture()

    def set_max_threads(self, max_threads: int | None):
        """
        Sets the maximum number of threads used for OCR (None sets no limit)
        """
        self._max_threads = max_threads

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
            if capture.is_enabled and capture.show_preview:
                capture.display(k)
                k += 1

    def update(self, screen_img: np.ndarray):
        """
        Processes the full screen image and displays all enabled outputs

        Args:
            - screen_img: Full screen image
        Returns
            Dictionary of captured data (key: data name)
        """
        outputs = {}
        futures = {}

        with ThreadPoolExecutor(max_workers=self._max_threads) as executor:
            for capture in self._captures:
                if not capture.is_enabled:
                    continue

                futures[capture.name] = executor.submit(capture.ocr, screen_img)

        for name in futures:
            output, processed_img = futures[name].result()
            output = self[name].post_process(output)
            outputs[name] = output
            self[name].update(output, processed_img)

        return outputs

    def set_ocr_method(self, method: OcrMethod):
        """
        Sets the method used to perform OCR
        """
        self._ocr_method = method

        for capture in self._captures:
            capture.set_ocr_method(method)
