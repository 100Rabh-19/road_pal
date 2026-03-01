# detector.py
# detector.py

import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppresses TF info/warning logs

import numpy as np
import mediapipe as mp
# ... rest of your imports
import numpy as np
import mediapipe as mp

from config import (
    MAX_FACES,
    DETECTION_CONFIDENCE,
    TRACKING_CONFIDENCE,
    LEFT_EYE_INDICES,
    RIGHT_EYE_INDICES,
)


class FaceEyeDetector:
    """
    Wraps MediaPipe Face Mesh to extract eye landmarks from a BGR frame.
    Designed to be instantiated once and reused across the video loop.
    """

    def __init__(self):
        self._mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self._mp_face_mesh.FaceMesh(
            max_num_faces=MAX_FACES,
            refine_landmarks=True,          # Enables iris landmarks (more precise eye tracking)
            min_detection_confidence=DETECTION_CONFIDENCE,
            min_tracking_confidence=TRACKING_CONFIDENCE,
        )

    def extract_eye_landmarks(self, frame: np.ndarray):
        """
        Process a BGR frame and extract eye landmark coordinates.

        Parameters
        ----------
        frame : np.ndarray
            BGR image from OpenCV.

        Returns
        -------
        tuple (left_eye, right_eye) where each is np.ndarray of shape (6, 2),
        or (None, None) if no face is detected.
        """
        h, w = frame.shape[:2]

        # MediaPipe expects RGB — convert without copying the original frame
        rgb_frame = frame[:, :, ::-1]  # faster than cv2.cvtColor for this case

        results = self.face_mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            return None, None

        # Take the first detected face (driver)
        face_landmarks = results.multi_face_landmarks[0].landmark

        left_eye  = self._get_eye_coords(face_landmarks, LEFT_EYE_INDICES,  w, h)
        right_eye = self._get_eye_coords(face_landmarks, RIGHT_EYE_INDICES, w, h)

        return left_eye, right_eye

    def _get_eye_coords(self, landmarks, indices: list, w: int, h: int) -> np.ndarray:
        """
        Convert normalized MediaPipe landmarks to pixel coordinates.

        MediaPipe returns x, y as fractions of image width/height.
        We multiply by w and h to get actual pixel positions.
        """
        return np.array(
            [[landmarks[i].x * w, landmarks[i].y * h] for i in indices],
            dtype=np.float32,
        )

    def close(self):
        """Release MediaPipe resources cleanly."""
        self.face_mesh.close()


