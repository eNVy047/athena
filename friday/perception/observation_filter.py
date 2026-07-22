from typing import List, Callable
from friday.perception.observation import Observation

class ObservationFilter:
    def __init__(self, min_confidence: float = 0.5):
        self.min_confidence = min_confidence
        self._rules: List[Callable[[Observation], bool]] = []

        # Default rule: confidence threshold check
        self.add_rule(lambda obs: obs.confidence >= self.min_confidence)

    def add_rule(self, rule: Callable[[Observation], bool]) -> None:
        self._rules.append(rule)

    def should_allow(self, observation: Observation) -> bool:
        for rule in self._rules:
            if not rule(observation):
                return False
        return True
