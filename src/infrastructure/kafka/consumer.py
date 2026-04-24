import json
from aiokafka import AIOKafkaConsumer


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str):
        self._consumer = AIOKafkaConsumer(
            "student_system-shipment.events",
            bootstrap_servers=bootstrap_servers,
            group_id="order-service",
            enable_auto_commit=True,
            auto_offset_reset="earliest",
        )

    async def start(self) -> None:
        await self._consumer.start()

    async def stop(self) -> None:
        await self._consumer.stop()

    async def run(self, on_order_shipped, on_order_cancelled) -> None:
        async for msg in self._consumer:
            data = json.loads(msg.value.decode("utf-8"))
            event_type = data.get("event_type")

            if event_type == "order.shipped":
                await on_order_shipped(data)
            elif event_type == "order.cancelled":
                await on_order_cancelled(data)
            else:
                print(f"Неизвестное событие: {event_type}")
