from collections import deque
from typing import List, Optional
from friday.perception.observation import Observation

class ObservationBuffer:
    def __init__(self, max_size: int = 100):
        self._buffer = deque(maxlen=max_size)

    def append(self, observation: Observation) -> None:
        self._buffer.append(observation)

    def get_all(self) -> List[Observation]:
        return list(self._buffer)

    def get_latest(self) -> Optional[Observation]:
        if len(self._buffer) > 0:
            return self._buffer[-1]
        return None

    def clear(self) -> None:
        self._buffer.clear()

    def size(self) -> int:
        return len(self._buffer)
