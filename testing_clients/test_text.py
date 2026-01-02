import random
import time
from test_runner import TestRunner


def test_motion_detection():
    runner = TestRunner(
        topic="home/front_door/motion",
        message="motion detected",
        interval_ms=3000
    )

    runner.connect()

    motion_events = [
        "motion detected",
        "no motion",
        "motion detected",
        "person detected",
        "no motion",
        "motion detected",
        "animal detected",
        "no motion",
    ]

    try:
        for i, event in enumerate(motion_events):
            runner.message = event
            runner.publish_once()
            print(f"[{i+1}/{len(motion_events)}] Sent motion event: {event}")
            time.sleep(3)
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        runner.disconnect()


def test_random_text_messages():
    runner = TestRunner(
        topic="home/front_door/motion",
        message="",
        interval_ms=2000
    )

    runner.connect()

    messages = [
        "Sensor active",
        "Movement at 14:32",
        "Alert: Multiple detections",
        "Idle",
        "Triggered by pet",
        "Armed",
        "Disarmed",
        "Battery low: 15%",
        "Connection restored",
        "Firmware updated",
    ]

    try:
        for i in range(15):
            msg = random.choice(messages)
            runner.message = msg
            runner.publish_once()
            print(f"[{i+1}/15] Sent text message: {msg}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        runner.disconnect()


def test_json_payload():
    runner = TestRunner(
        topic="home/front_door/motion",
        message={},
        interval_ms=2500
    )

    runner.connect()

    try:
        for i in range(10):
            payload = {
                "event": random.choice(["motion", "clear", "alert"]),
                "confidence": random.randint(50, 100),
                "timestamp": f"2026-01-01T22:{random.randint(0,59):02d}:00"
            }
            runner.message = payload
            runner.publish_once()
            print(f"[{i+1}/10] Sent JSON payload: {payload}")
            time.sleep(2.5)
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        runner.disconnect()


if __name__ == "__main__":
    test_motion_detection()

    test_random_text_messages()

    test_json_payload()
