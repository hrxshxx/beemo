import threading
import numpy as np
from unittest.mock import patch, MagicMock
from beemo.wake import WakeDetector


def test_callback_called_when_score_exceeds_threshold():
    mock_model = MagicMock()
    mock_model.predict.return_value = {'hey_jarvis': 0.9}

    mock_stream = MagicMock()
    mock_stream.read.return_value = np.zeros(1280, dtype=np.int16).tobytes()

    mock_pa = MagicMock()
    mock_pa.open.return_value = mock_stream

    fired = threading.Event()

    with patch('beemo.wake.Model', return_value=mock_model), \
         patch('beemo.wake.pyaudio.PyAudio', return_value=mock_pa):
        detector = WakeDetector()
        detector.start(lambda: fired.set())
        fired.wait(timeout=2)

    assert fired.is_set()


def test_prints_fallback_notice_when_custom_model_missing(capsys):
    with patch('beemo.wake.os.path.exists', return_value=False), \
         patch('beemo.wake.Model'):
        WakeDetector(model_path='models/hey_beemo.tflite')
    out = capsys.readouterr().out
    assert 'hey_jarvis' in out or 'fallback' in out.lower()
