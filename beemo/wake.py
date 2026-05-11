from __future__ import annotations
import os
import time
import threading
from typing import Callable
import numpy as np
import pyaudio
from openwakeword.model import Model

CHUNK = 1280
RATE = 16000
THRESHOLD = 0.5


class WakeDetector:
    def __init__(self, model_path: str | None = None):
        if model_path and os.path.exists(model_path):
            models = [model_path]
        else:
            if model_path:
                print("[Beemo] Custom wake word model not found, using hey_jarvis as fallback.")
            models = ['hey_jarvis']
        self._model = Model(wakeword_models=models, inference_framework='onnx')
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self, callback: Callable) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._listen_loop, args=(callback,), daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def _listen_loop(self, callback: Callable) -> None:
        pa = pyaudio.PyAudio()
        stream = pa.open(
            format=pyaudio.paInt16, channels=1, rate=RATE,
            input=True, frames_per_buffer=CHUNK,
        )
        try:
            while not self._stop_event.is_set():
                audio = np.frombuffer(
                    stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16,
                )
                predictions = self._model.predict(audio)
                for score in predictions.values():
                    if score > THRESHOLD:
                        callback()
                        time.sleep(1.5)
                        break
        finally:
            stream.stop_stream()
            stream.close()
            pa.terminate()
