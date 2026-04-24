from fastapi import APIRouter, Depends, status

from src.application.usecases.order import UpdateOrderUseCase
from src.presentation.deps.deps import update_order_use_case
from src.presentation.shemas.callback_payment import PaymentCallbackRequestResponse

router = APIRouter()


@router.post("/orders/payment-callback", status_code=status.HTTP_200_OK)
async def payment_callback(
    request: PaymentCallbackRequestResponse,
    update_order_use_case: UpdateOrderUseCase = Depends(update_order_use_case),
):
    await update_order_use_case.execute(request.order_id, request.status)
    print("Получен callback платежа:", request.model_dump(mode="json"))
    return {"message": "Payment callback received"}
