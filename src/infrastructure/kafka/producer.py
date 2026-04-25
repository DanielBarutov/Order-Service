import json
import typing

from aiokafka import AIOKafkaProducer


class KafkaProducer:
    def __init__(self, bootstrap_servers: str) -> None:
        self._producer: AIOKafkaProducer | None = None
        self._bootstrap_servers = bootstrap_servers

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=self._bootstrap_servers, acks="all"
        )
        await self._producer.start()

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()
            self._producer = None

    async def send_message(
        self, topic: str, key: str, payload: dict[str, typing.Any]
    ) -> None:
        if not self._producer:
            raise RuntimeError("Producer not started")
        try:
            print(
                f"Publishing event to topic from producer.py: {topic}, key: {key}, payload: {payload}"
            )
            metadata = await self._producer.send_and_wait(
                topic=topic,
                key=key.encode("utf-8"),
                value=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            )
            print(
                f"sent topic={metadata.topic} partition={metadata.partition} offset={metadata.offset}"
            )
        except Exception as e:
            print(f"Error publishing event: {e}")
            raise

    async def __aenter__(self) -> "KafkaProducer":
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.stop()
