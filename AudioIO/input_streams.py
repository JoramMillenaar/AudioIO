import wave
from typing import Iterator

import numpy as np
import sounddevice as sd

from AudioIO.base import AudioStream
from AudioIO.services import generate_sine_wave


class MicrophoneStream(AudioStream):
    def __init__(self, chunk_size: int, sample_rate: int = 44100, channels: int = 1):
        super().__init__(sample_rate=sample_rate, channels=channels)
        self.chunk_size = chunk_size
        self.channels = channels
        self.stream = None

    def open_stream(self):
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=self.chunk_size,
            channels=self.channels
        )
        self.stream.start()

    def iterable(self) -> Iterator:
        if self.stream is None:
            self.open_stream()

        while not self.is_closed:
            return self.stream.read(self.chunk_size)[0].T

    def close(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
        super().close()


class WAVFileReadStream(AudioStream):
    def __init__(self, file_path: str, chunk_size: int):
        self.file_path = file_path
        self.wav_file = wave.open(self.file_path, 'rb')
        self.channels = self.wav_file.getnchannels()
        self.chunk_size = chunk_size
        self.sample_width = self.wav_file.getsampwidth()
        super().__init__(sample_rate=self.wav_file.getframerate(), channels=self.wav_file.getnchannels())

    def iterable(self) -> Iterator:
        while True:
            frames = self.wav_file.readframes(self.chunk_size)
            if not frames:
                break

            # Convert byte data to numpy array
            data = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
            data /= 32768  # Convert from int16 to float32 range [-1, 1]

            data = np.reshape(data, (self.channels, self.chunk_size), order='F')

            yield data

    def close(self):
        self.wav_file.close()
        super().close()


class SineWaveStream(AudioStream):
    def __init__(self, frequency: float, amplitude: float, chunk_size: int, sample_rate: int = 44100, channels=1):
        super().__init__(sample_rate=sample_rate, channels=channels)
        self.amplitude = amplitude
        self.chunk_size = chunk_size
        self.frequency = frequency

    def iterable(self):
        sine_waver = generate_sine_wave(self.frequency, self.chunk_size, self.sample_rate, self.amplitude)
        while True:
            yield np.tile(next(sine_waver), (self.channels, 1))
