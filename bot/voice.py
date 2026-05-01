import sounddevice as sd
from kokoro_onnx import Kokoro
import os

kokoro = Kokoro(
    os.path.join(os.path.dirname(__file__), '..', 'kokoro-v1.0.onnx'),
    os.path.join(os.path.dirname(__file__), '..', 'voices-v1.0.bin')
)

def speak(text: str):
    from bot.warudo import trigger
    trigger("talking")
    samples, sample_rate = kokoro.create(
        text,
        voice="am_adam",
        speed=1.0,
        lang="en-us"
    )
    sd.play(samples, sample_rate)
    sd.wait()