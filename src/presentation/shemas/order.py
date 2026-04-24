import datetime
import uuid

import pydantic

from src.core.models import OrderStatusEnum


class CreateOrderRequest(pydantic.BaseModel):
    user_id: str
    quantity: int
    item_id: uuid.UUID
    idempotency_key: str | None = None


class CreateOrderResponse(pydantic.BaseModel):
    id: uuid.UUID
    user_id: str
    quantity: int
    item_id: uuid.UUID
    status: OrderStatusEnum
    created_at: datetime.datetime
    updated_at: datetime.datetime


class GetOrderResponse(pydantic.BaseModel):
    id: uuid.UUID
    user_id: str
    quantity: int
    item_id: uuid.UUID
    status: OrderStatusEnum
    created_at: datetime.datetime
    updated_at: datetime.datetime
