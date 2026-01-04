import random
import time
from test.remote.test_runner import TestRunner

def test_garage_door():
    runner = TestRunner(
        topic="home/garage/door",
        message="closed",
        interval_ms=3000
    )

    runner.connect()

    try:
        state = False
        for i in range(20):
            if random.random() < 0.3 or i % 5 == 0:
                state = not state

            runner.message = "open" if state else "closed"
            runner.publish_once()
            print(f"Sent garage door state: {'open' if state else 'closed'}")
            time.sleep(3)
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        runner.disconnect()


def test_boolean_toggle():
    runner = TestRunner(
        topic="home/garage/door",
        message="closed",
        interval_ms=1000
    )

    runner.connect()

    try:
        state = False
        for i in range(30):
            state = not state
            runner.message = "open" if state else "closed"
            runner.publish_once()
            print(f"Toggle #{i+1}: {'open' if state else 'closed'}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        runner.disconnect()


def test_boolean_random():
    runner = TestRunner(
        topic="home/garage/door",
        message="closed",
        interval_ms=2000
    )

    runner.connect()

    try:
        for i in range(20):
            state = random.choice(["open", "closed"])
            runner.message = state
            runner.publish_once()
            print(f"Random state: {state}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        runner.disconnect()


if __name__ == "__main__":
    test_garage_door()

    test_boolean_toggle()

    test_boolean_random()

