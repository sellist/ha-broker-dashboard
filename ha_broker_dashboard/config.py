from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml


@dataclass
class MQTTConfig:
    host: str
    port: int
    username: str = ""
    password: str = ""


@dataclass
class ServerConfig:
    host: str
    port: int


@dataclass
class SensorConfig:
    topic: str
    type: str
    name: str
    implementation: Literal["gauge", "graph", "text", "boolean"]
    history: int
    min: float | None = None
    max: float | None = None
    true: str | None = None
    false: str | None = None
    unit: str | None = None


@dataclass
class AppConfig:
    mqtt: MQTTConfig
    server: ServerConfig
    sensors: list[SensorConfig]


def load_config(config_path: str | Path = "config.yaml") -> AppConfig:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with open(path) as f:
        data = yaml.safe_load(f)

    return AppConfig(
        mqtt=MQTTConfig(**data.get("mqtt", {})),
        server=ServerConfig(**data.get("server", {})),
        sensors=[SensorConfig(**s) for s in data.get("sensors", [])],
    )
