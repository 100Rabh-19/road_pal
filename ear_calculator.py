# ear_calculator.py

import numpy as np


def euclidean_distance(point1: np.ndarray, point2: np.ndarray) -> float:
    return np.linalg.norm(point1 - point2)


def compute_ear(eye_landmarks: np.ndarray) -> float:
    vertical_1 = euclidean_distance(eye_landmarks[1], eye_landmarks[5])
    vertical_2 = euclidean_distance(eye_landmarks[2], eye_landmarks[4])
    horizontal = euclidean_distance(eye_landmarks[0], eye_landmarks[3])

    if horizontal == 0:
        return 0.0

    ear = (vertical_1 + vertical_2) / (2.0 * horizontal)
    return round(ear, 4)


def compute_average_ear(left_ear: float, right_ear: float) -> float:
    return round((left_ear + right_ear) / 2.0, 4)


if __name__ == "__main__":
    open_eye = np.array([
        [0.0, 0.0],
        [1.0, 1.5],
        [2.0, 1.5],
        [3.0, 0.0],
        [2.0, -1.5],
        [1.0, -1.5],
    ])

    closed_eye = np.array([
        [0.0, 0.0],
        [1.0, 0.1],
        [2.0, 0.1],
        [3.0, 0.0],
        [2.0, -0.1],
        [1.0, -0.1],
    ])

    print(f"Open eye EAR:   {compute_ear(open_eye)}")
    print(f"Closed eye EAR: {compute_ear(closed_eye)}")