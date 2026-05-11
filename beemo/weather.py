from __future__ import annotations
from datetime import datetime
from urllib.parse import quote
import requests
from beemo.config import Config

_geo_cache: dict = {'city': None, 'fetched_at': None}


def _get_city() -> str:
    now = datetime.now()
    if (
        _geo_cache['city']
        and _geo_cache['fetched_at']
        and (now - _geo_cache['fetched_at']).total_seconds() < 86400
    ):
        return _geo_cache['city']
    resp = requests.get('https://ipapi.co/json/', timeout=5)
    resp.raise_for_status()
    _geo_cache['city'] = resp.json()['city']
    _geo_cache['fetched_at'] = now
    return _geo_cache['city']


def get_weather(config: Config) -> dict | None:
    try:
        city = _get_city()
        url = (
            f'https://api.openweathermap.org/data/2.5/weather'
            f'?q={quote(city)}&appid={config.openweathermap_key}&units=metric'
        )
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return {
            'city': data['name'],
            'temp': data['main']['temp'],
            'condition': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
        }
    except Exception:
        print("Couldn't fetch weather right now")
        return None
