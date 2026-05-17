# Hand Tracking Gesture Painter

Hand Tracking Gesture Painter is a Python webcam app for drawing with hand gestures. It uses OpenCV for camera/video rendering and MediaPipe for real-time hand landmark tracking.

The app is built around a two-hand workflow:

- the left hand selects the current tool or action;
- the right hand moves the brush pointer with the index finger.

## Features

- Real-time hand tracking from a webcam.
- Two-hand gesture control.
- Drawing and erasing on a persistent canvas.
- Brush color switching.
- Brush size control.
- Canvas reset and PNG export.
- On-screen HUD with FPS, current mode, control action, color, and brush size.
- Fast mode for weaker laptops.

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

- Python 3.12
- Webcam
- OpenCV
- MediaPipe
- NumPy

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
