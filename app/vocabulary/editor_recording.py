"""Microphone capture to an atomically replaced WAV; no GUI operations."""
from pathlib import Path
import os
import tempfile
import wave
import pyaudio


def record_wave(destination,stop_event):
    destination=Path(destination)
    audio=pyaudio.PyAudio()
    stream=None
    temporary=None
    try:
        sample_width=audio.get_sample_size(pyaudio.paInt16)
        stream=audio.open(format=pyaudio.paInt16,channels=2,rate=44100,input=True,frames_per_buffer=1024)
        destination.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w+b', dir=destination.parent,
                                         suffix='.wav.tmp', delete=False) as output:
            temporary=Path(output.name)
            captured=0
            with wave.open(output,'wb') as file:
                file.setnchannels(2)
                file.setsampwidth(sample_width)
                file.setframerate(44100)
                while not stop_event.is_set():
                    chunk=stream.read(1024,exception_on_overflow=False)
                    file.writeframesraw(chunk)
                    captured += len(chunk)
                if not captured:
                    raise ValueError("No recording captured")
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary,destination)
    finally:
        try:
            if stream is not None:
                try:
                    stream.stop_stream()
                finally:
                    stream.close()
        finally:
            try:
                audio.terminate()
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
