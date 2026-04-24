import uuid

from fastapi import APIRouter, Depends, HTTPException, status


from src.application.usecases.order import CreateOrderUseCase, GetOrderUseCase
from src.core.models import OrderEntity
from src.presentation.deps.deps import create_order_use_case, get_order_use_case
from src.presentation.shemas.order import (
    CreateOrderRequest,
    CreateOrderResponse,
    GetOrderResponse,
)

router = APIRouter()


@router.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(
    order: CreateOrderRequest,
    use_case: CreateOrderUseCase = Depends(create_order_use_case),
) -> CreateOrderResponse:
    order_entity = OrderEntity(
        user_id=order.user_id,
        quantity=order.quantity,
        item_id=order.item_id,
        idempotency_key=order.idempotency_key or None,
    )
    try:
        created_order = await use_case.execute(order_entity)

        return CreateOrderResponse(
            id=created_order.id,
            user_id=created_order.user_id,
            quantity=created_order.quantity,
            item_id=created_order.item_id,
            status=created_order.status,
            created_at=created_order.created_at,
            updated_at=created_order.updated_at,
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Товар на складе недостаточно ):")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка сервера: {e}")


@router.get("/orders/{order_id}")
async def get_order(
    order_id: uuid.UUID,
    use_case: GetOrderUseCase = Depends(get_order_use_case),
) -> GetOrderResponse:
    getted_order = await use_case.execute(order_id)
    return GetOrderResponse(
        id=getted_order.id,
        user_id=getted_order.user_id,
        quantity=getted_order.quantity,
        item_id=getted_order.item_id,
        status=getted_order.status,
        created_at=getted_order.created_at,
        updated_at=getted_order.updated_at,
    )
