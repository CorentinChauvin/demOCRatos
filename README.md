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
```

## Dependencies

- https://github.com/tesseract-ocr/tesseract
- https://github.com/madmaze/pytesseract
- https://github.com/opencv/opencv-python
- https://github.com/tomschimansky/customtkinter
