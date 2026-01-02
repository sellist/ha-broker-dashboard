import random
import time
from test_runner import TestRunner

def test_temperature_gauge():
    runner = TestRunner(
        topic="home/living_room/temperature",
        message=25.0,
        interval_ms=2000
    )

    runner.connect()

    try:
        for i in range(20):
            temp = random.uniform(-5, 45)
            runner.message = round(temp, 1)
            runner.publish_once()
            print(f"Sent temperature: {temp:.1f}°C")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        runner.disconnect()

def test_humidity_gauge():
    runner = TestRunner(
        topic="home/living_room/humidity",
        message=50.0,
        interval_ms=1500
    )

    runner.connect()

    try:
        for i in range(15):
            humidity = random.uniform(0, 100)
            runner.message = round(humidity, 1)
            runner.publish_once()
            print(f"Sent humidity: {humidity:.1f}%")
            time.sleep(1.5)
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        runner.disconnect()

if __name__ == "__main__":
    test_temperature_gauge()

    test_humidity_gauge()
