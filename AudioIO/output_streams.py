import threading
import wave

import numpy as np
import sounddevice as sd

from AudioIO.base import AudioProcessor
from AudioIO.services import array_to_wav_format


class AudioPlaybackProcessor:
    def __init__(self, chunk_size, sample_rate, channels):
        self.sample_rate = sample_rate
        self.channels = channels
        self.output = sd.RawOutputStream(self.sample_rate, channels=channels, dtype='float32', blocksize=chunk_size)
        self.output.start()

        self.play_thread = threading.Thread(target=self.play,
                                            args=(np.zeros(channels * chunk_size, dtype=np.float32),))
        self.play_thread.start()

    def process(self, audio_chunk):
        interleaved_chunk = self.interleave(audio_chunk)

        self.play_thread.join()
        self.play_thread = threading.Thread(target=self.play, args=(interleaved_chunk,))
        self.play_thread.start()
        return interleaved_chunk

    def play(self, current):
        self.output.write(current.astype(np.float32))

    def interleave(self, stereo_data):
        return np.ravel(np.column_stack(stereo_data))

    def __del__(self):
        self.output.close()


class WAVFileWriteStream(AudioProcessor):
    def __init__(self, filename: str, sample_rate: int, channels: int):
        self.channels = channels
        self.sample_rate = sample_rate
        self.filename = filename
        self.wav_file = wave.open(self.filename, 'wb')
        self.wav_file.setnchannels(channels)
        self.wav_file.setsampwidth(2)  # 2 bytes for 'int16' format
        self.wav_file.setframerate(self.sample_rate)

        self.write_thread = threading.Thread(target=self.write_to_file, args=(b'',))
        self.write_thread.start()

    def process(self, audio_chunk):
        data = np.reshape(audio_chunk, self.channels * audio_chunk.shape[1], order='F')
        data = array_to_wav_format(data)
        self.write_thread.join()
        self.write_thread = threading.Thread(target=self.write_to_file, args=(data,))
        self.write_thread.start()
        return audio_chunk

    def write_to_file(self, data):
        self.wav_file.writeframes(data)

    def __del__(self):
        self.write_thread.join()  # Ensure the last bit of audio is written
        self.wav_file.close()
