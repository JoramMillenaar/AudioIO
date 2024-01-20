from abc import ABC, abstractmethod
from typing import Protocol, Iterator

import numpy as np


class AudioProcessor(Protocol):
    def process(self, audio_chunk: np.ndarray) -> np.ndarray:
        pass


class AudioStream(Iterator, ABC):
    def __init__(self, sample_rate: int, channels: int):
        self.channels = channels
        self.sample_rate = sample_rate
        self.is_closed = False
        self.is_closing = False
        self.current = None
        self._cached_iterable = None

    @abstractmethod
    def iterable(self) -> Iterator:
        pass

    def close(self):
        self.is_closed = True

    def start_closing(self):
        self.is_closing = True

    def get_current(self):
        return self.current

    def __next__(self):
        if self._cached_iterable is None:
            self._cached_iterable = self.iterable()

        if self.is_closed:
            raise StopIteration

        try:
            self.current = next(self._cached_iterable)
        except (KeyboardInterrupt, StopIteration):
            self.close()
            raise
        return self.current

    def run(self):
        try:
            while True:
                next(self)
        except KeyboardInterrupt:
            self.close()
            raise

    def __del__(self):
        self.close()

