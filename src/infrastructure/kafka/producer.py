import json

from aiokafka import AIOKafkaProducer


class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers, acks="all"
        )

    async def start(self):
        await self._producer.start()

    async def stop(self):
        await self._producer.stop()

    async def publish_event(self, topic: str, key: str, payload: dict):
        await self._producer.send(
            topic=topic,
            key=key.encode("utf-8"),
            value=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        )
