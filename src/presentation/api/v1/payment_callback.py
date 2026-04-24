from fastapi import APIRouter, status

from src.presentation.shemas.callback_payment import PaymentCallbackRequestResponse

router = APIRouter()


@router.post("/orders/payment-callback", status_code=status.HTTP_200_OK)
async def payment_callback(request: PaymentCallbackRequestResponse):
    # Обновить статус заказа на PAID при успешном платеже
    # Обновить статус заказа на CANCELLED при неуспешном платеже
    # Обеспечить идемпотентность обработки callback'ов
    return {"message": "Payment callback received"}
