import decimal
import pydantic
import uuid


class PaymentCallbackRequestResponse(pydantic.BaseModel):
    payment_id: uuid.UUID
    order_id: uuid.UUID
    status: str
    amount: decimal.Decimal
    error_message: str | None = None
