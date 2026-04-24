import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import OrderEntity
from src.infrastructure.db.models import Order as OrderModel


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_entity(order: OrderModel) -> OrderEntity:
        return OrderEntity(
            id=order.id,
            user_id=order.user_id,
            quantity=order.quantity,
            item_id=order.item_id,
            idempotency_key=order.idempotency_key or None,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

    async def create_order(self, order: OrderEntity) -> OrderEntity:
        order_model = OrderModel(
            id=order.id,
            user_id=order.user_id,
            quantity=order.quantity,
            item_id=order.item_id,
            idempotency_key=order.idempotency_key or None,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
        self.session.add(order_model)
        return order

    async def get_order(self, order_id: uuid.UUID) -> OrderEntity:
        order_model = await self.session.execute(
            select(OrderModel).where(OrderModel.id == order_id)
        )
        order: OrderModel = order_model.scalar()
        return self._to_entity(order)

    async def get_order_by_idempotency_key(
        self, idempotency_key: str
    ) -> OrderEntity | None:
        order_model = await self.session.execute(
            select(OrderModel).where(OrderModel.idempotency_key == idempotency_key)
        )
        order: OrderModel = order_model.scalar()
        return self._to_entity(order) if order else None

    async def update_order(self, order: OrderEntity) -> None:
        order_model = OrderModel(
            id=order.id,
            user_id=order.user_id,
            quantity=order.quantity,
            item_id=order.item_id,
            idempotency_key=order.idempotency_key or None,
            status=order.status,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
        print("Мерджим заказ в базу данных", order_model)
        await self.session.merge(order_model)
        print("Заказ мерджед")
