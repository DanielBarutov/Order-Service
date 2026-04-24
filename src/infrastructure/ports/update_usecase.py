import typing
import uuid

from src.core.models import OrderEntity


class UpdateOrderUseCasePort(typing.Protocol):
    async def execute(
        self, order_id: uuid.UUID, status: str, error_message: str | None = None
    ) -> OrderEntity: ...
