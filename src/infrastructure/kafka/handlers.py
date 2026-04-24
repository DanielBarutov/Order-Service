import uuid
from src.infrastructure.ports.update_usecase import UpdateOrderUseCasePort


async def handle_order_shipped(event: dict, update_uc: UpdateOrderUseCasePort) -> None:
    await update_uc.execute(
        order_id=uuid.UUID(event["order_id"]),
        status="shipped",
    )


async def handle_order_cancelled(
    event: dict, update_uc: UpdateOrderUseCasePort
) -> None:
    await update_uc.execute(
        order_id=uuid.UUID(event["order_id"]),
        status="cancelled",
        error_message=event.get("reason"),
    )
