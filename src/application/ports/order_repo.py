from src.core.models import OrderEntity
import typing
import uuid


class OrderRepositoryPort(typing.Protocol):
    async def create_order(self, order: OrderEntity) -> OrderEntity: ...
    async def get_order(self, order_id: uuid.UUID) -> OrderEntity: ...
