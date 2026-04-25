import asyncio

from src.application.ports.capashino_client import NotificationClientPort
from src.application.ports.uow import UnitOfWorkPort
from src.core.models import InboxEntity, OrderEntity, NotificationEntity


class InboxWorker:
    def __init__(
        self, unit_of_work: UnitOfWorkPort, notification_client: NotificationClientPort
    ):
        self.unit_of_work = unit_of_work
        self.notification_client = notification_client

    async def run(self) -> None:
        while True:
            try:
                async with self.unit_of_work() as uow:
                    inbox_entities: list[
                        InboxEntity
                    ] = await uow.inbox.get_pending_inbox()
                    if not inbox_entities:
                        print("Нет pending inbox, спим 10 секунд")
                        await asyncio.sleep(10)
                        continue
                    for inbox_entity in inbox_entities:
                        print(f"Inbox получен: {inbox_entity}")
                        inbox_entity: InboxEntity = inbox_entity.to_completed()
                        await uow.inbox.update(inbox_entity)

                        order: OrderEntity = await uow.orders.get_order(
                            inbox_entity.payload["order_id"]
                        )
                        if inbox_entity.event_type == "order.shipped":
                            order = order.to_shipped()
                        elif inbox_entity.event_type == "order.cancelled":
                            order = order.to_cancelled()
                        else:
                            print(f"Неизвестный event_type: {inbox_entity.event_type}")
                            continue
                        await uow.orders.update_order(order)
                        await uow.commit()
                        await self.notification_client.create_notification(
                            NotificationEntity(
                                user_id=order.user_id,
                                message=f"Your order has been {inbox_entity.event_type[6:]}!",
                                reference_id=order.id,
                            ),
                            idempotency_key=order.idempotency_key,
                        )
                        print(f"Inbox обновлен: {inbox_entity}")
            except Exception as e:
                print(f"Ошибка при получении inbox: {e}")
