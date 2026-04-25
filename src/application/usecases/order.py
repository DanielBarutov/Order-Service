import uuid
from src.application.ports.capashino_client import (
    StorageClientPort,
    PaymentClientPort,
    NotificationClientPort,
)
from src.application.ports.uow import UnitOfWorkPort
from src.application.ports.broker import KafkaProducerPort
from src.core.models import OrderEntity, ItemEntity, PaymentEntity


class CreateOrderUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWorkPort,
        storage_client: StorageClientPort,
        payment_client: PaymentClientPort,
        notification_client: NotificationClientPort,
    ):
        self._unit_of_work = unit_of_work
        self.storage_client = storage_client
        self.payment_client = payment_client
        self.notification_client = notification_client

    async def execute(self, order: OrderEntity) -> OrderEntity:
        async with self._unit_of_work() as uow:
            if order.idempotency_key:
                existing_order = await uow.orders.get_order_by_idempotency_key(
                    order.idempotency_key
                )
                if existing_order:
                    return existing_order
            item: ItemEntity = await self.storage_client.get_item(order.item_id)
            if item.available_qty < order.quantity:
                raise ValueError("Товара на складе недостаточно")
            await self.payment_client.create_payment(
                PaymentEntity(
                    order_id=order.id,
                    amount=item.price * order.quantity,
                    idempotency_key=order.idempotency_key,
                )
            )
            order: OrderEntity = await uow.orders.create_order(order)
            await uow.commit()
            return order


class GetOrderUseCase:
    def __init__(self, unit_of_work: UnitOfWorkPort):
        self._unit_of_work = unit_of_work

    async def execute(self, order_id: uuid.UUID) -> OrderEntity:
        async with self._unit_of_work() as uow:
            order: OrderEntity = await uow.orders.get_order(order_id)
            return order


class UpdateOrderCallbackUseCase:
    def __init__(
        self, unit_of_work: UnitOfWorkPort, broker: KafkaProducerPort | None = None
    ):
        self._unit_of_work = unit_of_work
        self.broker = broker

    async def execute(
        self, order_id: uuid.UUID, status: str, error_message: str | None = None
    ) -> OrderEntity:
        async with self._unit_of_work() as uow:
            event_payload = {}
            print(
                f"Update order use case started: {order_id}, {status}, {error_message}"
            )
            if status == "succeeded":
                print("Обновляем заказ на paid")
                order = await uow.orders.get_order(order_id)
                order = order.to_paid()
                await uow.orders.update_order(order)
                await uow.commit()
                print("Публикуем событие на paid")
                event_payload = {
                    "event_type": "order.paid",
                    "order_id": str(order.id),
                    "item_id": str(order.item_id),
                    "quantity": order.quantity,
                    "idempotency_key": order.idempotency_key,
                }
                if self.broker:
                    async with self.broker as broker:
                        await broker.send_message(
                            topic="student_system-order.events",
                            key=str(order.id),
                            payload=event_payload,
                        )

            else:
                print(f"Неизвестный статус: {status}")
                raise ValueError(f"Неизвестный статус: {status}")
            return order


class UpdateOrderUseCase:
    def __init__(self, unit_of_work: UnitOfWorkPort):
        self._unit_of_work = unit_of_work

    async def execute(
        self, order_id: uuid.UUID, status: str, error_message: str | None = None
    ) -> OrderEntity:
        async with self._unit_of_work() as uow:
            order = await uow.orders.get_order(order_id)
            order = (
                order.to_cancelled()
                if status == "cancelled"
                else order.to_shipped()
                if status == "shipped"
                else order.to_paid()
                if status == "paid"
                else order
            )
            await uow.orders.update_order(order)
            await uow.commit()
            return order
