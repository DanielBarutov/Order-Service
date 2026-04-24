import typing
import uuid


class CapashinoClientPort(typing.Protocol):
    async def get_item(self, item_id: uuid.UUID) -> typing.Any: ...
