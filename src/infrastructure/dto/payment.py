import datetime
import uuid
import decimal

import pydantic


class PaymentRequest(pydantic.BaseModel):
    order_id: uuid.UUID
    amount: decimal.Decimal
    callback_url: pydantic.HttpUrl
    idempotency_key: uuid.UUID | None = None


class PaymentResponse(pydantic.BaseModel):
    id: uuid.UUID
    user_id: str
    order_id: uuid.UUID
    amount: decimal.Decimal
    status: str
    idempotency_key: uuid.UUID | None = None
    created_at: datetime.datetime
