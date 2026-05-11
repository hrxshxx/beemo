from unittest.mock import MagicMock
from beemo.core import Core


def _make_core():
    return Core(
        config=MagicMock(),
        brain=MagicMock(),
        weather=MagicMock(),
        news=MagicMock(),
        music=MagicMock(),
        scheduler=MagicMock(),
        wake=MagicMock(),
        listener=MagicMock(),
    )


def test_weather_intent_calls_get_weather_and_prints_city(capsys):
    core = _make_core()
    core._brain.process.return_value = {'intent': 'weather', 'query': '', 'response': 'Checking!'}
    core._weather.get_weather.return_value = {
        'city': 'Chennai', 'temp': 32.0, 'condition': 'sunny', 'humidity': 70,
    }
    core._handle('what is the weather?')
    core._weather.get_weather.assert_called_once_with(core._config)
    assert 'Chennai' in capsys.readouterr().out


def test_news_intent_calls_get_headlines_and_prints_them(capsys):
    core = _make_core()
    core._brain.process.return_value = {'intent': 'news', 'query': '', 'response': 'Headlines!'}
    core._news.get_headlines.return_value = ['H1', 'H2', 'H3', 'H4']
    core._handle('what is in the news?')
    core._news.get_headlines.assert_called_once_with(core._config)
    assert 'H1' in capsys.readouterr().out


def test_music_intent_calls_play_with_query():
    core = _make_core()
    core._brain.process.return_value = {
        'intent': 'music', 'query': 'Bohemian Rhapsody', 'response': 'Playing!',
    }
    core._handle('play Bohemian Rhapsody')
    core._music.play.assert_called_once_with('Bohemian Rhapsody')


def test_music_stop_intent_calls_stop():
    core = _make_core()
    core._brain.process.return_value = {'intent': 'music_stop', 'query': '', 'response': 'Stopping.'}
    core._handle('stop the music')
    core._music.stop.assert_called_once()


def test_chat_intent_prints_response(capsys):
    core = _make_core()
    core._brain.process.return_value = {'intent': 'chat', 'query': '', 'response': 'Hello there!'}
    core._handle('hello')
    assert 'Hello there!' in capsys.readouterr().out
