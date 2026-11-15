"""One backup per window, with Tk-only completion and bounded retry frequency."""
from time import monotonic
from app.shared.background_task import BackgroundTask, check_cancelled


class BackupCoordinator:
    def __init__(self, owner, on_sent, on_error):
        self.owner, self.on_sent, self.on_error = owner, on_sent, on_error
        self.task = None
        self.closed = False
        self.last_key = None
        self.retry_at = 0
        owner.bind('<Destroy>', self._destroyed, add='+')

    def request(self, key, send):
        if self.closed or (self.task is not None and not self.task.closed):
            return False
        if key == self.last_key and monotonic() < self.retry_at:
            return False
        def work(cancelled, progress):
            check_cancelled(cancelled)
            return send()
        def finished(sent):
            self.last_key, self.retry_at = key, monotonic()+300
            if sent:self.on_sent(key)
        def failed(error):
            self.last_key, self.retry_at = key, monotonic()+300
            self.on_error(error)
        self.task = BackgroundTask(self.owner, work, finished, failed).start()
        return True

    def _destroyed(self, event):
        if event.widget is self.owner:
            self.closed = True
            if self.task is not None:self.task.close()

    def reset_retry(self):
        """New credentials may retry immediately after the next home refresh."""
        self.last_key=None
        self.retry_at=0


