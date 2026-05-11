import pytest
from unittest.mock import patch
from beemo.config import load_config


def test_exits_on_missing_openai_key():
    env = {'OPENWEATHERMAP_KEY': 'owm123', 'NEWS_API_KEY': 'news123'}
    with patch.dict('os.environ', env, clear=True), patch('beemo.config.load_dotenv'):
        with pytest.raises(SystemExit):
            load_config()


def test_exits_on_missing_weather_key():
    env = {'OPENAI_API_KEY': 'sk-123', 'NEWS_API_KEY': 'news123'}
    with patch.dict('os.environ', env, clear=True), patch('beemo.config.load_dotenv'):
        with pytest.raises(SystemExit):
            load_config()


def test_exits_on_missing_news_key():
    env = {'OPENAI_API_KEY': 'sk-123', 'OPENWEATHERMAP_KEY': 'owm123'}
    with patch.dict('os.environ', env, clear=True), patch('beemo.config.load_dotenv'):
        with pytest.raises(SystemExit):
            load_config()


def test_returns_config_with_all_required_keys():
    env = {
        'OPENAI_API_KEY': 'sk-abc',
        'OPENWEATHERMAP_KEY': 'owm-abc',
        'NEWS_API_KEY': 'news-abc',
        'BRIEFING_TIME': '07:30',
        'NEWS_COUNTRY': 'gb',
    }
    with patch.dict('os.environ', env, clear=True), patch('beemo.config.load_dotenv'):
        config = load_config()
    assert config.openai_api_key == 'sk-abc'
    assert config.openweathermap_key == 'owm-abc'
    assert config.news_api_key == 'news-abc'
    assert config.briefing_time == '07:30'
    assert config.news_country == 'gb'


def test_uses_defaults_for_optional_keys():
    env = {'OPENAI_API_KEY': 'sk-abc', 'OPENWEATHERMAP_KEY': 'owm-abc', 'NEWS_API_KEY': 'news-abc'}
    with patch.dict('os.environ', env, clear=True), patch('beemo.config.load_dotenv'):
        config = load_config()
    assert config.briefing_time == '08:00'
    assert config.news_country == 'us'
