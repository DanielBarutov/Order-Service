import typing


class KafkaProducerPort(typing.Protocol):
    async def _publish_event(self, topic: str, key: str, payload: dict) -> None: ...
