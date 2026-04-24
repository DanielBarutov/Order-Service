import json

from aiokafka import AIOKafkaProducer


class KafkaProducer:
    def __init__(self, bootstrap_servers: str) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers, acks="all"
        )

    async def start(self) -> None:
        if not self._producer:
            await self._producer.start()
        else:
            print("Producer already started")

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()

    async def publish_event(self, topic: str, key: str, payload: dict) -> None:
        try:
            print(
                f"Publishing event to topic from producer.py: {topic}, key: {key}, payload: {payload}"
            )
            await self._producer.send_and_wait(
                topic=topic,
                key=key.encode("utf-8"),
                value=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            )
        except Exception as e:
            print(f"Error publishing event: {e}")
            raise
