# DemOCRatos - OCR for the people

![version](https://img.shields.io/badge/Version-1.0-yellow)
![ubuntu 22.04](https://img.shields.io/badge/Ubuntu%2022.04-Kinda%20working-green)
![license](https://img.shields.io/badge/License-Apache%202.0-blue)

<div align="center">
    <img src="assets/logo_high.png" width=300 />
</div>

Attempting to read portions of a screen or a video and exporting its data in a CSV file.

> *Blazingly slow, but it kinda works*

<!-- **Contents:** -->
## Contents

1. [Features](#features)
2. [Install](#install)
3. [Run](#run)
4. [Notes](#notes)
5. [Dependencies](#dependencies)

<div align="center">
  <a href="https://vimeo.com/1019582159" target="_blank">
    <img src="assets/video_preview.jpg" />
  </a>
</div>

## Features

- Real time recognitions of numbers of the screen.
- Offline number recognition in a video file.
- Works on easily configurable areas, as many as one wants.
- Integrated Tesseract OCR and EasyOCR.
- Easy to add new OCR methods (see `src/ocr.py`).
- Dead simple to use!

## Install

This has been mainly developed and tested on Ubuntu 22.04, with Python 3.10.

```bash
# Install Python version >= 3.10 (necessary on lower Ubuntu versions)
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13 python3.13-venv python3.13-tk

# Install dependencies
sudo apt install tesseract-ocr libtesseract-dev

git clone ... && cd ocr_motor
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional additional OCR methods
pip install easyocr
```

## Run

```bash
source .venv/bin/activate
python gui.py
```

## Notes

- Known OCR issues:
    - Characters confusion, depending on the font: `0` and `8`, `1` and `7`, `5` and `9`.
    - Missing dot (*e.g.* `42.42` turned into `4242`).
- Tips to improve OCR reliability:
    - Upscale the detected area, to get a better characters resolution.
    - Use min and max bounds to filter outliers out.
    - Don't trust the OCR output too much. Potentially implement post-filtering based on knowledge of the recorded data. For example if measuring a variable that can only evolve slowly, big jumps in the output value can be marked as outliers and discarded.
- When processing a video, enabling the preview can induce up to 20% overhead.
- EasyOCR requires PyTorch and Scipy, so isn't lightweight. The first time the program is started, it will download necessary model weights (stored in `~/.EasyOCR/model`). See more details on the EasyOCR GitHub ([link](https://github.com/JaidedAI/EasyOCR)). With this application, it seems that EasyOCR is slower than Tesseract.

## Dependencies

This work is merely a wrapper and a graphical interface for some already existing OCR implementations. It heavily uses Tkinter and CustomTkinter for the interface.

- [OpenCV](https://github.com/opencv/opencv-python) (MIT license): image processing.
- [CustomTkinter](https://github.com/tomschimansky/customtkinter) (MIT license): beautiful interface and GUI.
- [Tesseract](https://github.com/tesseract-ocr/tesseract) (Apache 2.0): OCR API.
- [Tesserocr](https://github.com/sirfz/tesserocr) (MIT license): Python wrapper for Tesseract.
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) (Apache 2.0): another OCR API.

## TODO (maybe one day)

- [x] Loading and processing videos
- [x] Saving/loading configuration
- [x] Multi threading, for less blazing slowness
- [ ] Make it easier to add new OCR methods, and documenting it
- [x] Logging not only in the Python terminal, but also in the logging text box
- [ ] Real time graphing
