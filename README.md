# ocr_screen

Attempting to read a portion of the screen and plot its data real time.

> Blazingly slow, but it kinda works

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
