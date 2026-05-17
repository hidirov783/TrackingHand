<div align="center">

# Hand Tracking Gesture Painter

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Webcam-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand_Tracking-00A67E?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-111827?style=for-the-badge)

Draw on your screen with real-time hand gestures.

[Features](#features) · [Gesture Controls](#gesture-controls) · [Installation](#installation) · [Usage](#usage) · [Troubleshooting](#troubleshooting)

</div>

Hand Tracking Gesture Painter is a Python webcam app for drawing with hand gestures. It uses OpenCV for camera/video rendering and MediaPipe for real-time hand landmark tracking.

The app is built around a two-hand workflow:

- the left hand selects the current tool or action;
- the right hand moves the brush pointer with the index finger.

> A small computer-vision playground for learning hand tracking, gesture recognition, and webcam interaction in Python.

## Quick Start

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

## Features

| Feature | Description |
| --- | --- |
| Real-time tracking | Detects and tracks hands from your webcam |
| Two-hand workflow | Left hand controls tools, right hand moves the pointer |
| Drawing canvas | Persistent drawing layer over the camera feed |
| Tool control | Draw, erase, change color, resize brush, clear canvas |
| HUD | Shows FPS, mode, control action, brush size, and current color |
| Export | Saves the drawing as `hand_drawing.png` |
| Performance mode | Lower resolution and hidden landmarks for more FPS |

## Gesture Controls

Default roles:

| Hand | Gesture | Action |
| --- | --- | --- |
| Left | Thumb + index closed | Enable draw mode |
| Left | Thumb + middle closed | Enable erase mode |
| Left | Thumb + ring closed | Change color |
| Left | Thumb + pinky closed | Clear canvas |
| Left | Only thumb raised | Increase brush size |
| Left | Only pinky raised | Decrease brush size |
| Right | Index finger raised | Move the brush pointer |

The left hand never draws. The right hand never changes tools.

If MediaPipe labels your hands the other way around, swap roles:

```bash
python main.py --draw-hand Left --control-hand Right
```

## Keyboard Shortcuts

| Key | Action |
| --- | --- |
| `q` | Quit |
| `r` | Reset canvas |
| `s` | Save canvas to `hand_drawing.png` |

## Requirements

| Requirement | Version / Note |
| --- | --- |
| Python | `3.12` recommended |
| Webcam | Built-in or external |
| OpenCV | Installed from `requirements.txt` |
| MediaPipe | Pinned to `0.10.21` |
| NumPy | Installed from `requirements.txt` |

This project currently pins `mediapipe==0.10.21` because newer Python/MediaPipe combinations may not provide the legacy `mp.solutions` API used by the app.

## Installation

### macOS

```bash
brew install python@3.12
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Allow camera access for your terminal or IDE in:

```text
System Settings -> Privacy & Security -> Camera
```

### Windows

Install Python 3.12 from the official Python website, then run:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If the camera is blocked, check:

```text
Settings -> Privacy & security -> Camera
```

### Linux

Install Python 3.12 using your distribution package manager, then run:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If OpenCV cannot access the webcam, check that your user has access to the video device, for example `/dev/video0`.

## Usage

Start the app:

```bash
python main.py
```

Use another camera:

```bash
python main.py --camera 1
```

Fast mode:

```bash
python main.py --width 960 --height 540 --hide-landmarks --model-complexity 0
```

More accurate mode:

```bash
python main.py --model-complexity 1 --min-detection-confidence 0.75
```

## Command Line Options

```bash
python main.py --help
```

Useful options:

| Option | Description |
| --- | --- |
| `--camera` | Webcam index, usually `0` or `1` |
| `--width` / `--height` | Requested camera resolution |
| `--max-hands` | Maximum number of hands to track |
| `--model-complexity` | `0` for speed, `1` for accuracy |
| `--hide-landmarks` | Hide hand skeleton rendering for more FPS |
| `--draw-hand` | Hand used as the brush pointer |
| `--control-hand` | Hand used for tool selection |

## Project Structure

```text
.
├── main.py              # Main webcam gesture painting app
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── models/              # Optional local model files or experiments
```

## Troubleshooting

### `mediapipe` has no attribute `solutions`

Use Python 3.12 and reinstall dependencies:

```bash
deactivate
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Camera does not open

Try another camera index:

```bash
python main.py --camera 1
```

Also make sure your OS allows camera access for the terminal or IDE.

### Low FPS

Use fast mode:

```bash
python main.py --width 960 --height 540 --hide-landmarks --model-complexity 0
```

## Notes Before Publishing

- Do not commit `.venv/`, `__pycache__/`, `.matplotlib/`, or generated drawings.
- The included `.gitignore` excludes local runtime files.
- Add a license file if you want others to reuse the project publicly.
