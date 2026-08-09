<div align="center">

# beemo

**ambient intelligence that lives on your machine**

<sub>say *"hey beemo"* — it wakes, listens, thinks locally, and answers</sub>

<br />

![Python](https://img.shields.io/badge/python-0A0A0A?style=flat-square&logo=python&logoColor=white&labelColor=0A0A0A)
![Ollama](https://img.shields.io/badge/ollama-0A0A0A?style=flat-square&logo=ollama&logoColor=white&labelColor=0A0A0A)
![Whisper](https://img.shields.io/badge/whisper-0A0A0A?style=flat-square&logo=openai&logoColor=white&labelColor=0A0A0A)
![FastAPI](https://img.shields.io/badge/fastapi-0A0A0A?style=flat-square&logo=fastapi&logoColor=white&labelColor=0A0A0A)
![Tests](https://img.shields.io/badge/pytest-9_suites-0A0A0A?style=flat-square&labelColor=0A0A0A)

</div>

<br />

## ⟢ &nbsp; the idea

Most assistants ship your voice to someone else's datacenter and rent you the answer.

Beemo doesn't. The reasoning happens on **your** hardware — a local Llama model over Ollama,
no round trip, no subscription, no telemetry. It sits idle at near-zero cost, watching a
16 kHz audio stream for one word. When it hears its name, it wakes up, catches what you said,
figures out what you meant, and does it.

Everything it can't do locally, it does deliberately and narrowly — one Whisper call to turn
your voice into text, and nothing else leaves the machine.

<br />

## ⟢ &nbsp; what it does

**Wakes on its name.** A neural wake-word model runs continuously against live mic input at
1280-sample frames. No button, no hotkey, no "click to talk." It costs almost nothing to leave
running all day.

**Knows when you've stopped talking.** Rather than a fixed recording window, the listener tracks
RMS amplitude per chunk and cuts the moment you fall silent — so short questions stay short
instead of padding out to a timeout.

**Thinks locally.** A local Llama model classifies intent and writes the reply in a single pass,
returning strict JSON — intent, query, response. One inference does the routing *and* the talking.

**Routes to the real world.** Six intents, each wired to something that actually happens:

| intent | what fires |
|:--|:--|
| `weather` | geolocates you by IP, caches the city for a day, pulls live conditions |
| `news` | top headlines for your region |
| `music` | searches YouTube, streams the audio, no video, no browser |
| `music_stop` | kills playback mid-song |
| `search` | live DuckDuckGo results when it knows it doesn't know |
| `chat` | just answers |

**Wakes you up too.** A scheduled morning briefing reads out weather and headlines at whatever
time you set — the one thing it does without being asked.

**Knows what it doesn't know.** The intent prompt draws an explicit line between what the model
can answer confidently and what needs looking up — recent events, prices, scores, people. Uncertainty
routes to search instead of hallucinating.

**Degrades honestly.** Ollama down, mic busy, API unreachable, no search hits — every failure path
returns a plain sentence about what broke instead of a stack trace.

<br />

## ⟢ &nbsp; two front ends, one brain

```
                    ┌─────────────┐
     mic ──────────►│  wake word  │  openWakeWord · ONNX · always on
                    └──────┬──────┘
                           │  "hey beemo"
                    ┌──────▼──────┐
                    │   listener  │  silence-aware capture ──► Whisper
                    └──────┬──────┘
                           │
  terminal ───────────►┌───▼───┐◄─────────── web ui
                       │ brain │  llama3.2 · local · strict json
                       └───┬───┘
                           │
       ┌───────────┬───────┼───────┬───────────┐
       ▼           ▼       ▼       ▼           ▼
    weather      news    music   search      chat
                            │
                    yt-dlp ─┴─ mpv
```

The same core answers to a **terminal REPL** and a **FastAPI server** — a threaded queue merges
wake-word events and typed input into one stream, so voice and text are the same code path rather
than two implementations that drift apart.

<br />

## ⟢ &nbsp; the interface

The web UI is not a chat box on a white page. It's a dark, atmospheric surface built by hand —
a canvas particle field drifting upward, layered radial gradients, twinkling starfield, SVG film
grain over the top, glassmorphic panels with real backdrop blur, and parallax that responds to
the cursor.

It respects `prefers-reduced-motion` (particles drop to zero), throttles DPR to 1.5 so it stays
smooth on retina, and pauses its own animation loop the moment the tab loses visibility. Pretty
*and* well-behaved.

Voice works in the browser too — recorded audio posts to a transcription endpoint and rejoins the
same pipeline the terminal uses.

<br />

## ⟢ &nbsp; built properly

- **Dependency-injected core.** `Core` receives brain, listener, wake, music, scheduler, weather
  and news as constructor arguments — every one swappable, every one mockable.
- **9 pytest suites** covering intent parsing, silence detection, config validation, playback,
  scheduling and the API integrations.
- **Threaded, not blocking.** Wake detection, the scheduler, and text input each run on their own
  thread and communicate through a single queue. Ctrl-C unwinds all of them cleanly.
- **Fails closed on config.** Missing keys are caught at startup with a named error, not five
  minutes later mid-request.
- **Bounded memory.** Web conversation history trims to the last 20 turns instead of growing forever.

<br />

## ⟢ &nbsp; stack

`python` · `ollama` · `openwakeword` · `onnx` · `whisper` · `pyaudio` · `fastapi` · `uvicorn`
`apscheduler` · `yt-dlp` · `mpv` · `duckduckgo` · `pytest`

<br />

<div align="center">

<sub>built by **[hrxshx](https://github.com/hrxshxx)** &nbsp;·&nbsp; runs on your machine, answers to you</sub>

</div>
