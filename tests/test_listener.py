import struct
from unittest.mock import patch, MagicMock
from beemo.config import Config
from beemo.listener import Listener, _rms

MOCK_CONFIG = Config(
    openai_api_key='sk-test', openweathermap_key='owm-test',
    news_api_key='news-test', briefing_time='08:00', news_country='us',
)


def test_rms_returns_zero_for_silence():
    assert _rms(struct.pack('4h', 0, 0, 0, 0)) == 0.0


def test_rms_returns_positive_for_audio():
    assert _rms(struct.pack('4h', 1000, -1000, 1000, -1000)) == 1000.0


def test_listen_returns_transcript_on_success():
    loud = struct.pack('1024h', *([2000] * 1024))
    silent = struct.pack('1024h', *([0] * 1024))

    mock_stream = MagicMock()
    mock_stream.read.side_effect = [loud] * 3 + [silent] * 20

    mock_pa = MagicMock()
    mock_pa.open.return_value = mock_stream
    mock_pa.get_sample_size.return_value = 2

    mock_transcript = MagicMock()
    mock_transcript.text = 'play some music'

    listener = Listener(MOCK_CONFIG)

    with patch('beemo.listener.pyaudio.PyAudio', return_value=mock_pa), \
         patch('beemo.listener.wave.open', MagicMock()), \
         patch('builtins.open', MagicMock()), \
         patch('beemo.listener.os.unlink'), \
         patch('beemo.listener.tempfile.NamedTemporaryFile') as mock_tmp, \
         patch.object(listener._client.audio.transcriptions, 'create', return_value=mock_transcript):
        mock_tmp.return_value.__enter__.return_value.name = '/tmp/test.wav'
        result = listener.listen()

    assert result == 'play some music'


def test_listen_returns_empty_string_on_whisper_failure(capsys):
    loud = struct.pack('1024h', *([2000] * 1024))
    mock_stream = MagicMock()
    mock_stream.read.return_value = loud

    mock_pa = MagicMock()
    mock_pa.open.return_value = mock_stream
    mock_pa.get_sample_size.return_value = 2

    listener = Listener(MOCK_CONFIG)

    with patch('beemo.listener.pyaudio.PyAudio', return_value=mock_pa), \
         patch('beemo.listener.wave.open', MagicMock()), \
         patch('builtins.open', MagicMock()), \
         patch('beemo.listener.os.unlink'), \
         patch('beemo.listener.tempfile.NamedTemporaryFile') as mock_tmp, \
         patch.object(listener._client.audio.transcriptions, 'create', side_effect=Exception("fail")):
        mock_tmp.return_value.__enter__.return_value.name = '/tmp/test.wav'
        result = listener.listen()

    assert result == ''
    assert "couldn't process" in capsys.readouterr().out.lower()
