print(">>> main.py V2 <<<")

import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import MainWindow
from tasks.scheduler import Scheduler


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Smart Property Management System")

    # Start background scheduler (runs ReminderTask daily at 08:00)
    scheduler = Scheduler(run_at_hour=8, run_at_minute=0)
    scheduler.start()

    window = MainWindow()
    window.show()

    # Ensure the scheduler stops when the app exits
    app.aboutToQuit.connect(scheduler.stop)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()