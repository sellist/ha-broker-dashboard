from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Any

from .conversions import convert_value, truncate_to_precision


@dataclass
class SensorData:
    topic: str
    name: str
    type: str
    implementation: str
    current_value: Any = None
    history: deque = field(default_factory=lambda: deque(maxlen=100))
    last_updated: datetime | None = None
    min_value: float | None = None
    max_value: float | None = None
    true_value: str | None = None
    false_value: str | None = None
    last_switched: datetime | None = None
    unit: str | None = None
    input_unit: str | None = None
    precision: float | None = None

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "name": self.name,
            "type": self.type,
            "implementation": self.implementation,
            "current_value": self.current_value,
            "history": list(self.history),
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "true_value": self.true_value,
            "false_value": self.false_value,
            "last_switched": self.last_switched.isoformat() if self.last_switched else None,
            "unit": self.unit,
            "input_unit": self.input_unit,
            "precision": self.precision,
        }


class DataStore:
    def __init__(self):
        self._sensors: dict[str, SensorData] = {}
        self._lock = Lock()

    def register_sensor(
        self,
        topic: str,
        name: str,
        sensor_type: str,
        implementation: str,
        history_size: int,
        min_value: float | None = None,
        max_value: float | None = None,
        true_value: str | None = None,
        false_value: str | None = None,
        unit: str | None = None,
        input_unit: str | None = None,
        precision: float | None = None,
    ) -> None:
        with self._lock:
            if topic in self._sensors:
                return
            self._sensors[topic] = SensorData(
                topic=topic,
                name=name,
                type=sensor_type,
                implementation=implementation,
                history=deque(maxlen=history_size),
                min_value=min_value,
                max_value=max_value,
                true_value=true_value,
                false_value=false_value,
                unit=unit,
                input_unit=input_unit,
                precision=precision,
            )

    def update_sensor(self, topic: str, value: Any) -> SensorData | None:
        with self._lock:
            if topic not in self._sensors:
                return None
            sensor = self._sensors[topic]
            old_value = sensor.current_value

            # apply unit conversion if input_unit and unit differ
            converted_value = value
            if sensor.input_unit and sensor.unit and sensor.input_unit != sensor.unit:
                try:
                    numeric_value = float(value)
                    converted_value = convert_value(numeric_value, sensor.input_unit, sensor.unit)
                except (ValueError, TypeError):
                    pass

            if sensor.precision is not None:
                try:
                    numeric_value = float(converted_value)
                    converted_value = truncate_to_precision(numeric_value, sensor.precision)
                except (ValueError, TypeError):
                    pass

            sensor.current_value = converted_value
            sensor.last_updated = datetime.now()
            if sensor.implementation == "graph":
                sensor.history.append(
                    {"value": converted_value, "timestamp": sensor.last_updated.isoformat()}
                )
            elif sensor.implementation == "boolean":
                if old_value != converted_value:
                    sensor.last_switched = sensor.last_updated
            return sensor

    def get_sensor(self, topic: str) -> SensorData | None:
        with self._lock:
            return self._sensors.get(topic)

    def get_all_sensors(self) -> dict[str, dict]:
        with self._lock:
            return {topic: sensor.to_dict() for topic, sensor in self._sensors.items()}

