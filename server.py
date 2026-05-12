from __future__ import annotations

import os
import tempfile
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from beemo.brain import Brain
from beemo.config import load_config
from beemo import weather as weather_mod
from beemo import news as news_mod
from beemo import search as search_mod
from beemo.music import MusicPlayer
from beemo.scheduler import Scheduler

config = load_config()
_brain = Brain(config)
_music = MusicPlayer()
_history: list[dict] = []  # conversation history, kept in memory

UI_DIR = Path(__file__).parent / 'beemo ui'


def _morning_briefing() -> None:
    info = weather_mod.get_weather(config)
    headlines = news_mod.get_headlines(config)
    print('\n[Beemo] Good morning! Briefing:')
    if info:
        print(f'  Weather: {info["city"]} — {info["temp"]:.1f}°C, {info["condition"]}, {info["humidity"]}% humidity')
    for i, h in enumerate(headlines, 1):
        print(f'  {i}. {h}')


app = FastAPI()


class ChatRequest(BaseModel):
    text: str


@app.get('/')
async def index() -> FileResponse:
    return FileResponse(str(UI_DIR / 'Beemo.html'))


@app.post('/api/chat')
async def chat(req: ChatRequest) -> JSONResponse:
    result = _brain.process(req.text, _history)
    _history.append({'role': 'user', 'content': req.text})
    _history.append({'role': 'assistant', 'content': result.get('response', '')})
    if len(_history) > 20:
        _history[:] = _history[-20:]
    data: dict = {
        'response': result.get('response', ''),
        'intent': result.get('intent', 'chat'),
    }
    intent = result.get('intent')
    if intent == 'weather':
        info = weather_mod.get_weather(config)
        if info:
            data['weather'] = info
    elif intent == 'news':
        data['headlines'] = news_mod.get_headlines(config)
    elif intent == 'music':
        _music.play(result.get('query') or req.text)
    elif intent == 'music_stop':
        _music.stop()
    elif intent == 'search':
        results = search_mod.web_search(result.get('query') or req.text)
        if results:
            data['search_results'] = results
    return JSONResponse(data)


@app.post('/api/transcribe')
async def transcribe(audio: UploadFile = File(...)) -> JSONResponse:
    import openai
    client = openai.OpenAI(api_key=config.openai_api_key)
    with tempfile.NamedTemporaryFile(suffix='.webm', delete=False) as f:
        f.write(await audio.read())
        tmp = f.name
    try:
        with open(tmp, 'rb') as f:
            text = client.audio.transcriptions.create(model='whisper-1', file=f).text
        return JSONResponse({'text': text})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        os.unlink(tmp)


# Static files — must come after explicit routes
app.mount('/', StaticFiles(directory=str(UI_DIR)), name='static')


if __name__ == '__main__':
    scheduler = Scheduler(config)
    scheduler.start(_morning_briefing)
    print(f'[Beemo] Starting at http://127.0.0.1:8000')
    print(f'[Beemo] Morning briefing at {config.briefing_time}')
    uvicorn.run(app, host='127.0.0.1', port=8000, log_level='warning')
