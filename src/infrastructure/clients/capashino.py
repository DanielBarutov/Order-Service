import urllib.parse
import uuid

import httpx

from src.infrastructure.dto.item import ItemEntityResponse


class CapashinoClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    async def get_item(self, item_id: uuid.UUID) -> ItemEntityResponse:
        async with httpx.AsyncClient(timeout=10.0) as client:
            url = urllib.parse.urljoin(self.base_url, f"/api/catalog/items/{item_id}")
            headers = {"X-API-Key": self.api_key}

            response = await client.get(
                url,
                headers=headers,
            )
            response.raise_for_status()
            return ItemEntityResponse.model_validate(response.json())
