# alert.py

import winsound
import threading
from config import ALERT_TEXT, ALERT_COLOR_BGR


class AlertSystem:
    """
    Handles audio and visual alert triggering.

    Audio runs in a separate thread so it never blocks the video loop.
    A blocked video loop means dropped frames — unacceptable in a safety system.
    """

    def __init__(self):
        self._audio_playing = False  # Guard to prevent overlapping beeps

    def trigger(self):
        """
        Call this every frame when drowsiness is detected.
        Handles both audio and returns visual alert data.
        """
        self._play_audio_async()
        return {
            "text"  : ALERT_TEXT,
            "color" : ALERT_COLOR_BGR,
        }

    def _play_audio_async(self):
        """
        Play alert beep in a background thread.
        Without threading, winsound.Beep() blocks for its full duration,
        freezing the video feed.
        """
        if not self._audio_playing:
            thread = threading.Thread(target=self._beep, daemon=True)
            thread.start()

    def _beep(self):
        """1000Hz beep for 500ms — loud enough to wake a drowsy driver."""
        self._audio_playing = True
        winsound.Beep(1000, 500)
        self._audio_playing = False

    def silence(self):
        """
        Called when drowsiness state clears.
        Currently a no-op for beep-based alerts but important
        for future continuous alarm implementations.
        """
        self._audio_playing = False

    if __name__ == "__main__":
        import time
        alert = AlertSystem()

        print("Triggering alert...")
        data = alert.trigger()
        print(f"Visual data: {data}")

        time.sleep(1)  # Let the beep finish
        print("Done.")