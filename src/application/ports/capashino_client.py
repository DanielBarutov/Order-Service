import typing
import uuid


class CapashinoClientPort(typing.Protocol):
    def get_item(self, item_id: uuid.UUID) -> typing.Any: ...
