import datetime
import uuid
import logging

from src.core.models import InboxStatusEnum, InboxEntity
from src.infrastructure.uow import UnitOfWork

logger = logging.getLogger(__name__)


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


async def handle_order_shipped(event: dict, unit_of_work: UnitOfWork) -> None:
    logger.info("Получено сообщение о доставке заказа: %s", event)
    async with unit_of_work() as uow:
        try:
            inbox = InboxEntity(
                id=uuid.uuid4(),
                event_type="order.shipped",
                payload=event,
                status=InboxStatusEnum.PENDING,
                retry=0,
                created_at=utc_now(),
            )
            await uow.inbox.create(inbox)
            await uow.commit()
        except Exception as e:
            logger.error("Ошибка при создании Inbox с событием доставки: %s", e)
            raise e


async def handle_order_cancelled(event: dict, unit_of_work: UnitOfWork) -> None:
    logger.info("Получено сообщение об отмене заказа: %s", event)
    async with unit_of_work() as uow:
        try:
            inbox = InboxEntity(
                id=uuid.uuid4(),
                event_type="order.cancelled",
                payload=event,
                status=InboxStatusEnum.PENDING,
                created_at=utc_now(),
            )
            await uow.inbox.create(inbox)
            await uow.commit()
        except Exception as e:
            logger.error("Ошибка при создании Inbox с событием доставки: %s", e)
            raise e
