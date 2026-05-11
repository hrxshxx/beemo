from beemo.config import load_config
from beemo.brain import Brain
from beemo import weather, news
from beemo.music import MusicPlayer
from beemo.scheduler import Scheduler
from beemo.wake import WakeDetector
from beemo.listener import Listener
from beemo.core import Core


def main():
    config = load_config()
    core = Core(
        config=config,
        brain=Brain(config),
        weather=weather,
        news=news,
        music=MusicPlayer(),
        scheduler=Scheduler(config),
        wake=WakeDetector(model_path='models/hey_beemo.tflite'),
        listener=Listener(config),
    )
    core.run()


if __name__ == '__main__':
    main()
