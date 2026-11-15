"""Pooled HTTP requests and atomic streamed audio downloads."""
import atexit
import os
import tempfile
from pathlib import Path
import requests

REQUEST_TIMEOUT = (5, 30)
SESSION = requests.Session()
atexit.register(SESSION.close)


def get_entries(url, **options):
    with SESSION.get(url, timeout=REQUEST_TIMEOUT, **options) as response:
        if response.status_code == 404:
            return []
        response.raise_for_status()
        payload = response.json()
    # Dictionary services may return spelling suggestions instead of entries.
    if not isinstance(payload, list):
        return []
    return [entry for entry in payload if isinstance(entry, dict)]


def download_audio(url, destination, *, method="GET", **options):
    """Keep the previous file on HTTP errors, empty bodies or interrupted streams.

    POSTs are never automatically retried because they may incur charges.
    """
    destination = Path(destination)
    temporary = None
    try:
        with SESSION.request(method, url, timeout=REQUEST_TIMEOUT, stream=True, **options) as response:
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "").lower()
            if "json" in content_type or "text/html" in content_type:
                raise ValueError("Audio service returned a non-audio response")
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="wb", dir=destination.parent,
                    prefix=destination.name + ".", suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
                length = 0
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        stream.write(chunk)
                        length += len(chunk)
                if not length:
                    raise ValueError("Audio service returned an empty response")
                stream.flush()
                os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
