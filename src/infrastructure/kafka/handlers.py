import datetime
import uuid

from core.models import InboxStatusEnum, InboxEntity
from infrastructure.uow import UnitOfWork


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


async def handle_order_shipped(event: dict, unit_of_work: UnitOfWork) -> None:
    print("Получено событие о доставке заказа и записываем в outbox")
    async with unit_of_work() as uow:
        inbox = InboxEntity(
            id=uuid.uuid4(),
            event_type="order.shipped",
            payload=event,
            status=InboxStatusEnum.PENDING,
            created_at=utc_now(),
        )
        await uow.inbox.create(inbox)
        await uow.commit()


async def handle_order_cancelled(event: dict, unit_of_work: UnitOfWork) -> None:
    print("Получено событие о отмене заказа")
    async with unit_of_work() as uow:
        inbox = InboxEntity(
            id=uuid.uuid4(),
            event_type="order.cancelled",
            payload=event,
            status=InboxStatusEnum.PENDING,
            created_at=utc_now(),
        )
        await uow.inbox.create(inbox)
        await uow.commit()
