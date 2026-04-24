import urllib.parse

import httpx

from src.infrastructure.dto.payment import PaymentRequest, PaymentResponse
from src.infrastructure.clients.tools import retry_on_error


class PaymentClient:
    def __init__(self, base_url: str, api_key: str, callback_url: str):
        self.base_url = base_url
        self.api_key = api_key
        self.callback_url = callback_url

    @retry_on_error(max_retries=3)
    async def create_payment(self, payment: PaymentRequest) -> PaymentResponse:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = urllib.parse.urljoin(self.base_url, "/api/payments")
            headers = {"X-API-Key": self.api_key}
            payment.callback_url = self.callback_url
            response = await client.post(
                url,
                json=payment.model_dump(),
                headers=headers,
            )
            response.raise_for_status()
            return PaymentResponse.model_validate(response.json())
