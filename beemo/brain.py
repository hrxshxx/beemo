from __future__ import annotations
import json
import openai
from beemo.config import Config

_SYSTEM_PROMPT = """You are Beemo, a friendly local AI assistant. Given a user message, respond helpfully and return a JSON object with exactly these fields:
- "intent": one of "weather", "news", "music", "music_stop", "search", "chat"
- "query": the search query if intent is "search", the song/artist name if intent is "music", otherwise an empty string
- "response": your short, friendly text response to the user

Intent rules:
- "weather": user asks about weather, temperature, forecast, or conditions outside
- "news": user asks about news, headlines, or current events
- "music": user asks to play a song or names a song/artist to play
- "music_stop": user asks to stop, pause, or quiet the music
- "search": user asks anything that requires real-time or factual information — current events, people, places, how-to questions, recent scores, prices, definitions, or anything you're not certain about
- "chat": casual conversation, greetings, opinions, or things you can answer confidently without needing to look up

Return ONLY valid JSON. No markdown, no code fences, no extra text."""


class Brain:
    def __init__(self, config: Config):
        self._client = openai.OpenAI(
            api_key='ollama',
            base_url='http://localhost:11434/v1',
        )

    def process(self, text: str, history: list | None = None) -> dict:
        messages = [{'role': 'system', 'content': _SYSTEM_PROMPT}]
        if history:
            messages.extend(history)
        messages.append({'role': 'user', 'content': text})
        try:
            response = self._client.chat.completions.create(
                model='llama3.2',
                messages=messages,
                response_format={'type': 'json_object'},
                temperature=0.7,
            )
            return json.loads(response.choices[0].message.content)
        except Exception as exc:
            msg = str(exc).lower()
            if 'connection' in msg or 'refused' in msg or 'connect' in msg:
                return {
                    'intent': 'chat',
                    'query': '',
                    'response': "Ollama isn't running — start it with: ollama serve",
                }
            return {
                'intent': 'chat',
                'query': '',
                'response': "Beemo couldn't process that, try again.",
            }
