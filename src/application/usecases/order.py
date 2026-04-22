import uuid
from src.application.ports.capashino_client import CapashinoClientPort
from src.application.ports.order_repo import OrderRepositoryPort
from src.core.models import OrderEntity


class CreateOrderUseCase:
    def __init__(self, repository: OrderRepositoryPort, client: CapashinoClientPort):
        self.repository = repository
        self.client = client

    async def execute(self, order: OrderEntity) -> OrderEntity:
        item = await self.client.get_item(order.item_id)
        if item.available_qty < order.quantity:
            raise ValueError("Item quantity is not enough")
        order = await self.repository.create_order(order)
        return order


class GetOrderUseCase:
    def __init__(self, repository: OrderRepositoryPort):
        self.repository = repository

    async def execute(self, order_id: uuid.UUID) -> OrderEntity:
        order = await self.repository.get_order(order_id)
        return order
