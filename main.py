print(">>> main.py V4 <<<")

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

print("[main] Imports starting...")
from ui.main_window import MainWindow
from tasks.scheduler import Scheduler
print("[main] Imports complete.")


def main():
    print("[main] main() entered.")

    app = QApplication(sys.argv)
    app.setApplicationName("Smart Property Management System")

    # Set a clean, modern default font
    default_font = QFont("Segoe UI", 10)
    default_font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(default_font)
    print("[main] QApplication created.")

    try:
        scheduler = Scheduler(run_at_hour=8, run_at_minute=0)
        scheduler.start()
        print("[main] Scheduler started.")
    except Exception as e:
        print(f"[main] Scheduler failed (non-fatal): {e}")
        scheduler = None

    print("[main] Creating MainWindow...")
    window = MainWindow()
    print("[main] MainWindow created. Calling show()...")
    window.show()
    print("[main] show() returned. Entering event loop.")
    print("[main] If the window isn't visible, check Task Manager for python.exe")

    if scheduler is not None:
        app.aboutToQuit.connect(scheduler.stop)

    rc = app.exec()
    print(f"[main] Event loop exited with code {rc}.")
    sys.exit(rc)


if __name__ == "__main__":
    print("[main] __name__ == '__main__', calling main()")
    main()