import json
import typing
from aiokafka import AIOKafkaConsumer


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str):
        self._consumer = AIOKafkaConsumer(
            "student_system-shipment.events",
            bootstrap_servers=bootstrap_servers,
            group_id="order-service",
            enable_auto_commit=False,
            auto_offset_reset="latest",
        )

    async def start(self) -> None:
        await self._consumer.start()

    async def stop(self) -> None:
        await self._consumer.stop()

    async def run(
        self,
        on_order_shipped: typing.Callable[[dict], None],
        on_order_cancelled: typing.Callable[[dict], None],
    ) -> None:
        async for msg in self._consumer:
            data = json.loads(msg.value.decode("utf-8"))
            event_type = data.get("event_type")
            try:
                if event_type == "order.shipped":
                    await on_order_shipped(data)
                    await self._consumer.commit()
                elif event_type == "order.cancelled":
                    await on_order_cancelled(data)
                    await self._consumer.commit()
                else:
                    print(f"Неизвестное событие: {event_type}")
            except Exception as e:
                print(f"Ошибка при обработке события: {e}, Без остановки консьюмера")
                await self._consumer.commit()
                continue
            finally:
                await self._consumer.commit()
