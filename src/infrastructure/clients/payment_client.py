import urllib.parse

import httpx

from src.core.models import PaymentEntity
from src.infrastructure.dto.payment import PaymentRequest, PaymentResponse
from src.infrastructure.clients.tools import retry_on_error


class PaymentClient:
    def __init__(self, base_url: str, api_key: str, callback_url: str):
        self.base_url = base_url
        self.api_key = api_key
        self.callback_url = callback_url

    @staticmethod
    def _to_entity(payment: PaymentResponse) -> PaymentEntity:
        return PaymentEntity(
            id=str(payment.id),
            user_id=payment.user_id,
            order_id=str(payment.order_id),
            amount=payment.amount,
            status=payment.status,
            idempotency_key=payment.idempotency_key,
            created_at=payment.created_at,
        )

    @retry_on_error(max_retries=3)
    async def create_payment(self, payment: PaymentEntity) -> PaymentEntity:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = urllib.parse.urljoin(self.base_url, "/api/payments")
            headers = {"X-API-Key": self.api_key}
            payment_request = PaymentRequest(
                order_id=str(payment.order_id),
                amount=payment.amount,
                callback_url=self.callback_url,
                idempotency_key=payment.idempotency_key,
            )
            response = await client.post(
                url,
                json=payment_request.model_dump(mode="json"),
                headers=headers,
            )
            response.raise_for_status()
            result: PaymentResponse = PaymentResponse.model_validate(response.json())
            return self._to_entity(result)
