import uuid
import urllib.parse

import httpx

from src.core.models import ItemEntity
from src.infrastructure.dto.item import ItemEntityResponse


class StorageClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    @staticmethod
    def _to_entity(item: ItemEntityResponse) -> ItemEntity:
        return ItemEntity(
            id=item.id,
            name=item.name,
            price=item.price,
            available_qty=item.available_qty,
            created_at=item.created_at,
        )

    async def get_item(self, item_id: uuid.UUID) -> ItemEntityResponse:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = urllib.parse.urljoin(self.base_url, f"/api/catalog/items/{item_id}")
            headers = {"X-API-Key": self.api_key}

            response = await client.get(
                url,
                headers=headers,
            )
            response.raise_for_status()
            result: ItemEntityResponse = ItemEntityResponse.model_validate(
                response.json()
            )
            return self._to_entity(result)
