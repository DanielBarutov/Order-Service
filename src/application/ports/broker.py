import typing


class KafkaProducerPort(typing.Protocol):
    async def send_message(
        self, topic: str, key: str, payload: dict[str, typing.Any]
    ) -> None: ...
