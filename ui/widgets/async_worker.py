
from PySide6.QtCore import QObject, QThread, Signal


class Worker(QObject):
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def run(self):
        try:
            result = self._func(*self._args, **self._kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(f"{type(e).__name__}: {e}")


class AsyncRunner(QObject):
    """
    Runs a function on a background thread and returns the result to the UI thread.

    Usage:
        self._async = AsyncRunner(self)
        self._async.run(
            self.controller.list, filters,
            on_done=self._on_loaded,
            on_error=self._on_error,
        )
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._threads = []   # keep references so GC doesn't kill them

    def run(self, func, *args, on_done=None, on_error=None, **kwargs):
        thread = QThread()
        worker = Worker(func, *args, **kwargs)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)

        if on_done:
            worker.finished.connect(on_done)
        if on_error:
            worker.error.connect(on_error)

        worker.finished.connect(thread.quit)
        worker.error.connect(thread.quit)
        thread.finished.connect(thread.deleteLater)

        self._threads.append(thread)
        thread.finished.connect(lambda: self._threads.remove(thread) if thread in self._threads else None)

        thread.start()
