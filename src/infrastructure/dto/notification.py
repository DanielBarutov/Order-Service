import uuid
import datetime

import pydantic


class NotificationRequest(pydantic.BaseModel):
    message: str
    reference_id: uuid.UUID
    idempotency_key: str | None = None


class NotificationResponse(pydantic.BaseModel):
    id: uuid.UUID
    user_id: str
    message: str
    reference_id: uuid.UUID
    created_at: datetime.datetime
