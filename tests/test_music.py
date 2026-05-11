from unittest.mock import patch, MagicMock
from beemo.music import MusicPlayer


def _ytdlp_result(url='https://youtube.com/fake-stream'):
    m = MagicMock()
    m.stdout = url + '\n'
    m.returncode = 0
    return m


def test_play_passes_query_to_ytdlp():
    with patch('beemo.music.subprocess.run', return_value=_ytdlp_result()) as mock_run, \
         patch('beemo.music.subprocess.Popen'):
        MusicPlayer().play('Bohemian Rhapsody')
    args = mock_run.call_args[0][0]
    assert args[0] == 'yt-dlp'
    assert 'ytsearch1:Bohemian Rhapsody' in args


def test_play_starts_mpv_with_extracted_url():
    url = 'https://youtube.com/fake-stream'
    with patch('beemo.music.subprocess.run', return_value=_ytdlp_result(url)), \
         patch('beemo.music.subprocess.Popen') as mock_popen:
        MusicPlayer().play('some song')
    args = mock_popen.call_args[0][0]
    assert 'mpv' in args
    assert url in args


def test_stop_terminates_running_process():
    with patch('beemo.music.subprocess.run', return_value=_ytdlp_result()), \
         patch('beemo.music.subprocess.Popen') as mock_popen:
        mock_proc = MagicMock()
        mock_proc.poll.return_value = None
        mock_popen.return_value = mock_proc
        player = MusicPlayer()
        player.play('some song')
        player.stop()
    mock_proc.terminate.assert_called_once()


def test_play_prints_error_when_mpv_missing(capsys):
    with patch('beemo.music.subprocess.run', return_value=_ytdlp_result()), \
         patch('beemo.music.subprocess.Popen', side_effect=FileNotFoundError):
        MusicPlayer().play('some song')
    assert 'brew install mpv' in capsys.readouterr().out


def test_play_prints_error_when_ytdlp_missing(capsys):
    with patch('beemo.music.subprocess.run', side_effect=FileNotFoundError):
        MusicPlayer().play('some song')
    assert 'yt-dlp' in capsys.readouterr().out
