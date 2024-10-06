# DemOCRatos - OCR for the people

![version](https://img.shields.io/badge/Version-0.1-yellow)
![ubuntu 22.04](https://img.shields.io/badge/Ubuntu%2022.04-working-green)
![license](https://img.shields.io/badge/License-Apache%202.0-blue)

<div align="center">
    <img src="assets/logo_high.png" width=400 />
</div>

Attempting to read a portion of the screen and plot its data real time.

> Blazingly slow, but it just works

## Features

- Real time recognitions of numbers of the screen.
- Offline number recognition in a video file.
- Works on easily configurable areas, as many as one wants.
- Easy to integrate new OCR methods (see below TODO)

## Install

```bash
# Install Python version (if necessary)
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

- EasyOCR requires PyTorch and Scipy, so isn't lightweight. The first time the program is started, it will download necessary model weights (stored in `~/.EasyOCR/model`). See more details on the EasyOCR GitHub ([link](https://github.com/JaidedAI/EasyOCR)).

## Dependencies

- https://github.com/opencv/opencv-python
- https://github.com/tomschimansky/customtkinter
- https://github.com/tesseract-ocr/tesseract
- https://github.com/sirfz/tesserocr
- https://github.com/JaidedAI/EasyOCR

## TODO

- [x] Loading and processing videos
- [x] Saving/loading configuration
- [ ] Multi threading, for less blazing slowness
- [ ] Make it easy to add new OCR methods, and documenting it
- [ ] Logging not only in the Python terminal, but also in the logging text box
- [ ] Real time graphing
