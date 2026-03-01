# utils/drawing.py

import cv2
import numpy as np

from config import (
    FONT,
    FONT_SCALE,
    FONT_THICKNESS,
    NORMAL_COLOR_BGR,
    ALERT_COLOR_BGR,
    CONSECUTIVE_FRAMES,
)


def draw_eye_contour(frame: np.ndarray, eye_landmarks: np.ndarray, color: tuple):
    """
    Draw a polygon around the eye landmarks.

    Parameters
    ----------
    frame         : BGR frame to draw on
    eye_landmarks : np.ndarray of shape (6, 2) — pixel coordinates
    color         : BGR tuple
    """
    points = eye_landmarks.astype(np.int32)
    cv2.polylines(frame, [points], isClosed=True, color=color, thickness=1)


def draw_ear_value(frame: np.ndarray, ear: float, is_drowsy: bool):
    """
    Display current EAR value in top-left corner.
    Color shifts red when drowsy.
    """
    color = ALERT_COLOR_BGR if is_drowsy else NORMAL_COLOR_BGR
    cv2.putText(
        frame,
        f"EAR: {ear:.3f}",
        (10, 30),
        FONT,
        FONT_SCALE,
        color,
        FONT_THICKNESS,
    )


def draw_status(frame: np.ndarray, is_drowsy: bool, frame_counter: int):
    """
    Display system status and a progress bar showing
    how close the driver is to triggering an alert.
    """
    h, w = frame.shape[:2]

    # Status text
    status_text  = "DROWSY" if is_drowsy else "ALERT"
    status_color = ALERT_COLOR_BGR if is_drowsy else NORMAL_COLOR_BGR

    cv2.putText(
        frame,
        f"Status: {status_text}",
        (10, 60),
        FONT,
        FONT_SCALE,
        status_color,
        FONT_THICKNESS,
    )

    # ── Progress bar ──────────────────────────────────────────────────────────
    # Shows how many consecutive closed-eye frames have accumulated
    bar_x, bar_y      = 10, 80
    bar_width         = 200
    bar_height        = 15
    progress          = min(frame_counter / CONSECUTIVE_FRAMES, 1.0)
    filled_width      = int(bar_width * progress)

    # Background bar (grey)
    cv2.rectangle(
        frame,
        (bar_x, bar_y),
        (bar_x + bar_width, bar_y + bar_height),
        (100, 100, 100),
        -1,
    )

    # Filled portion — green → yellow → red based on progress
    if progress < 0.5:
        bar_color = NORMAL_COLOR_BGR          # Green
    elif progress < 0.85:
        bar_color = (0, 165, 255)             # Orange
    else:
        bar_color = ALERT_COLOR_BGR           # Red

    if filled_width > 0:
        cv2.rectangle(
            frame,
            (bar_x, bar_y),
            (bar_x + filled_width, bar_y + bar_height),
            bar_color,
            -1,
        )

    # Bar border
    cv2.rectangle(
        frame,
        (bar_x, bar_y),
        (bar_x + bar_width, bar_y + bar_height),
        (255, 255, 255),
        1,
    )


def draw_alert_banner(frame: np.ndarray):
    """
    Full-width red banner at the top of the frame when drowsiness is confirmed.
    Hard to miss — that's the point.
    """
    h, w = frame.shape[:2]

    # Semi-transparent red overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 50), ALERT_COLOR_BGR, -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

    # Centered alert text
    text      = "DROWSINESS DETECTED!"
    font_scale = 0.9
    thickness  = 2
    text_size  = cv2.getTextSize(text, FONT, font_scale, thickness)[0]
    text_x     = (w - text_size[0]) // 2
    text_y     = 33

    cv2.putText(
        frame,
        text,
        (text_x, text_y),
        FONT,
        font_scale,
        (255, 255, 255),
        thickness,
    )


def draw_no_face(frame: np.ndarray):
    """Display warning when no face is detected in frame."""
    cv2.putText(
        frame,
        "No face detected",
        (10, 30),
        FONT,
        FONT_SCALE,
        (0, 165, 255),   # Orange
        FONT_THICKNESS,
    )


def render_frame(
    frame         : np.ndarray,
    left_eye      : np.ndarray,
    right_eye     : np.ndarray,
    ear           : float,
    is_drowsy     : bool,
    frame_counter : int,
):
    """
    Master render function — call this once per frame.
    Composes all visual elements onto the frame in the correct order.

    Parameters
    ----------
    frame         : BGR frame (modified in-place)
    left_eye      : shape (6,2) landmark coords, or None
    right_eye     : shape (6,2) landmark coords, or None
    ear           : averaged EAR value
    is_drowsy     : current drowsiness state
    frame_counter : consecutive below-threshold frames
    """
    if left_eye is None or right_eye is None:
        draw_no_face(frame)
        return

    eye_color = ALERT_COLOR_BGR if is_drowsy else NORMAL_COLOR_BGR

    draw_eye_contour(frame, left_eye,  eye_color)
    draw_eye_contour(frame, right_eye, eye_color)
    draw_ear_value(frame, ear, is_drowsy)
    draw_status(frame, is_drowsy, frame_counter)

    if is_drowsy:
        draw_alert_banner(frame)


# adding a fps Counter
def draw_fps(frame: np.ndarray, fps: float):
    """Display FPS in bottom-left corner for performance monitoring."""
    h = frame.shape[0]
    cv2.putText(
        frame,
        f"FPS: {fps:.1f}",
        (10, h - 10),
        FONT,
        FONT_SCALE,
        (255, 255, 0),  # Yellow
        FONT_THICKNESS,
    )
