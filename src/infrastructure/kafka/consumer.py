import json
import typing
import logging

from aiokafka import AIOKafkaConsumer

logger = logging.getLogger(__name__)


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
                    logger.info(
                        "Было получено сообщение, но такого статуса мы не обрабатываем: %s",
                        event_type,
                    )
            except Exception as e:
                logger.error("Ошибка при обработке сообщения в Consumer.Kafka: %s", e)
                await self._consumer.commit()
                continue
            finally:
                await self._consumer.commit()


class FakeKafkaConsumer:
    def __init__(self):
        self._consumer = None

    async def start(self) -> None:
        pass

    async def stop(self) -> None:
        pass

    async def run(
        self,
        on_order_shipped: typing.Callable[[dict], None],
        on_order_cancelled: typing.Callable[[dict], None],
    ) -> None:
        pass
