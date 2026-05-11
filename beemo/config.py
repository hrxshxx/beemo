import os
import sys
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Config:
    openai_api_key: str
    openweathermap_key: str
    news_api_key: str
    briefing_time: str
    news_country: str


def load_config() -> Config:
    load_dotenv()
    required = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
        'OPENWEATHERMAP_KEY': os.getenv('OPENWEATHERMAP_KEY', ''),
        'NEWS_API_KEY': os.getenv('NEWS_API_KEY', ''),
    }
    for key, val in required.items():
        if not val:
            print(f"Missing required environment variable: {key}", file=sys.stderr)
            sys.exit(1)
    briefing_time = os.getenv('BRIEFING_TIME', '08:00')
    try:
        h, m = briefing_time.split(':')
        int(h)
        int(m)
    except (ValueError, AttributeError):
        print(f"BRIEFING_TIME must be HH:MM, got: {briefing_time!r}", file=sys.stderr)
        sys.exit(1)
    return Config(
        openai_api_key=required['OPENAI_API_KEY'],
        openweathermap_key=required['OPENWEATHERMAP_KEY'],
        news_api_key=required['NEWS_API_KEY'],
        briefing_time=briefing_time,
        news_country=os.getenv('NEWS_COUNTRY', 'us'),
    )
