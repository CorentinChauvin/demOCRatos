#!/usr/bin/env python3
"""
    Runs OCR on an image to extract numbers
"""

import pytesseract
from cv2.typing import MatLike
import cv2
import numpy as np
from copy import deepcopy
from typing import Tuple


class BaseOcrEngine:
    """
    Base class for an engine extracting numbers from an image
    """
    class PreProcessConfig:
        invert_img: bool = False  # Whether to invert the image before the preprocessing
        upscale_ratio: float = (
            1.0  # Amount used to resize the input image (>1 for upscale)
        )
        unsharp_kernel_size: int = 5  # Kernel size for the unsharp filter
        unsharp_sigma: float = 1.0  # Gaussian filter std for the unsharp filter
        unsharp_amount: float = 1.0  # Unsharpening ratio

    def __init__(self):
        self._config = self.PreProcessConfig()

    def set_pre_process_config(self, config: PreProcessConfig):
        """
        Sets the configuration for the image pre-processing
        """
        config = deepcopy(config)
        config.unsharp_kernel_size = abs(config.unsharp_kernel_size)
        config.upscale_ratio = abs(config.upscale_ratio)

        if config.unsharp_kernel_size % 2 == 0:
            config.unsharp_kernel_size += 1

        if config.upscale_ratio < 0.01:
            config.upscale_ratio = self._config.upscale_ratio

        self._config = deepcopy(config)

    def get_pre_process_config(self) -> PreProcessConfig:
        """
        Returns the configuration for the image pre-processing
        """
        return self._config

    def process(self, raw_img: np.ndarray) -> Tuple[str, np.ndarray]:
        """
        Processes an image and runs OCR on it

        Args:
            - raw_img: The image to process
        Returns:
            - The output given by OCR
            - The preprocessed image used for OCR
        """
        img = self._preprocess_img(raw_img)
        raw_output = self._ocr(img)

        return raw_output, img

    def _preprocess_img(self, raw_img: np.ndarray) -> MatLike:
        """
        Prepares a raw image for OCR.

        Performs the following steps:
            - Turns the image into black and white
            - Enlarges the image by a given factor
            - Sharpens the image (unsharp mask)
            - Thresholds the image (otsu)
        """
        # img = cv2.cvtColor(raw_img, cv2.COLOR_GRAY2BGR)
        img = raw_img

        if self._config.invert_img:
            img = cv2.bitwise_not(img)

        shape = np.shape(img)
        new_shape = (
            int(shape[1] * self._config.upscale_ratio),
            int(shape[0] * self._config.upscale_ratio),
        )
        img = cv2.resize(
            img, new_shape, interpolation=cv2.INTER_LINEAR
        )

        img = self._unsharp_mask(img)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        return img

    def _unsharp_mask(self, img: MatLike) -> MatLike:
        """
        Returns a sharpened version of the image, using an unsharp mask
        """
        amount = float(self._config.unsharp_amount)

        blurred = cv2.GaussianBlur(
            img, (self._config.unsharp_kernel_size,) * 2, self._config.unsharp_sigma
        )
        sharpened = (1.0 + amount) * img - amount * blurred
        sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
        sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
        sharpened = sharpened.round().astype(np.uint8)

        return sharpened

    def _ocr(self, img: MatLike) -> str:
        """
        Reads the portion of image, and returns the raw output

        Has to be implemented for a specic OCR method
        """
        return "???"


class TesseractOcrEngine(BaseOcrEngine):
    """
    Uses Tesseract to extract digits from an image
    """
    def __init__(self):
        BaseOcrEngine.__init__(self)

    def _ocr(self, img: MatLike) -> str:
        """
        Reads the portion of image, and returns the raw output
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        output = pytesseract.image_to_string(
            img_rgb, config="--dpi 20 --psm 13 -c tessedit_char_whitelist=-0123456789."
        )

        return output.strip()
