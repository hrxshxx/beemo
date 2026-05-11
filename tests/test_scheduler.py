from unittest.mock import patch, MagicMock
from beemo.config import Config
from beemo.scheduler import Scheduler

MOCK_CONFIG = Config(
    openai_api_key='sk-test', openweathermap_key='owm-test',
    news_api_key='news-test', briefing_time='07:45', news_country='us',
)


def test_job_added_at_configured_hour_and_minute():
    mock_sched = MagicMock()
    with patch('beemo.scheduler.BackgroundScheduler', return_value=mock_sched):
        Scheduler(MOCK_CONFIG).start(MagicMock())
    _, kwargs = mock_sched.add_job.call_args
    assert kwargs.get('hour') == 7
    assert kwargs.get('minute') == 45
    mock_sched.start.assert_called_once()


def test_stop_shuts_down_scheduler():
    mock_sched = MagicMock()
    with patch('beemo.scheduler.BackgroundScheduler', return_value=mock_sched):
        s = Scheduler(MOCK_CONFIG)
        s.start(MagicMock())
        s.stop()
    mock_sched.shutdown.assert_called_once()
