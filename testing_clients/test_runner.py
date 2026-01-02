import json
import logging
import random
import time
from typing import Any, Callable

import paho.mqtt.client as mqtt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class TestRunner:

    def __init__(
        self,
        topic: str,
        message: Any | Callable[[], Any],
        interval_ms: int = 1000,
        host: str = "192.168.4.20",
        port: int = 1883,
        username: str = "admin",
        password: str = "password",
    ):
        self.topic = topic
        self.message = message
        self.interval_ms = interval_ms
        self.host = host
        self.port = port

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        if username and password:
            self.client.username_pw_set(username, password)

        self._running = False

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        # all the unused parameters are required by the callback signature :(, will silent fail otherwise
        if reason_code == 0:
            logger.info(f"Connected to MQTT broker at {self.host}:{self.port}")
        else:
            logger.error(f"Failed to connect to MQTT broker: {reason_code}")

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        # all the unused parameters are required by the callback signature :(, will silent fail otherwise
        logger.warning(f"Disconnected from MQTT broker: {reason_code}")

    def _format_message(self) -> str:
        msg = self.message() if callable(self.message) else self.message
        if isinstance(msg, str):
            return msg
        return json.dumps(msg)

    def connect(self) -> None:
        logger.info(f"Connecting to MQTT broker at {self.host}:{self.port}")
        try:
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
        except ConnectionRefusedError:
            logger.error(f"Connection refused to {self.host}:{self.port}")
            raise
        except TimeoutError:
            logger.error(f"Connection timed out to {self.host}:{self.port}")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def disconnect(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()
        logger.info("Disconnected from MQTT broker")

    def publish_once(self) -> None:
        payload = self._format_message()
        result = self.client.publish(self.topic, payload)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            logger.info(f"Published to {self.topic}: {payload}")
        else:
            logger.error(f"Failed to publish to {self.topic}: {result.rc}")

    def run(self, count: int | None = None) -> None:
        self.connect()
        self._running = True
        interval_sec = self.interval_ms / 1000.0

        try:
            messages_sent = 0
            while self._running:
                self.publish_once()
                messages_sent += 1

                if count is not None and messages_sent >= count:
                    logger.info(f"Sent {messages_sent} messages, stopping...")
                    break

                time.sleep(interval_sec)
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.disconnect()

    def stop(self) -> None:
        self._running = False


if __name__ == "__main__":
    runner = TestRunner(
        topic="home/living_room/temperature",
        message=lambda: random.uniform(-20, 50),
        interval_ms=2000,
    )
    runner.run(count=5)
