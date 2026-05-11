from __future__ import annotations
import queue
import threading
from beemo.config import Config
from beemo.brain import Brain
from beemo.music import MusicPlayer
from beemo.scheduler import Scheduler
from beemo.wake import WakeDetector
from beemo.listener import Listener


class Core:
    def __init__(
        self,
        config: Config,
        brain: Brain,
        weather,
        news,
        music: MusicPlayer,
        scheduler: Scheduler,
        wake: WakeDetector,
        listener: Listener,
    ):
        self._config = config
        self._brain = brain
        self._weather = weather
        self._news = news
        self._music = music
        self._scheduler = scheduler
        self._wake = wake
        self._listener = listener
        self._queue: queue.Queue = queue.Queue()

    def run(self) -> None:
        self._wake.start(lambda: self._queue.put(('wake', None)))
        self._scheduler.start(self._morning_briefing)
        threading.Thread(target=self._text_loop, daemon=True).start()
        print("Beemo is ready. Type a command or say 'hey beemo'.\n")
        try:
            while True:
                try:
                    kind, data = self._queue.get(timeout=1)
                    if kind == 'wake':
                        print('[Beemo] Listening...')
                        transcript = self._listener.listen()
                        if transcript:
                            self._handle(transcript)
                    elif kind == 'text':
                        self._handle(data)
                except queue.Empty:
                    continue
        except KeyboardInterrupt:
            print('\n[Beemo] Shutting down.')
            self._scheduler.stop()
            self._wake.stop()
            self._music.stop()

    def _text_loop(self) -> None:
        while True:
            try:
                text = input('> ')
                if text.strip():
                    self._queue.put(('text', text.strip()))
            except EOFError:
                break

    def _handle(self, text: str) -> None:
        result = self._brain.process(text)
        print(f'\nBeemo: {result["response"]}')
        if result['intent'] == 'weather':
            info = self._weather.get_weather(self._config)
            if info:
                print(f'  {info["city"]}: {info["temp"]}°C, {info["condition"]}, {info["humidity"]}% humidity')
        elif result['intent'] == 'news':
            headlines = self._news.get_headlines(self._config)
            for i, h in enumerate(headlines, 1):
                print(f'  {i}. {h}')
        elif result['intent'] == 'music':
            self._music.play(result.get('query') or text)
        elif result['intent'] == 'music_stop':
            self._music.stop()
        print()

    def _morning_briefing(self) -> None:
        print('\n--- Good morning! Here is your briefing ---')
        info = self._weather.get_weather(self._config)
        if info:
            print(f'Weather: {info["city"]}: {info["temp"]}°C, {info["condition"]}, {info["humidity"]}% humidity')
        headlines = self._news.get_headlines(self._config)
        print('Top headlines:')
        for i, h in enumerate(headlines, 1):
            print(f'  {i}. {h}')
        print('-------------------------------------------\n')
