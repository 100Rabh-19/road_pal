# main.py

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"]  = "3"

import cv2

from config          import CAMERA_INDEX, FRAME_WIDTH, FRAME_HEIGHT
from detector        import FaceEyeDetector
from ear_calculator  import compute_ear, compute_average_ear
from drowsiness_monitor import DrowsinessMonitor
from alert           import AlertSystem
from utils.drawing   import render_frame


def main():
    # ── Initialize all components ─────────────────────────────────────────────
    cap      = cv2.VideoCapture(CAMERA_INDEX)
    detector = FaceEyeDetector()
    monitor  = DrowsinessMonitor()
    alert    = AlertSystem()

    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        print("[ERROR] Cannot open camera. Check CAMERA_INDEX in config.py")
        return

    print("[INFO] System started. Press 'q' to quit.")

    # ── Main video loop ───────────────────────────────────────────────────────
    while True:
        ret, frame = cap.read()

        if not ret:
            print("[ERROR] Failed to read frame from camera.")
            break

        # Step 1: Extract eye landmarks
        left_eye, right_eye = detector.extract_eye_landmarks(frame)

        ear       = 0.0
        is_drowsy = False

        if left_eye is not None and right_eye is not None:
            # Step 2: Compute EAR
            left_ear  = compute_ear(left_eye)
            right_ear = compute_ear(right_eye)
            ear       = compute_average_ear(left_ear, right_ear)

            # Step 3: Update drowsiness state
            is_drowsy = monitor.update(ear)

            # Step 4: Trigger alert if drowsy
            if is_drowsy:
                alert.trigger()
            else:
                alert.silence()

        # Step 5: Get monitor state for display
        status = monitor.get_status()

        # Step 6: Render all visuals onto frame
        render_frame(
            frame         = frame,
            left_eye      = left_eye,
            right_eye     = right_eye,
            ear           = ear,
            is_drowsy     = is_drowsy,
            frame_counter = status["frame_counter"],
        )

        # Step 7: Show frame
        cv2.imshow("Driver Drowsiness Detection", frame)

        # Step 8: Quit on 'q'
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("[INFO] Quitting...")
            break

    # ── Cleanup ───────────────────────────────────────────────────────────────
    cap.release()
    detector.close()
    cv2.destroyAllWindows()

    print(f"[INFO] Session ended. Total drowsiness alerts: {monitor.total_alerts}")


if __name__ == "__main__":
    main()