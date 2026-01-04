import asyncio
import logging
import sys
from pathlib import Path

import uvicorn

if __name__ == "__main__" and __package__ is None:
    # Running as script - fix imports
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from ha_broker_dashboard.config import load_config
    from ha_broker_dashboard.data_store import DataStore
    from ha_broker_dashboard.mqtt_client import MQTTClient
    from ha_broker_dashboard.web_server import broadcast_sensor_update, create_app
    from ha_broker_dashboard.websocket_manager import WebSocketManager
else:
    # Running as module
    from .config import load_config
    from .data_store import DataStore
    from .mqtt_client import MQTTClient
    from .web_server import broadcast_sensor_update, create_app
    from .websocket_manager import WebSocketManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class Dashboard:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = load_config(config_path)
        self.data_store = DataStore()
        self.ws_manager = WebSocketManager()
        self.app = create_app(self.data_store, self.ws_manager)
        self.mqtt_client: MQTTClient | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def _register_sensors(self) -> None:
        topics_seen = set()
        for sensor in self.config.sensors:
            if sensor.topic in topics_seen:
                logger.warning(f"Duplicate topic found in configuration: {sensor.topic}")
                logger.warning("Only the first sensor configuration for this topic will be used")
                continue

            topics_seen.add(sensor.topic)

            self.data_store.register_sensor(
                topic=sensor.topic,
                name=sensor.name,
                sensor_type=sensor.type,
                implementation=sensor.implementation,
                history_size=sensor.history,
                min_value=sensor.min,
                max_value=sensor.max,
                true_value=getattr(sensor, 'true', None),
                false_value=getattr(sensor, 'false', None),
                unit=sensor.unit,
                input_unit=sensor.inputUnit,
                precision=sensor.precision,
            )
            logger.info(f"Registered sensor: {sensor.name} ({sensor.topic})")

    def _on_mqtt_message(self, topic: str, value) -> None:
        sensor_data = self.data_store.update_sensor(topic, value)
        if sensor_data and self._loop:
            asyncio.run_coroutine_threadsafe(
                broadcast_sensor_update(self.ws_manager, topic, sensor_data.to_dict()),
                self._loop,
            )

    def run(self) -> None:
        logger.info("Starting HA Broker Dashboard...")
        self._register_sensors()

        self.mqtt_client = MQTTClient(
            config=self.config.mqtt,
            sensors=self.config.sensors,
            on_message_callback=self._on_mqtt_message,
        )

        try:
            self.mqtt_client.connect()
            self.mqtt_client.start()
            logger.info("MQTT client started")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")

        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        config = uvicorn.Config(
            self.app,
            host=self.config.server.host,
            port=self.config.server.port,
            loop="asyncio",
        )
        server = uvicorn.Server(config)

        try:
            logger.info(
                f"Starting web server on http://{self.config.server.host}:{self.config.server.port}"
            )
            self._loop.run_until_complete(server.serve())
        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            if self.mqtt_client:
                self.mqtt_client.stop()
            self._loop.close()


def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"

    if not Path(config_path).exists():
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)

    dashboard = Dashboard(config_path)
    dashboard.run()


if __name__ == "__main__":
    main()

