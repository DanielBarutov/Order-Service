import typing


class KafkaProducerPort(typing.Protocol):
    async def publish_event(self, topic: str, key: str, payload: dict) -> None: ...
