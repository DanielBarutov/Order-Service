import asyncio

from src.application.ports.broker import KafkaProducerPort
from src.application.ports.capashino_client import NotificationClientPort
from src.application.ports.uow import UnitOfWorkPort
from src.core.models import OutboxEntity, OrderEntity, NotificationEntity


class OutboxWorker:
    def __init__(
        self,
        unit_of_work: UnitOfWorkPort,
        broker: KafkaProducerPort,
        notification_client: NotificationClientPort,
    ):
        self.unit_of_work = unit_of_work
        self.broker = broker
        self.notification_client = notification_client

    async def run(self) -> None:
        print("Outbox worker стартует через 10 секунд")
        await asyncio.sleep(10)
        while True:
            try:
                async with self.unit_of_work() as uow:
                    outbox_entities: list[
                        OutboxEntity
                    ] = await uow.outbox.get_pending_outbox()
                    if not outbox_entities:
                        print("Нет pending outbox, спим 10 секунд")
                        await asyncio.sleep(10)
                        continue
                    for outbox_entity in outbox_entities:
                        async with self.broker as broker:
                            await broker.send_message(
                                topic="student_system-order.events",
                                key=str(outbox_entity.id),
                                payload=outbox_entity.payload,
                            )
                        outbox_entity: OutboxEntity = outbox_entity.to_completed()
                        print(f"Outbox обновлен: {outbox_entity}")
                        await uow.outbox.update(outbox_entity)
                        order: OrderEntity = await uow.orders.get_order(
                            outbox_entity.payload["order_id"]
                        )
                        order = order.to_paid()
                        await uow.orders.update_order(order)
                        await uow.commit()
                        await self.notification_client.create_notification(
                            NotificationEntity(
                                message="Your order has been paid!",
                                reference_id=order.id,
                            ),
                            idempotency_key=order.idempotency_key + "_paid",
                        )
                        await asyncio.sleep(5)
                        print(
                            f"Outbox отправлен в репозиторий: {outbox_entity}, спим 5 секунд"
                        )
            except Exception as e:
                print(
                    f"Ошибка при отправке outbox: {e}, повторная попытка через 10 секунд"
                )
                await asyncio.sleep(10)
