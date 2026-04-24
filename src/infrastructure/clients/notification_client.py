import httpx
import urllib.parse

from src.infrastructure.dto.payment import PaymentRequest, PaymentResponse
from src.infrastructure.clients.tools import retry_on_error


class NotificationClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
    ):
        self.base_url = base_url
        self.api_key = api_key

    @retry_on_error(max_retries=3)
    async def create_payment(self, payment: PaymentRequest) -> PaymentResponse:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = urllib.parse.urljoin(self.base_url, "/api/payments")
            headers = {"X-API-Key": self.api_key}
            response = await client.post(
                url,
                json=payment.model_dump(),
                headers=headers,
            )
            response.raise_for_status()
            result: PaymentResponse = PaymentResponse.model_validate(response.json())
            return result
