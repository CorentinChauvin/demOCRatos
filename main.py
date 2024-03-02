#!/usr/bin/env python3
"""
TODO
"""

import pytesseract
from cv2.typing import MatLike
import cv2
import numpy as np
import csv


class DataConfig:
    def __init__(
        self, min_value: float, max_value: float, slice_x: slice, slice_y: slice
    ):
        """
        Args:
            - min_value: Minimum value the data field can take
            - max_value: Maximum value the data field can take
            - position_mask: Pixel location of the data field
        """
        self.min_value = min_value
        self.max_value = max_value
        self.slice_x = slice_x
        self.slice_y = slice_y


# =========================================================
# CONFIGURATION
#
video_path = "resources/long.mp4"
image_path = "resources/frame_raw.png"
output_file = "output/output.csv"
max_cnt = 1000

min_value = 20.0
max_value = 100.0

data_config = {
    "temperature": DataConfig(20.0, 100.0, slice(295, 311), slice(750, 770)),
    "current": DataConfig(0.0, 20.0, slice(295, 311), slice(576, 620)),
    "speed": DataConfig(0.0, 1500, slice(295, 311), slice(402, 450)),
}


# =========================================================
# OCR
#
def unsharp_mask(image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
    """
    Return a sharpened version of the image, using an unsharp mask
    """
    blurred = cv2.GaussianBlur(image, kernel_size, sigma)
    sharpened = float(amount + 1) * image - float(amount) * blurred
    sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
    sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
    sharpened = sharpened.round().astype(np.uint8)

    if threshold > 0:
        low_contrast_mask = np.absolute(image - blurred) < threshold
        np.copyto(sharpened, image, where=low_contrast_mask)

    return sharpened


def preprocess_frame(frame: MatLike, slice_x: slice, slice_y: slice) -> MatLike:
    """
    Crops a frame and preprocesses it ahead of OCR (upscaling, sharpening and
    thresholding)
    """
    cropped = frame[slice_x, slice_y]
    shape = np.shape(cropped)
    cropped = cv2.resize(
        cropped, (shape[1] * 2, shape[0] * 2), interpolation=cv2.INTER_LINEAR
    )

    cropped = unsharp_mask(cropped, kernel_size=(5, 5), amount=2, sigma=1)
    cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    cropped = cv2.threshold(
        cropped, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    return cropped


def ocr(image: MatLike) -> str:
    """
    Reads the portion of image, and returns the raw output
    """
    img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    output = pytesseract.image_to_string(
        img_rgb, config="--dpi 20 --psm 13 -c tessedit_char_whitelist=0123456789."
    )

    return output.strip()


# =========================================================
# POST PROCESSING
#
def filter(raw_string: str, min_value: float, max_value: float) -> float | None:
    """
    Tries to convert a string into a float, and returns only if the resulting value
    is within some given bounds.
    """
    try:
        value = float(raw_string)
    except ValueError:
        return None

    if value < min_value or value > max_value:
        return None

    return value


# =========================================================
# FILE PROCESSING
#
def run_video():
    cap = cv2.VideoCapture(video_path)
    cnt = 0
    outputs = {key: [] for key in data_config}
    outputs["t"] = []

    while cap.isOpened():
        ret, frame = cap.read()

        cnt += 1
        if cnt % 25 != 0:
            continue
        if cnt >= max_cnt:
            break

        print(cnt)

        if not ret:
            print("Can't receive frame (stream end?). Exiting...")
            break

        # cropped = frame[295:311, 590:620]  # current, second digit
        # cropped = frame[295:311, 576:592]  # current, first digit
        # cropped = frame[295:311, 576:620]  # current
        # cropped = frame[295:311, 402:450]  # RPM
        # cropped = frame[295:311, 750:770]  # temperature
        # shape = np.shape(cropped)
        # cropped = cv2.resize(
        #     cropped, (shape[1] * 2, shape[0] * 2), interpolation=cv2.INTER_LINEAR
        # )
        #
        # cropped = unsharp_mask(cropped, kernel_size=(5, 5), amount=2, sigma=1)
        # cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        # cropped = cv2.threshold(
        #     cropped, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        # )[1]
        #
        # value = ocr(cropped)
        #
        # if value is not None:
        #     values.append(value)
        #     t.append(cnt)
        #
        # print(value)

        for key in data_config:
            config = data_config[key]
            cropped = preprocess_frame(frame, config.slice_x, config.slice_y)
            raw_output = ocr(cropped)
            outputs[key].append(filter(raw_output, config.min_value, config.max_value))

        outputs["t"].append(cnt)


        cv2.imshow("frame", frame)

        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()

    return outputs


def run_image():
    img = cv2.imread(image_path)
    img = img[295:311, 748:770]
    # img = img[287:311, 661:760]
    # img = img[287:311, 661:826]

    ocr(img)

    cv2.imshow(image_path, img)
    cv2.waitKey(0)


if __name__ == "__main__":
    outputs = run_video()

    print(outputs)
    exit()

    with open(output_file, "w", newline="") as csv_file:
        fieldnames = ["t", "temperature"]
        writer = csv.DictWriter(
            csv_file, fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writeheader()

        for k in range(len(t)):
            writer.writerow({"t": t[k], "temperature": values[k]})

    # with open("output/data_out", "r") as f:
    #     raw_output = f.readline().strip("][\n").split(', ')
    #
    # output = []
    # min_value = 20.0
    # max_value = 100.0
    #
    # for x in raw_output:
    #     try:
    #         x = float(x)
    #     except ValueError:
    #         continue
    #
    #     if x < min_value or x > max_value:
    #         continue
    #
    #     output.append(x)
