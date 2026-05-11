from unittest.mock import patch, MagicMock
from beemo.config import Config
from beemo.weather import get_weather

MOCK_CONFIG = Config(
    openai_api_key='sk-test', openweathermap_key='owm-test',
    news_api_key='news-test', briefing_time='08:00', news_country='us',
)


def _ipapi_mock():
    m = MagicMock()
    m.json.return_value = {'city': 'Chennai'}
    m.raise_for_status.return_value = None
    return m


def _owm_mock():
    m = MagicMock()
    m.json.return_value = {
        'main': {'temp': 32.5, 'humidity': 78},
        'weather': [{'description': 'clear sky'}],
        'name': 'Chennai',
    }
    m.raise_for_status.return_value = None
    return m


def test_get_weather_returns_correct_fields():
    with patch('beemo.weather._geo_cache', {'city': None, 'fetched_at': None}), \
         patch('beemo.weather.requests.get') as mock_get:
        mock_get.side_effect = [_ipapi_mock(), _owm_mock()]
        result = get_weather(MOCK_CONFIG)
    assert result['city'] == 'Chennai'
    assert result['temp'] == 32.5
    assert result['condition'] == 'clear sky'
    assert result['humidity'] == 78


def test_get_weather_returns_none_on_api_failure(capsys):
    with patch('beemo.weather._geo_cache', {'city': None, 'fetched_at': None}), \
         patch('beemo.weather.requests.get', side_effect=Exception("Network error")):
        result = get_weather(MOCK_CONFIG)
    assert result is None
    assert "Couldn't fetch weather right now" in capsys.readouterr().out
