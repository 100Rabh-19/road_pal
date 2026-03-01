# drowsiness_monitor.py

from config import EAR_THRESHOLD, CONSECUTIVE_FRAMES


class DrowsinessMonitor:
    """
    Stateful monitor that tracks eye closure duration across frames.

    This is intentionally separated from EAR calculation —
    the monitor doesn't care HOW the EAR was computed,
    only what the value is and for how long it stays low.
    """

    def __init__(self):
        self.frame_counter  = 0      # Consecutive frames below EAR threshold
        self.is_drowsy      = False  # Current drowsiness state
        self.total_alerts   = 0      # Total drowsiness events this session

    def update(self, ear: float) -> bool:
        """
        Update monitor state based on current EAR value.

        Parameters
        ----------
        ear : float
            Averaged EAR value for the current frame.

        Returns
        -------
        bool
            True if drowsiness is currently detected, False otherwise.
        """
        if ear < EAR_THRESHOLD:
            self.frame_counter += 1

            if self.frame_counter >= CONSECUTIVE_FRAMES:
                # Only count a new alert event on the transition
                if not self.is_drowsy:
                    self.total_alerts += 1

                self.is_drowsy = True
        else:
            # Eye opened back up — reset
            self.frame_counter = 0
            self.is_drowsy     = False

        return self.is_drowsy

    def get_status(self) -> dict:
        """
        Return current monitor state as a dictionary.
        Useful for logging, display, or future dashboard integration.
        """
        return {
            "is_drowsy"     : self.is_drowsy,
            "frame_counter" : self.frame_counter,
            "total_alerts"  : self.total_alerts,
            "frames_to_alert": max(0, CONSECUTIVE_FRAMES - self.frame_counter),
        }

    def reset(self):
        """Full reset — useful if driver identity changes or session restarts."""
        self.frame_counter = 0
        self.is_drowsy     = False
        self.total_alerts  = 0


if __name__ == "__main__":
    monitor = DrowsinessMonitor()

    # Simulate 25 frames of closed eyes
    for i in range(25):
        result = monitor.update(0.18)  # Below threshold
        print(f"Frame {i+1:02d} | Drowsy: {result} | Counter: {monitor.frame_counter}")

    print("\n--- Eye opens ---\n")

    # Simulate eye opening
    for i in range(3):
        result = monitor.update(0.35)  # Above threshold
        print(f"Frame {i+1:02d} | Drowsy: {result} | Counter: {monitor.frame_counter}")

    print(f"\nTotal alerts this session: {monitor.total_alerts}")
# ### Why `frames_to_alert` matters

# In a real system you'd use this to show a **progressive warning** — a yellow indicator before the red alert fires. For example:
# ```
# 0–10 frames below threshold  →  green  (normal)
# 10–19 frames below threshold →  yellow (warning)
# 20+ frames below threshold   →  red    (alert)