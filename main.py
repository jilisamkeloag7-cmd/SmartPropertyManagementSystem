print(">>> main.py V5 <<<")

import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont

print("[main] Imports starting...")
from ui.main_window import MainWindow
from tasks.scheduler import Scheduler
from Services.connectivity_service import is_online
from Database.config import IS_CLOUD
print("[main] Imports complete.")


# --------------------------------------------------------------------- helpers
def _is_connection_error(exc) -> bool:
    """Return True if the exception is a database/network connectivity error."""
    try:
        from sqlalchemy.exc import OperationalError, DBAPIError
    except ImportError:
        return False

    if not isinstance(exc, (OperationalError, DBAPIError)):
        return False

    msg = str(exc).lower()
    keywords = [
        "could not translate host name",
        "name or service not known",
        "connection refused",
        "connection reset",
        "connection timed out",
        "network is unreachable",
        "no route to host",
        "could not connect",
        "server closed the connection",
        "terminating connection",
    ]
    return any(kw in msg for kw in keywords)


def _show_offline_dialog():
    QMessageBox.warning(
        None,
        "No Internet Connection",
        "The application cannot reach the server.\n\n"
        "Please check your internet connection and try again.",
    )


def _install_exception_hook():
    """
    Replace sys.excepthook so that unhandled connection errors
    show a friendly dialog instead of a Python traceback.
    """
    def hook(exc_type, exc_value, exc_tb):
        if _is_connection_error(exc_value):
            _show_offline_dialog()
            return
        # Default behaviour for non-connection errors
        sys.__excepthook__(exc_type, exc_value, exc_tb)

    sys.excepthook = hook


# --------------------------------------------------------------------- entry
def main():
    print("[main] main() entered.")

    app = QApplication(sys.argv)
    app.setApplicationName("Smart Property Management System")

    default_font = QFont("Segoe UI", 10)
    app.setFont(default_font)
    print("[main] QApplication created.")

    # Install our exception handler BEFORE any UI runs
    _install_exception_hook()

    # ---- Startup connectivity check (cloud mode only)
    if IS_CLOUD and not is_online():
        print("[main] Startup: no internet detected.")
        QMessageBox.critical(
            None,
            "No Internet Connection",
            "This application requires an internet connection to run.\n\n"
            "Please connect to the internet and restart the application.",
        )
        sys.exit(1)
    print("[main] Startup connectivity check passed.")

    # ---- Scheduler (best-effort, non-fatal)
    try:
        scheduler = Scheduler(run_at_hour=8, run_at_minute=0)
        scheduler.start()
        print("[main] Scheduler started.")
    except Exception as e:
        print(f"[main] Scheduler failed (non-fatal): {e}")
        scheduler = None

    # ---- Main window
    print("[main] Creating MainWindow...")
    window = MainWindow()
    print("[main] MainWindow created. Calling show()...")
    window.show()
    print("[main] show() returned. Entering event loop.")

    if scheduler is not None:
        app.aboutToQuit.connect(scheduler.stop)

    rc = app.exec()
    print(f"[main] Event loop exited with code {rc}.")
    sys.exit(rc)


if __name__ == "__main__":
    print("[main] __name__ == '__main__', calling main()")
    main()