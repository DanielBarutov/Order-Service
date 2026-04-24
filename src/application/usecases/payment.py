import uuid
import decimal

from src.application.ports.capashino_client import PaymentClientPort
from src.core.models import PaymentEntity


class CreatePaymentUseCase:
    def __init__(self, payment_client: PaymentClientPort):
        self.payment_client = payment_client

    async def execute(
        self,
        order_id: uuid.UUID,
        amount: decimal.Decimal,
        callback_url: None = None,
        idempotency_key: str | None = None,
    ) -> PaymentEntity:
        payment: PaymentEntity = await self.payment_client.create_payment(
            PaymentEntity(
                order_id=order_id,
                amount=amount,
                callback_url=callback_url,
                idempotency_key=idempotency_key,
            )
        )
        return payment
