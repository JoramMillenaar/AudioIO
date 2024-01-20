import threading
import wave

import numpy as np
import sounddevice as sd

from AudioIO.base import AudioProcessor
from AudioIO.services import array_to_wav_format


class AudioPlaybackProcessor(AudioProcessor):
    def __init__(self, chunk_size, sample_rate):
        self.sample_rate = sample_rate
        self.output = sd.RawOutputStream(self.sample_rate, channels=1, dtype='float32', blocksize=chunk_size)
        self.output.start()

        self.play_thread = threading.Thread(target=self.play, args=(np.zeros(chunk_size, dtype=np.float32),))
        self.play_thread.start()

    def process(self, audio_chunk):
        self.play_thread.join()
        self.play_thread = threading.Thread(target=self.play, args=(audio_chunk,))
        self.play_thread.start()
        return audio_chunk

    def play(self, current):
        self.output.write(np.clip(current, -1, 1).astype(np.float32))

    def __del__(self):
        self.output.close()


class AudioFileOutputProcessor(AudioProcessor):
    def __init__(self, filename: str, sample_rate):
        self.sample_rate = sample_rate
        self.filename = filename
        self.wav_file = wave.open(self.filename, 'wb')
        self.wav_file.setnchannels(1)
        self.wav_file.setsampwidth(2)  # 2 bytes for 'int16' format
        self.wav_file.setframerate(self.sample_rate)

        self.write_thread = threading.Thread(target=self.write_to_file, args=(b'',))
        self.write_thread.start()

    def process(self, audio_chunk):
        data = array_to_wav_format(audio_chunk)
        self.write_thread.join()
        self.write_thread = threading.Thread(target=self.write_to_file, args=(data,))
        self.write_thread.start()
        return audio_chunk

    def write_to_file(self, data):
        self.wav_file.writeframes(data)

    def __del__(self):
        self.write_thread.join()  # Ensure the last bit of audio is written
        self.wav_file.close()
