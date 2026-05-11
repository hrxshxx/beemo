from __future__ import annotations
import requests
from beemo.config import Config


def get_headlines(config: Config) -> list[str]:
    try:
        url = (
            f'https://newsapi.org/v2/top-headlines'
            f'?country={config.news_country}&pageSize=4&apiKey={config.news_api_key}'
        )
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        articles = resp.json().get('articles', [])
        return [a['title'] for a in articles[:4]]
    except Exception:
        print("Couldn't fetch headlines right now")
        return []
