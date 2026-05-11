from __future__ import annotations
from typing import Callable
from apscheduler.schedulers.background import BackgroundScheduler
from beemo.config import Config


class Scheduler:
    def __init__(self, config: Config):
        self._config = config
        self._scheduler = BackgroundScheduler()

    def start(self, job_fn: Callable) -> None:
        hour, minute = map(int, self._config.briefing_time.split(':'))
        self._scheduler.add_job(job_fn, 'cron', hour=hour, minute=minute)
        self._scheduler.start()

    def stop(self) -> None:
        self._scheduler.shutdown()
