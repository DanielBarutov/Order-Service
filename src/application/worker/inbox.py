import uuid
import logging

import asyncio

from src.application.ports.capashino_client import NotificationClientPort
from src.application.ports.uow import UnitOfWorkPort
from src.core.models import InboxEntity, OrderEntity, NotificationEntity

logger = logging.getLogger(__name__)


class InboxWorker:
    def __init__(
        self, unit_of_work: UnitOfWorkPort, notification_client: NotificationClientPort
    ):
        self.unit_of_work = unit_of_work
        self.notification_client = notification_client

    async def run(self) -> None:
        logger.info("InboxWorker старутет через 10 секунд...")
        await asyncio.sleep(10)
        while True:
            try:
                async with self.unit_of_work() as uow:
                    inbox_entities: list[
                        InboxEntity
                    ] = await uow.inbox.get_pending_inbox()
                    if not inbox_entities:
                        await asyncio.sleep(10)
                        continue
                    for inbox_entity in inbox_entities:
                        try:
                            order: OrderEntity = await uow.orders.get_order(
                                uuid.UUID(inbox_entity.payload["order_id"])
                            )
                            if order is None:
                                if inbox_entity.retry > 3:
                                    inbox_entity: InboxEntity = inbox_entity.to_failed()
                                else:
                                    inbox_entity.retry += 1
                            else:
                                inbox_entity: InboxEntity = inbox_entity.to_completed()
                                if inbox_entity.event_type == "order.shipped":
                                    order = order.to_shipped()
                                    text = "SHIPPED"
                                elif inbox_entity.event_type == "order.cancelled":
                                    order = order.to_cancelled()
                                    text = "CANCELLED"
                                else:
                                    logger.info(
                                        "Был получен статус, который мы не обрабатываем: %s",
                                        inbox_entity.event_type,
                                    )
                                    continue
                        except Exception as e:
                            logger.error(
                                "Ошибка при обработке Inbox, но продолжаем работу: %s",
                                e,
                            )
                            continue
                        await uow.inbox.update(inbox_entity)
                        await uow.orders.update_order(order)
                        await uow.commit()
                        await self.notification_client.create_notification(
                            NotificationEntity(
                                user_id=order.user_id,
                                message=text,
                                reference_id=order.id,
                            ),
                            idempotency_key=order.idempotency_key
                            + "_"
                            + inbox_entity.event_type[6:],
                        )
                        logger.info(
                            "InboxWorker - Было обработано %s задач",
                            len(inbox_entities),
                        )
            except Exception as e:
                logger.error("InboxWorker - Ошибка при обработке inbox-задач: %s", e)
                await asyncio.sleep(10)
