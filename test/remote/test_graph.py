import math
import random
import time
from test.remote.test_runner import TestRunner


def test_bedroom_temperature_graph():
    runner = TestRunner(
        topic="home/bedroom/temperature",
        message=20.0,
        interval_ms=1000
    )

    runner.connect()

    try:
        base_temp = 20.0
        for i in range(50):
            temp = base_temp + 5 * math.sin(i / 10) + random.uniform(-0.5, 0.5)
            runner.message = round(temp, 1)
            runner.publish_once()
            print(f"[{i+1}/50] Sent bedroom temperature: {temp:.1f}°C")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        runner.disconnect()


def test_graph_rapid_changes():
    runner = TestRunner(
        topic="home/bedroom/temperature",
        message=20.0,
        interval_ms=500
    )

    runner.connect()

    try:
        for i in range(30):
            temp = random.uniform(15, 30)
            runner.message = round(temp, 1)
            runner.publish_once()
            print(f"[{i+1}/30] Sent rapid temperature: {temp:.1f}°C")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        runner.disconnect()


def test_graph_rising_trend():
    runner = TestRunner(
        topic="home/bedroom/temperature",
        message=15.0,
        interval_ms=1000
    )

    runner.connect()

    try:
        temp = 15.0
        for i in range(25):
            temp += random.uniform(0.3, 0.8)
            runner.message = round(temp, 1)
            runner.publish_once()
            print(f"[{i+1}/25] Sent rising temperature: {temp:.1f}°C")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        runner.disconnect()


if __name__ == "__main__":

    test_bedroom_temperature_graph()

    test_graph_rapid_changes()

    test_graph_rising_trend()


