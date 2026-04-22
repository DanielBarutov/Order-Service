import datetime
import decimal
import uuid

import pydantic


class ItemEntityResponse(pydantic.BaseModel):
    id: uuid.UUID
    name: str
    price: decimal.Decimal
    available_qty: int
    created_at: datetime.datetime
