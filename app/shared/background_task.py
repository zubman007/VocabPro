"""One worker thread, with progress and completion delivered only by Tk polling."""
from concurrent.futures import CancelledError
from queue import Empty, Queue
from threading import Event, Thread


class BackgroundTask:
    def __init__(self, owner, work, on_success, on_error, on_progress=None):
        self.owner, self.on_success, self.on_error = owner, on_success, on_error
        self.on_progress = on_progress
        self.cancelled = Event()
        self.results = Queue(maxsize=1)
        self.progress = None
        self._last_progress = None
        self._timer = None
        self.closed = False
        self.thread = Thread(target=self._run, args=(work,), daemon=True)

    def start(self):
        self.thread.start()
        self._timer = self.owner.after(60, self._poll)
        return self

    def _run(self, work):
        try:
            value = work(self.cancelled, self._progress)
        except Exception as error:
            error.__traceback__ = None
            self.results.put((False, error))
        else:
            self.results.put((True, value))

    def _progress(self, completed, total):
        self.progress = (completed, total)

    def _poll(self):
        self._timer = None
        if self.closed:
            return
        if self.on_progress and self.progress != self._last_progress and self.progress is not None:
            self._last_progress = self.progress
            self.on_progress(*self.progress)
        if self.closed:return
        try:
            success, value = self.results.get_nowait()
        except Empty:
            self._timer = self.owner.after(60, self._poll)
            return
        self.closed = True
        (self.on_success if success else self.on_error)(value)

    def cancel(self):
        self.cancelled.set()

    def close(self):
        self.cancel()
        self.closed = True
        if self._timer is not None:
            self.owner.after_cancel(self._timer)
            self._timer = None


def check_cancelled(event):
    if event is not None and event.is_set():
        raise CancelledError()
