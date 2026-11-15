"""Bounded, process-local cache of CSV-derived statistics, never Tk objects."""
from collections import OrderedDict
from copy import deepcopy
from pathlib import Path
from threading import RLock


class StatisticsCache:
    def __init__(self, limit=12):
        self._lock = RLock()
        self.limit = limit
        self._entries = OrderedDict()

    @staticmethod
    def _revision(path):
        info = path.stat()
        return info.st_mtime_ns, info.st_ctime_ns, info.st_size, info.st_ino

    def get(self, path, namespace, options, calculate):
        with self._lock:
            return self._get(path, namespace, options, calculate)

    def _get(self, path, namespace, options, calculate):
        path = Path(path).resolve()
        key = (str(path), namespace, options)
        revision = self._revision(path)
        entry = self._entries.get(key)
        if entry is not None and entry[0] == revision:
            self._entries.move_to_end(key)
            return deepcopy(entry[1])
        # Do not publish a snapshot read while another process was changing it.
        for attempt in range(2):
            value = calculate(path)
            after = self._revision(path)
            if after == revision:
                self._entries[key] = (revision, value)
                self._entries.move_to_end(key)
                while len(self._entries) > self.limit:
                    self._entries.popitem(last=False)
                return deepcopy(value)
            revision = after
        raise OSError('Statistics source changed while reading. Please reopen statistics.')


cache = StatisticsCache()
