# Beemo — Local AI Assistant Design Spec

**Date:** 2026-05-11
**Platform:** macOS
**Language:** Python
**Status:** Approved

---

## Overview

Beemo is a local AI assistant activated by the wake word "hey beemo" or via text input in the terminal. It responds in text, integrates with weather and news APIs, and plays songs from YouTube. The OpenAI API powers both speech-to-text (Whisper) and intent classification + responses (GPT-4o).

---

## Architecture & Data Flow

```
[Mic] ──► wake.py (openWakeWord)
              │
              ▼  "hey beemo" detected
         listener.py (records audio clip)
              │
              ▼
         OpenAI Whisper API (speech → text)
              │
              ▼  OR  [Terminal text input]
         brain.py (GPT-4o)
         ├─ intent: weather    ──► weather.py ──► OpenWeatherMap
         ├─ intent: news       ──► news.py    ──► NewsAPI
         ├─ intent: music      ──► music.py   ──► yt-dlp + mpv
         └─ intent: general    ──► GPT reply
              │
              ▼
         Text printed to terminal

scheduler.py (APScheduler)
  └─ every morning at configured time ──► news.py + weather.py (auto-briefing)
```

---

## Project Structure

```
beemo/
├── .env                  ← API keys + config
├── requirements.txt
├── main.py               ← entry point
├── beemo/
│   ├── __init__.py
│   ├── core.py           ← main loop + dispatcher
│   ├── wake.py           ← openWakeWord listener thread
│   ├── listener.py       ← mic recording + Whisper STT
│   ├── brain.py          ← GPT-4o intent + response
│   ├── weather.py        ← OpenWeatherMap integration
│   ├── news.py           ← NewsAPI headlines
│   ├── music.py          ← yt-dlp + mpv playback
│   └── scheduler.py      ← APScheduler morning briefing
└── models/
    └── hey_beemo.tflite  ← custom wake word model (trained separately)
```

---

## APIs & Dependencies

### External APIs

| Service | Purpose | Free Tier |
|---|---|---|
| OpenAI API | Whisper STT + GPT-4o brain | Pay-per-use |
| OpenWeatherMap | Current weather conditions | 1000 calls/day |
| NewsAPI | Top 4 headlines | 100 req/day |
| ipapi.co | IP → city/country geolocation | 1000 req/day |

### Python Libraries

| Library | Role |
|---|---|
| `openwakeword` | "hey beemo" hotword detection |
| `pyaudio` | Microphone capture |
| `openai` | Whisper STT + GPT-4o |
| `yt-dlp` | YouTube audio stream extraction |
| `mpv` (system, via Homebrew) | Audio playback subprocess |
| `APScheduler` | Morning briefing cron job |
| `requests` | Weather + news HTTP calls |
| `python-dotenv` | `.env` key loading |

---

## Feature Details

### Wake Word Detection
- `wake.py` runs in a background thread, continuously listening via `pyaudio`
- Uses `openWakeWord` with a custom `hey_beemo.tflite` model
- During development, the built-in `"hey_jarvis"` model is used as a placeholder
- On detection, triggers `listener.py` to begin recording

### Voice Input
- `listener.py` records up to 8 seconds of audio, stopping early on silence
- Audio buffer is sent to OpenAI Whisper API and returned as text
- Text input mode: user types directly in terminal, bypassing wake + Whisper

### Brain (GPT-4o Intent Routing)
- `brain.py` sends transcript + system prompt to GPT-4o
- System prompt instructs Beemo to respond in character and return structured JSON:
  ```json
  { "intent": "weather|news|music|chat", "query": "...", "response": "..." }
  ```
- `core.py` reads `intent` and dispatches to the appropriate module

### Weather
- On startup, `weather.py` fetches city from `ipapi.co` (cached, refreshed daily)
- Calls OpenWeatherMap for current conditions
- Output: city, temperature (°C), condition description, humidity

### News Headlines
- `news.py` fetches the top 4 headlines from NewsAPI
- Country configurable via `NEWS_COUNTRY` in `.env` (default: `us`)
- Triggered on-demand ("hey beemo, what's the news?") or by scheduler

### Morning Briefing (Scheduled)
- `scheduler.py` uses APScheduler to fire at `BRIEFING_TIME` (default: `08:00`)
- Briefing output: current weather + 4 headlines, printed to terminal

### Music Playback
- `music.py` accepts a song/artist query
- Uses `yt-dlp` to search YouTube and extract the best audio-only stream URL
- Plays via `mpv` as a background subprocess
- Supported commands: play, stop

---

## Configuration (`.env`)

```
OPENAI_API_KEY=
OPENWEATHERMAP_KEY=
NEWS_API_KEY=
BRIEFING_TIME=08:00
NEWS_COUNTRY=us
```

---

## Error Handling

| Scenario | Behaviour |
|---|---|
| Missing `.env` key on startup | Print specific missing key name and exit |
| OpenAI API failure | Print "Beemo couldn't process that, try again" |
| Weather API failure | Print "Couldn't fetch weather right now" |
| News API failure | Print "Couldn't fetch headlines right now" |
| `mpv` not installed | Print Homebrew install command on first music request |
| Wake word model missing | Fall back to text-only mode with a printed notice |

---

## Out of Scope (v1)

- Text-to-speech output (TTS) — text only for now
- Multi-turn conversation memory
- Spotify integration
- GUI / web interface
- Custom wake word training (placeholder model used during development)
