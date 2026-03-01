CAMERA_INDEX = 0          # 0 = default webcam. Change to 1 if you have multiple cameras.
FRAME_WIDTH  = 640
FRAME_HEIGHT = 480

# ── EAR (Eye Aspect Ratio) ────────────────────────────────────────────────────
EAR_THRESHOLD       = 0.22   # Below this value, eye is considered closed
CONSECUTIVE_FRAMES  = 20     # Frames eye must stay closed to trigger drowsiness alert
                             # At 30fps → ~0.67 seconds

# ── MediaPipe Face Mesh ───────────────────────────────────────────────────────
MAX_FACES            = 1     # We only care about the driver
DETECTION_CONFIDENCE = 0.7
TRACKING_CONFIDENCE  = 0.7

# ── MediaPipe Eye Landmark Indices ────────────────────────────────────────────
# These are the 6 landmark indices per eye used for EAR calculation.
# Sourced from MediaPipe's canonical face mesh topology.
LEFT_EYE_INDICES  = [362, 385, 387, 263, 373, 380]
RIGHT_EYE_INDICES = [33,  160, 158, 133, 153, 144]

# ── Alert ─────────────────────────────────────────────────────────────────────
ALERT_TEXT       = "DROWSINESS ALERT!"
ALERT_COLOR_BGR  = (0, 0, 255)    # Red in BGR
NORMAL_COLOR_BGR = (0, 255, 0)    # Green in BGR

# ── Display ───────────────────────────────────────────────────────────────────
FONT            = 0   # cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE      = 0.7
FONT_THICKNESS  = 2