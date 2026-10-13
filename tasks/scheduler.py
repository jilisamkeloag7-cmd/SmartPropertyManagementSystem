
import threading
import time
from datetime import datetime, timedelta
from tasks.reminder_task import ReminderTask


class Scheduler:
    """
    Minimal in-process scheduler. Runs ReminderTask daily at the configured time.
    """

    def __init__(self, run_at_hour: int = 8, run_at_minute: int = 0):
        self.run_at_hour = run_at_hour
        self.run_at_minute = run_at_minute
        self._stop_event = threading.Event()
        self._thread = None
        self._task = ReminderTask()

    def _next_run(self) -> datetime:
        now = datetime.now()
        target = now.replace(
            hour=self.run_at_hour, minute=self.run_at_minute,
            second=0, microsecond=0,
        )
        if target <= now:
            target += timedelta(days=1)
        return target

    def _loop(self):
        while not self._stop_event.is_set():
            target = self._next_run()
            wait_seconds = (target - datetime.now()).total_seconds()
            # Sleep in 1-second steps so stop() is responsive
            while wait_seconds > 0 and not self._stop_event.is_set():
                step = min(1.0, wait_seconds)
                time.sleep(step)
                wait_seconds -= step
            if self._stop_event.is_set():
                break
            try:
                self._task.run()
            except Exception as e:
                print(f"[scheduler] task error: {e}")

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print(f"[scheduler] started — daily run at {self.run_at_hour:02d}:{self.run_at_minute:02d}")

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=3)
        print("[scheduler] stopped")

    def run_now(self):
        """Trigger the reminder task immediately (useful for demos/testing)."""
        try:
            self._task.run()
        except Exception as e:
            print(f"[scheduler] run_now error: {e}")
            
