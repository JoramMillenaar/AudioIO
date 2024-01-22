from typing import Iterable, Protocol

import numpy as np


class Buffer(Protocol):
    def __getitem__(self, key: slice) -> np.ndarray:
        pass


class NotEnoughSamples(BufferError):
    pass


class NotEnoughSamplesInHistory(BufferError):
    pass


class CircularBuffer(Buffer):
    def __init__(self, channels: int, max_history: int):
        self.channels = channels
        self.max_history = max_history
        self._buffer = np.zeros((channels, max_history), dtype=np.float32)
        self.pushed_samples = 0

    def __len__(self):
        return min(self.pushed_samples, self.max_history)

    def get_slice(self, start: int, end: int) -> np.ndarray:
        start_index = self.max_history - (self.pushed_samples - start)
        end_index = self.max_history - (self.pushed_samples - end)
        if start_index < 0:
            raise NotEnoughSamplesInHistory(f"History under-reached by {-start_index} samples")
        if end_index > self.max_history:
            raise NotEnoughSamples(f"Buffer ran out of samples. Needed {self.max_history - end_index} more")

        if start_index < end_index:
            return self._buffer[:, start_index:end_index]
        else:
            return np.hstack((self._buffer[:, start_index:], self._buffer[:, :end_index]))

    def push(self, audio_chunk: np.ndarray):
        chunk_length = audio_chunk.shape[1]
        self._buffer = np.concatenate((self._buffer[:, chunk_length:], audio_chunk), axis=1)
        self.pushed_samples += chunk_length

    def __getitem__(self, key: slice) -> np.ndarray:
        if not isinstance(key, slice):
            raise NotImplementedError("CircularBuffer can only lookup slices")
        if key.step is not None:
            raise NotImplementedError("CircularBuffer does not support slices with a step size")

        start, stop = key.start, key.stop

        if start is None:
            start = 0
        if stop is None:
            stop = self.pushed_samples
        if start < 0:
            start += self.pushed_samples
        if stop < 0:
            stop += self.pushed_samples
        return self.get_slice(start, stop)


class BufferedInput(Buffer):
    def __init__(self, max_history: int, audio_input: Iterable[np.ndarray], channels: int):
        self.audio_input = iter(audio_input)
        self.circular_buffer = CircularBuffer(channels=channels, max_history=max_history)

    def _fetch_and_store(self):
        self.circular_buffer.push(next(self.audio_input))

    def __getitem__(self, item):
        try:
            return self.circular_buffer[item]
        except NotEnoughSamples:
            self._fetch_and_store()
            return self[item]
