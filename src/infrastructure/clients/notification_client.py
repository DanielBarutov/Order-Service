import logging
import urllib.parse

import httpx

from src.core.models import NotificationEntity
from src.infrastructure.dto.notification import (
    NotificationRequest,
    NotificationResponse,
)
from src.infrastructure.clients.tools import retry_on_error

logger = logging.getLogger(__name__)


class NotificationClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
    ):
        self.base_url = base_url
        self.api_key = api_key

    @staticmethod
    def _to_entity(notification: NotificationResponse) -> NotificationEntity:
        return NotificationEntity(
            id=notification.id,
            user_id=notification.user_id,
            message=notification.message,
            reference_id=notification.reference_id,
            created_at=notification.created_at,
        )

    @retry_on_error(max_retries=3)
    async def create_notification(
        self, notification: NotificationEntity, idempotency_key: str | None = None
    ) -> NotificationResponse:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = urllib.parse.urljoin(self.base_url, "/api/notifications")
            headers = {"X-API-Key": self.api_key}
            payload = NotificationRequest(
                message=notification.message,
                reference_id=notification.reference_id,
                idempotency_key=idempotency_key,
            )
            response = await client.post(
                url,
                json=payload.model_dump(mode="json"),
                headers=headers,
            )
            response.raise_for_status()
            logger.info(
                "Было отправлено уведомление, тип: %s, ключ_идемпотентности: %s",
                notification.message,
                idempotency_key,
            )
            result: NotificationResponse = NotificationResponse.model_validate(
                response.json()
            )
            return self._to_entity(result)
