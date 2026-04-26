import json

import pytest

from src.infrastructure.kafka.consumer import KafkaConsumer
from src.infrastructure.kafka.producer import KafkaProducer


class DummyMessage:
    def __init__(self, payload):
        self.value = json.dumps(payload).encode("utf-8")


class DummyAIOProducer:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.started = False
        self.stopped = False
        self.sent = []

    async def start(self):
        self.started = True

    async def stop(self):
        self.stopped = True

    async def send_and_wait(self, topic, key, value):
        self.sent.append((topic, key, value))
        return type("Meta", (), {"topic": topic, "partition": 0, "offset": 42})()


class DummyAIOConsumer:
    def __init__(self, *args, **kwargs):
        self.started = False
        self.stopped = False
        self.commits = 0
        self.messages = []

    async def start(self):
        self.started = True

    async def stop(self):
        self.stopped = True

    async def commit(self):
        self.commits += 1

    def __aiter__(self):
        async def _gen():
            for msg in self.messages:
                yield msg

        return _gen()


@pytest.mark.asyncio
async def test_kafka_producer_send_message(mocker):
    mocker.patch(
        "src.infrastructure.kafka.producer.AIOKafkaProducer",
        side_effect=DummyAIOProducer,
    )
    producer = KafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()

    await producer.send_message("topic", "key", {"x": 1})

    assert producer._producer is not None
    assert producer._producer.sent
    await producer.stop()


@pytest.mark.asyncio
async def test_kafka_producer_send_without_start_raises():
    producer = KafkaProducer(bootstrap_servers="localhost:9092")
    with pytest.raises(RuntimeError, match="not started"):
        await producer.send_message("topic", "key", {"x": 1})


@pytest.mark.asyncio
async def test_kafka_consumer_routes_events(mocker):
    dummy_consumer = DummyAIOConsumer()
    dummy_consumer.messages = [
        DummyMessage({"event_type": "order.shipped", "order_id": "1"}),
        DummyMessage({"event_type": "order.cancelled", "order_id": "2"}),
    ]
    mocker.patch(
        "src.infrastructure.kafka.consumer.AIOKafkaConsumer",
        return_value=dummy_consumer,
    )

    consumer = KafkaConsumer(bootstrap_servers="localhost:9092")
    shipped = mocker.AsyncMock()
    cancelled = mocker.AsyncMock()

    await consumer.run(shipped, cancelled)

    shipped.assert_awaited_once()
    cancelled.assert_awaited_once()
    assert dummy_consumer.commits >= 2
