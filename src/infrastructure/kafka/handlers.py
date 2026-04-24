import uuid
from src.infrastructure.ports.update_usecase import UpdateOrderUseCasePort


async def handle_order_shipped(event: dict, update_uc: UpdateOrderUseCasePort) -> None:
    print(f"Handling order shipped event from handlers.py: {event}")
    await update_uc.execute(
        order_id=uuid.UUID(event["order_id"]),
        status="shipped",
    )


async def handle_order_cancelled(
    event: dict, update_uc: UpdateOrderUseCasePort
) -> None:
    print(f"Handling order cancelled event from handlers.py: {event}")
    await update_uc.execute(
        order_id=uuid.UUID(event["order_id"]),
        status="cancelled",
        error_message=event.get("reason"),
    )
