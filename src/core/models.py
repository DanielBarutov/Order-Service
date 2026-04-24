import decimal
import uuid
import datetime
import dataclasses
import enum


class OrderStatusEnum(enum.Enum):
    NEW = "new"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


@dataclasses.dataclass
class OrderEntity:
    id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    user_id: str = dataclasses.field(default="")
    quantity: int = dataclasses.field(default=0)
    item_id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    idempotency_key: str | None = dataclasses.field(default=None)
    status: OrderStatusEnum = dataclasses.field(default=OrderStatusEnum.NEW)
    created_at: datetime.datetime = dataclasses.field(default_factory=utc_now)
    updated_at: datetime.datetime = dataclasses.field(default_factory=utc_now)

    def to_paid(self) -> "OrderEntity":
        return dataclasses.replace(
            self,
            status=OrderStatusEnum.PAID,
            updated_at=utc_now(),
        )

    def to_shipped(self) -> "OrderEntity":
        return dataclasses.replace(
            self,
            status=OrderStatusEnum.SHIPPED,
            updated_at=utc_now(),
        )

    def to_cancelled(self) -> "OrderEntity":
        return dataclasses.replace(
            self,
            status=OrderStatusEnum.CANCELLED,
            updated_at=utc_now(),
        )


@dataclasses.dataclass
class ItemEntity:
    id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    name: str = dataclasses.field(default="")
    price: decimal.Decimal = dataclasses.field(default=0)
    available_qty: int = dataclasses.field(default=0)
    created_at: datetime.datetime = dataclasses.field(default_factory=utc_now)


@dataclasses.dataclass
class PaymentEntity:
    id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    user_id: str = dataclasses.field(default="")
    order_id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    amount: decimal.Decimal = dataclasses.field(default=0)
    status: (
        str  # PaymentStatusEnum = dataclasses.field(default=PaymentStatusEnum.PENDING)
    )
    idempotency_key: str | None = dataclasses.field(default=None)
    created_at: datetime.datetime = dataclasses.field(default_factory=utc_now)


@dataclasses.dataclass
class NotificationEntity:
    id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    user_id: str = dataclasses.field(default="")
    message: str = dataclasses.field(default="")
    reference_id: uuid.UUID = dataclasses.field(default_factory=uuid.uuid4)
    created_at: datetime.datetime = dataclasses.field(default_factory=utc_now)
