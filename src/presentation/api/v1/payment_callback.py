import logging

from fastapi import APIRouter, Depends, status

from src.application.usecases.order import OrderCallbackUseCase
from src.presentation.deps.deps import order_callback_use_case
from src.presentation.shemas.callback_payment import PaymentCallbackRequestResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/orders/payment-callback", status_code=status.HTTP_200_OK)
async def payment_callback(
    request: PaymentCallbackRequestResponse,
    order_callback_use_case: OrderCallbackUseCase = Depends(order_callback_use_case),
):
    await order_callback_use_case.execute(
        request.order_id,
        request.status,
        request.error_message if request.error_message else None,
    )
    logger.info("Получен callback платежа: %s", request.model_dump(mode="json"))
    return {"message": "Payment callback received"}
