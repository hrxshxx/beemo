from __future__ import annotations
import math
import os
import struct
import tempfile
import wave
import pyaudio
import openai
from beemo.config import Config

CHUNK = 1024
RATE = 16000
FORMAT = pyaudio.paInt16
CHANNELS = 1
SILENCE_THRESHOLD = 500
SILENCE_CHUNKS = 15
MAX_SECONDS = 8


def _rms(data: bytes) -> float:
    count = len(data) // 2
    if count == 0:
        return 0.0
    shorts = struct.unpack(f'{count}h', data)
    return math.sqrt(sum(s * s for s in shorts) / count)


class Listener:
    def __init__(self, config: Config):
        self._client = openai.OpenAI(api_key=config.openai_api_key)

    def listen(self) -> str:
        pa = pyaudio.PyAudio()
        sample_width = pa.get_sample_size(FORMAT)
        stream = pa.open(
            format=FORMAT, channels=CHANNELS, rate=RATE,
            input=True, frames_per_buffer=CHUNK,
        )
        frames: list[bytes] = []
        silent_chunks = 0
        max_chunks = (RATE // CHUNK) * MAX_SECONDS

        for _ in range(max_chunks):
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            if _rms(data) < SILENCE_THRESHOLD:
                silent_chunks += 1
                if silent_chunks >= SILENCE_CHUNKS:
                    break
            else:
                silent_chunks = 0

        stream.stop_stream()
        stream.close()
        pa.terminate()

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            tmp_path = f.name

        with wave.open(tmp_path, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(sample_width)
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        try:
            with open(tmp_path, 'rb') as f:
                transcript = self._client.audio.transcriptions.create(
                    model='whisper-1', file=f,
                )
            return transcript.text
        except Exception:
            print("Beemo couldn't process that, try again")
            return ''
        finally:
            os.unlink(tmp_path)
