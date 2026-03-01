# 🚗 Driver Drowsiness Detection System

A real-time driver monitoring system that detects drowsiness using facial landmarks and Eye Aspect Ratio (EAR) analysis from a webcam or video stream.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Key Parameters](#key-parameters)
- [Visual Interface](#visual-interface)
- [Future Improvements](#future-improvements)

---

## Overview

This system uses computer vision to monitor a driver's eye state in real time. When the driver's eyes remain closed beyond a safe threshold, the system fires a visual and audio alert. The approach is based on the **Eye Aspect Ratio (EAR)** formula introduced by Soukupová & Čech (2016), combined with a temporal state machine that distinguishes between a normal blink and dangerous drowsiness.

---

## Tech Stack

| Library | Purpose |
|---|---|
| Python 3.10+ | Core language |
| OpenCV | Video capture and frame rendering |
| MediaPipe Face Mesh | 468-point facial landmark detection |
| NumPy | EAR math and coordinate handling |
| winsound | Native Windows audio alert |

---

## Project Structure

```
drowsiness_detector/
│
├── main.py                  # Entry point — video loop and pipeline orchestration
├── detector.py              # MediaPipe Face Mesh wrapper + landmark extraction
├── ear_calculator.py        # EAR formula implementation
├── drowsiness_monitor.py    # Temporal state machine (frame counter + alert logic)
├── alert.py                 # Threaded audio + visual alert system
├── config.py                # All tunable constants in one place
├── utils/
│   ├── __init__.py
│   └── drawing.py           # HUD overlay — eye contours, EAR, progress bar, banner
└── requirements.txt
```

---

## How It Works

```
Webcam Frame
     │
     ▼
┌─────────────────┐
│  Video Capture  │  ← OpenCV reads frames in real-time
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Face Detection │  ← MediaPipe Face Mesh finds 468 landmarks
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Eye Landmark    │  ← Extract 6 specific points per eye
│ Extraction      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ EAR Calculation │  ← Compute ratio using Euclidean distances
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Temporal Analysis│  ← Track consecutive frames where EAR < threshold
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Alert Engine   │  ← Audio beep + red banner when drowsiness confirmed
└─────────────────┘
```

### The EAR Formula

```
       ||p2 - p6|| + ||p3 - p5||
EAR = ─────────────────────────────
            2 × ||p1 - p4||
```

- **Open eye:** EAR ≈ 0.28 – 0.35
- **Closed eye:** EAR ≈ 0.05 – 0.10
- **Alert fires when:** EAR stays below threshold for N consecutive frames

---

## Installation

### 1. Clone or download the project

```bash
cd Desktop
mkdir drowsiness_detector
cd drowsiness_detector
```

### 2. Create and activate virtual environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
```

### 3. Install dependencies

```bash
pip install opencv-python mediapipe numpy
```

### 4. Verify installation

```bash
python -c "import cv2; import mediapipe; import numpy; print('All good')"
```

---

## Usage

Make sure your virtual environment is active and you are inside the project folder:

```bash
cd C:\Users\<your-name>\Desktop\drowsiness_detector
venv\Scripts\activate
python main.py
```

Press **`q`** to quit the application.

---

## Configuration

All tunable parameters live in `config.py`. You never need to touch any other file to recalibrate the system.

```python
# config.py

CAMERA_INDEX        = 0      # Change to 1 if using external webcam
FRAME_WIDTH         = 640
FRAME_HEIGHT        = 480

EAR_THRESHOLD       = 0.22   # Below this → eye considered closed
CONSECUTIVE_FRAMES  = 20     # Frames eye must stay closed before alert fires

MAX_FACES           = 1
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE  = 0.7
```

---

## Key Parameters

| Parameter | Default | Effect |
|---|---|---|
| `EAR_THRESHOLD` | `0.22` | Lower = less sensitive, higher = more sensitive |
| `CONSECUTIVE_FRAMES` | `20` | At 30fps, 20 frames ≈ 0.67 seconds of closure |
| `CAMERA_INDEX` | `0` | Change if default webcam is not used |
| `PROCESS_EVERY_N_FRAMES` | `2` | Frame skip for CPU optimization (in main.py) |

### Tuning tips

- If you get **too many false alerts** → lower `EAR_THRESHOLD` or raise `CONSECUTIVE_FRAMES`
- If the system is **too slow to react** → raise `EAR_THRESHOLD` or lower `CONSECUTIVE_FRAMES`
- If you wear **glasses** → you may need to lower `EAR_THRESHOLD` slightly (glasses reduce apparent EAR)

---

## Visual Interface

The live display shows:

| Element | Description |
|---|---|
| **Eye contours** | Green when awake, red when drowsy |
| **EAR value** | Real-time Eye Aspect Ratio (top-left) |
| **Status label** | ALERT (normal) or DROWSY |
| **Progress bar** | Fills green → orange → red as eye closure accumulates |
| **Alert banner** | Full-width red banner when drowsiness is confirmed |
| **FPS counter** | Live frames-per-second (bottom-left) |

---

## Future Improvements

| Upgrade | Description |
|---|---|
| **PERCLOS metric** | Industry-standard: % of eye closure over 60-second rolling window (USDOT validated) |
| **Head pose estimation** | Detect distracted driving when driver looks away from road |
| **Blink rate tracking** | Alert drivers blink < 8 times/min vs normal 15–20 times/min |
| **CNN eye classifier** | Deep learning model that works with glasses and poor lighting |
| **Per-driver calibration** | Personalized EAR baseline instead of fixed threshold |
| **IR camera support** | Night-time detection using infrared camera input |

---

## References

- Soukupová & Čech (2016) — *Real-Time Eye Blink Detection using Facial Landmarks*
- MediaPipe Face Mesh — https://mediapipe.dev
- US DOT PERCLOS Standard — Federal Highway Administration fatigue research

---

## License

This project is for educational and research purposes.
