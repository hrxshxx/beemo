from __future__ import annotations
import subprocess


class MusicPlayer:
    def __init__(self):
        self._process: subprocess.Popen | None = None

    def play(self, query: str) -> None:
        self.stop()
        try:
            result = subprocess.run(
                ['yt-dlp', f'ytsearch1:{query}', '--format', 'bestaudio/best',
                 '--get-url', '--no-playlist', '-q'],
                capture_output=True, text=True, timeout=30,
            )
        except FileNotFoundError:
            print("yt-dlp is not installed. Run: pip install yt-dlp")
            return

        url = result.stdout.strip().split('\n')[0]
        if not url:
            print(f"Couldn't find a YouTube result for: {query}")
            return

        try:
            self._process = subprocess.Popen(
                ['mpv', '--no-video', '--really-quiet', url],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            print(f"[Beemo] Now playing: {query}")
        except FileNotFoundError:
            print("mpv is not installed. Run: brew install mpv")

    def stop(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()
            self._process = None
            print("[Beemo] Music stopped.")
