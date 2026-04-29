import sounddevice as sd
import numpy as np
from kokoro_onnx import Kokoro

kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")

def speak(text: str):
    samples, sample_rate = kokoro.create(
        text,
        voice="am_adam",
        speed=1.0,
        lang="en-us"
    )
    sd.play(samples, sample_rate)
    sd.wait()