from unittest.mock import patch, MagicMock
from beemo.config import Config
from beemo.news import get_headlines

MOCK_CONFIG = Config(
    openai_api_key='sk-test', openweathermap_key='owm-test',
    news_api_key='news-test', briefing_time='08:00', news_country='us',
)


def _newsapi_mock():
    m = MagicMock()
    m.json.return_value = {
        'articles': [
            {'title': 'Headline 1'}, {'title': 'Headline 2'},
            {'title': 'Headline 3'}, {'title': 'Headline 4'},
            {'title': 'Headline 5'},
        ]
    }
    m.raise_for_status.return_value = None
    return m


def test_get_headlines_returns_exactly_four():
    with patch('beemo.news.requests.get', return_value=_newsapi_mock()):
        headlines = get_headlines(MOCK_CONFIG)
    assert len(headlines) == 4
    assert headlines[0] == 'Headline 1'
    assert headlines[3] == 'Headline 4'


def test_get_headlines_returns_empty_list_on_failure(capsys):
    with patch('beemo.news.requests.get', side_effect=Exception("fail")):
        headlines = get_headlines(MOCK_CONFIG)
    assert headlines == []
    assert "Couldn't fetch headlines right now" in capsys.readouterr().out
