from __future__ import annotations
import json
import openai
from beemo.config import Config

_SYSTEM_PROMPT = """You are Beemo, a friendly local AI assistant. Given a user message, respond helpfully and return a JSON object with exactly these fields:
- "intent": one of "weather", "news", "music", "music_stop", "chat"
- "query": the song or artist name if intent is "music", otherwise an empty string
- "response": your short, friendly text response to the user

Intent rules:
- "weather": user asks about weather, temperature, forecast, or conditions outside
- "news": user asks about news, headlines, or current events
- "music": user asks to play a song or names a song/artist to play
- "music_stop": user asks to stop, pause, or quiet the music
- "chat": everything else

Return ONLY valid JSON. No markdown, no code fences, no extra text."""


class Brain:
    def __init__(self, config: Config):
        self._client = openai.OpenAI(api_key=config.openai_api_key)

    def process(self, text: str) -> dict:
        try:
            response = self._client.chat.completions.create(
                model='gpt-4o',
                messages=[
                    {'role': 'system', 'content': _SYSTEM_PROMPT},
                    {'role': 'user', 'content': text},
                ],
                response_format={'type': 'json_object'},
                temperature=0.7,
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {
                'intent': 'chat',
                'query': '',
                'response': "Beemo couldn't process that, try again.",
            }
