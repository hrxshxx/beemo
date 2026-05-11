import json
from unittest.mock import patch, MagicMock
from beemo.config import Config
from beemo.brain import Brain

MOCK_CONFIG = Config(
    openai_api_key='sk-test', openweathermap_key='owm-test',
    news_api_key='news-test', briefing_time='08:00', news_country='us',
)


def _openai_mock(intent, query='', response='OK'):
    payload = json.dumps({'intent': intent, 'query': query, 'response': response})
    msg = MagicMock()
    msg.content = payload
    choice = MagicMock()
    choice.message = msg
    resp = MagicMock()
    resp.choices = [choice]
    return resp


def test_process_weather_intent():
    brain = Brain(MOCK_CONFIG)
    with patch.object(brain._client.chat.completions, 'create',
                      return_value=_openai_mock('weather', response="It's warm!")):
        result = brain.process("what's the weather?")
    assert result['intent'] == 'weather'
    assert result['response'] == "It's warm!"


def test_process_news_intent():
    brain = Brain(MOCK_CONFIG)
    with patch.object(brain._client.chat.completions, 'create',
                      return_value=_openai_mock('news', response='Headlines!')):
        result = brain.process("what's in the news?")
    assert result['intent'] == 'news'


def test_process_music_intent_with_query():
    brain = Brain(MOCK_CONFIG)
    with patch.object(brain._client.chat.completions, 'create',
                      return_value=_openai_mock('music', query='Bohemian Rhapsody', response='Playing!')):
        result = brain.process("play Bohemian Rhapsody")
    assert result['intent'] == 'music'
    assert result['query'] == 'Bohemian Rhapsody'


def test_process_music_stop_intent():
    brain = Brain(MOCK_CONFIG)
    with patch.object(brain._client.chat.completions, 'create',
                      return_value=_openai_mock('music_stop', response='Stopping.')):
        result = brain.process("stop the music")
    assert result['intent'] == 'music_stop'


def test_process_chat_intent():
    brain = Brain(MOCK_CONFIG)
    with patch.object(brain._client.chat.completions, 'create',
                      return_value=_openai_mock('chat', response='Hello!')):
        result = brain.process("hello beemo")
    assert result['intent'] == 'chat'


def test_process_returns_safe_fallback_on_openai_failure():
    brain = Brain(MOCK_CONFIG)
    with patch.object(brain._client.chat.completions, 'create', side_effect=Exception("API error")):
        result = brain.process("something")
    assert result['intent'] == 'chat'
    assert "couldn't process" in result['response'].lower()
