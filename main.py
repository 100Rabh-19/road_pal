# main.py

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"]  = "3"

import cv2
import time

from config             import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT
from detector           import FaceEyeDetector
from ear_calculator     import compute_ear, compute_average_ear
from drowsiness_monitor import DrowsinessMonitor
from alert              import AlertSystem
from utils.drawing      import render_frame, draw_fps


def main():
    # ── Initialize ────────────────────────────────────────────────────────────
    cap      = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)  # CAP_DSHOW = faster on Windows
    detector = FaceEyeDetector()
    monitor  = DrowsinessMonitor()
    alert    = AlertSystem()

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer lag — always process latest frame

    if not cap.isOpened():
        print("[ERROR] Cannot open camera. Check CAMERA_INDEX in config.py")
        return

    print("[INFO] System started. Press 'q' to quit.")

    # ── FPS tracking ──────────────────────────────────────────────────────────
    fps          = 0.0
    frame_count  = 0
    fps_timer    = time.time()

    # ── Frame skip control ────────────────────────────────────────────────────
    # Process MediaPipe every N frames — reduces CPU load significantly
    # Display still updates every frame so video stays smooth
    PROCESS_EVERY_N_FRAMES = 2
    last_left_eye  = None
    last_right_eye = None
    last_ear       = 0.0
    last_is_drowsy = False

    # ── Main loop ─────────────────────────────────────────────────────────────
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Failed to read frame.")
            break

        frame_count += 1

        # ── FPS calculation (updated every second) ────────────────────────────
        elapsed = time.time() - fps_timer
        if elapsed >= 1.0:
            fps       = frame_count / elapsed
            frame_count = 0
            fps_timer = time.time()

        # ── Detection (runs every N frames) ───────────────────────────────────
        if frame_count % PROCESS_EVERY_N_FRAMES == 0:
            left_eye, right_eye = detector.extract_eye_landmarks(frame)

            if left_eye is not None and right_eye is not None:
                left_ear  = compute_ear(left_eye)
                right_ear = compute_ear(right_eye)
                ear       = compute_average_ear(left_ear, right_ear)
                is_drowsy = monitor.update(ear)

                if is_drowsy:
                    alert.trigger()
                else:
                    alert.silence()

                # Cache results for frames we skip
                last_left_eye  = left_eye
                last_right_eye = right_eye
                last_ear       = ear
                last_is_drowsy = is_drowsy
            else:
                monitor.update(0.0)
                last_left_eye  = None
                last_right_eye = None

        # ── Render (every frame for smooth display) ───────────────────────────
        status = monitor.get_status()

        render_frame(
            frame         = frame,
            left_eye      = last_left_eye,
            right_eye     = last_right_eye,
            ear           = last_ear,
            is_drowsy     = last_is_drowsy,
            frame_counter = status["frame_counter"],
        )

        draw_fps(frame, fps)

        cv2.imshow("Driver Drowsiness Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("[INFO] Quitting...")
            break

    # ── Cleanup ───────────────────────────────────────────────────────────────
    cap.release()
    detector.close()
    cv2.destroyAllWindows()
    print(f"[INFO] Session ended. Total alerts: {monitor.total_alerts}")


if __name__ == "__main__":
    main()




### What changed and why

# **`cv2.CAP_DSHOW`** — DirectShow backend on Windows. Faster camera initialization and lower latency than the default backend.

# **`CAP_PROP_BUFFERSIZE = 1`** — By default OpenCV buffers 4–5 frames. This means you're processing frames that are already 150ms old. Setting buffer to 1 ensures you always work on the freshest frame — critical for a safety system.

# **Frame skipping** — MediaPipe is the heaviest part of the pipeline. Running it every 2nd frame halves CPU load while reusing the last known landmark positions for display. At 30fps, landmarks from 33ms ago are still accurate enough.

# ---

# ## Step 11: ML Upgrades — Where Real Systems Go

# This is what separates a university project from an automotive-grade system. I'll explain each upgrade conceptually so you know what exists and how to pursue it.

# ---

# ### 11.1 — PERCLOS (The Industry Standard Metric)

# **What it is:** Percentage of Eye Closure over time. Developed by the US DOT.

# Instead of counting consecutive frames, you measure:

# PERCLOS = (frames where EAR < threshold) / (total frames in last 60 seconds)