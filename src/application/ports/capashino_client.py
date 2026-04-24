import typing
import uuid

from src.core.models import PaymentEntity, NotificationEntity


class StorageClientPort(typing.Protocol):
    async def get_item(self, item_id: uuid.UUID) -> typing.Any: ...


class PaymentClientPort(typing.Protocol):
    async def create_payment(self, payment: PaymentEntity) -> PaymentEntity: ...


class NotificationClientPort(typing.Protocol):
    async def send_notification(
        self, notification: NotificationEntity
    ) -> NotificationEntity: ...
