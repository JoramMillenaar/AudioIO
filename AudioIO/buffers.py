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
        self.total_samples = 0
        self.current_position = 0

    def __len__(self):
        return min(self.total_samples, self.max_history)

    def get_slice(self, start: int, end: int) -> np.ndarray:
        effective_start = start - (self.total_samples - self.max_history)
        effective_end = end - (self.total_samples - self.max_history)

        if effective_start < 0:
            raise NotEnoughSamplesInHistory(f"History under-reached by {-effective_start} samples")
        if effective_end > self.max_history:
            raise NotEnoughSamples(f"Buffer ran out of samples. Needed {self.max_history - effective_end} more")

        start_index = (self.current_position + effective_start) % self.max_history
        end_index = (self.current_position + effective_end) % self.max_history

        if start_index < end_index or effective_end == 0:
            return self._buffer[:, start_index:end_index]
        else:
            return np.hstack((self._buffer[:, start_index:], self._buffer[:, :end_index]))

    def push(self, audio_chunk: np.ndarray):
        chunk_length = audio_chunk.shape[1]
        end_position = (self.current_position + chunk_length) % self.max_history
        if self.current_position < end_position:
            self._buffer[:, self.current_position:end_position] = audio_chunk
        else:
            space_at_end = self.max_history - self.current_position
            self._buffer[:, self.current_position:] = audio_chunk[:, :space_at_end]
            self._buffer[:, :end_position] = audio_chunk[:, space_at_end:]

        self.current_position = end_position
        self.total_samples += chunk_length

    def __getitem__(self, key: slice) -> np.ndarray:
        if not isinstance(key, slice):
            raise NotImplementedError("CircularBuffer can only lookup slices")
        if key.step is not None:
            raise NotImplementedError("CircularBuffer does not support slices with a step size")

        if key.start is None:
            key.start = 0
        if key.stop is None:
            key.stop = self.total_samples
        if key.start < 0:
            key.start += self.total_samples
        if key.stop < 0:
            key.stop += self.total_samples
        return self.get_slice(key.start, key.stop)


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
