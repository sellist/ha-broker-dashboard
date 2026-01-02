import json
import logging
from typing import Callable

import paho.mqtt.client as mqtt

from .config import MQTTConfig, SensorConfig

logger = logging.getLogger(__name__)


class MQTTClient:

    def __init__(
        self,
        config: MQTTConfig,
        sensors: list[SensorConfig],
        on_message_callback: Callable[[str, str], None],
    ):
        self.config = config
        self.sensors = sensors
        self.on_message_callback = on_message_callback
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

        if config.username and config.password:
            self.client.username_pw_set(config.username, config.password)

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            logger.info("Connected to MQTT broker")
            for sensor in self.sensors:
                client.subscribe(sensor.topic)
                logger.info(f"Subscribed to topic: {sensor.topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker: {reason_code}")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        try:
            payload = msg.payload.decode("utf-8")
            try:
                value = json.loads(payload)
            except json.JSONDecodeError:
                value = payload

            logger.debug(f"Received message on {topic}: {value}")
            self.on_message_callback(topic, value)
        except Exception as e:
            logger.error(f"Error processing message from {topic}: {e}")

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        logger.warning(f"Disconnected from MQTT broker: {reason_code}")

    def connect(self) -> None:
        logger.info(f"Connecting to MQTT broker at {self.config.host}:{self.config.port}")
        try:
            self.client.connect(self.config.host, self.config.port, 60)
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def start(self) -> None:
        self.client.loop_start()

    def stop(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()

