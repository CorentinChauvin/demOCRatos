#!/usr/bin/env python3
"""
    Runs OCR on an image to extract numbers
"""

import pytesseract
from cv2.typing import MatLike
import cv2
import numpy as np
from typing import Tuple


class OcrEngine:
    """
    TODO
    """
    def __init__(self):
        pass

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

        print(raw_output)

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

        shape = np.shape(img)
        img = cv2.resize(
            img, (shape[1] * 2, shape[0] * 2), interpolation=cv2.INTER_LINEAR
        )  # TODO: the factor should be a parameter

        img = self._unsharp_mask(img, kernel_size=(5, 5), amount=2, sigma=1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.threshold(
            img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]

        return img

    def _unsharp_mask(self, img, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
        """
        Returns a sharpened version of the image, using an unsharp mask
        """
        blurred = cv2.GaussianBlur(img, kernel_size, sigma)
        sharpened = float(amount + 1) * img - float(amount) * blurred
        sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
        sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
        sharpened = sharpened.round().astype(np.uint8)

        if threshold > 0:
            low_contrast_mask = np.absolute(img - blurred) < threshold
            np.copyto(sharpened, img, where=low_contrast_mask)

        return sharpened

    def _ocr(self, img: MatLike) -> str:
        """
        Reads the portion of image, and returns the raw output
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        output = pytesseract.image_to_string(
            img_rgb, config="--dpi 20 --psm 13 -c tessedit_char_whitelist=-0123456789."
        )

        return output.strip()
