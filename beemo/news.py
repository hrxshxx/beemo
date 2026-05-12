from __future__ import annotations
import requests
from beemo.config import Config


def get_headlines(config: Config) -> list[str]:
    try:
        url = (
            f'https://newsdata.io/api/1/news'
            f'?country={config.news_country}&language=en&apikey={config.news_api_key}'
        )
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        articles = resp.json().get('results', [])
        return [a['title'] for a in articles[:4]]
    except Exception:
        print("Couldn't fetch headlines right now")
        return []
