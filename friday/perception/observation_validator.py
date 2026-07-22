from friday.perception.observation import Observation

class ObservationValidator:
    @staticmethod
    def validate(observation: Observation) -> bool:
        if not observation.id or not isinstance(observation.id, str):
            return False
        if not observation.sensor_name or not isinstance(observation.sensor_name, str):
            return False
        if observation.timestamp <= 0:
            return False
        if not (0.0 <= observation.confidence <= 1.0):
            return False
        return True
