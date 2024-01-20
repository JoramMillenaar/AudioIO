import numpy as np
from numpy._typing import NDArray


def generate_sine_wave(freq: float, chunk_size: int, sample_rate: int, volume: float):
    t = 0
    omega = 2 * np.pi * freq
    while True:
        samples = np.arange(t, t + chunk_size, dtype=np.float32) / sample_rate
        chunk = np.sin(omega * samples) * volume
        yield chunk
        t += chunk_size


def array_to_wav_format(data: NDArray) -> bytes:
    """Convert the float32 array to int16 to write to WAV file"""
    return (data * 32767).astype(np.int16).tobytes()
