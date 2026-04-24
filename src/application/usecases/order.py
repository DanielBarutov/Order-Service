import uuid
from src.application.ports.capashino_client import CapashinoClientPort
from src.application.ports.uow import UnitOfWorkPort
from src.core.models import OrderEntity


class CreateOrderUseCase:
    def __init__(self, unit_of_work: UnitOfWorkPort, client: CapashinoClientPort):
        self._unit_of_work = unit_of_work
        self.client = client

    async def execute(self, order: OrderEntity) -> OrderEntity:
        async with self._unit_of_work() as uow:
            if order.idempotency_key:
                existing_order = await uow.orders.get_order_by_idempotency_key(
                    order.idempotency_key
                )
                if existing_order:
                    return existing_order
            item = await self.client.get_item(order.item_id)
            if item.available_qty < order.quantity:
                raise ValueError("Товара на складе недостаточно")
            order = await uow.orders.create_order(order)
            await uow.commit()
            return order


class GetOrderUseCase:
    def __init__(self, unit_of_work: UnitOfWorkPort):
        self._unit_of_work = unit_of_work

    async def execute(self, order_id: uuid.UUID) -> OrderEntity:
        async with self._unit_of_work() as uow:
            order = await uow.orders.get_order(order_id)
            return order
