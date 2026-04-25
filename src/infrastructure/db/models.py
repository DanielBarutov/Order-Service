import datetime
import uuid

from sqlalchemy import UUID, String, Column, Integer, Enum, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase

from src.core.models import OrderStatusEnum
from src.core.models import InboxStatusEnum
from src.core.models import OutboxStatusEnum


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID, primary_key=True, unique=True, default=lambda: uuid.uuid4())
    user_id = Column(String, nullable=False)
    quantity = Column(Integer)
    item_id = Column(UUID, nullable=False)
    idempotency_key = Column(String, nullable=True, unique=True)
    status = Column(
        Enum(OrderStatusEnum, name="statusenum"),
        nullable=False,
        default=OrderStatusEnum.NEW,
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )


class Inbox(Base):
    __tablename__ = "inbox"

    id = Column(UUID, primary_key=True, unique=True, default=lambda: uuid.uuid4())
    event_id = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(
        Enum(InboxStatusEnum, name="inboxstatusenum"),
        nullable=False,
        default=InboxStatusEnum.PENDING,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class Outbox(Base):
    __tablename__ = "outbox"

    id = Column(UUID, primary_key=True, unique=True, default=lambda: uuid.uuid4())
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(
        Enum(OutboxStatusEnum, name="outboxstatusenum"),
        nullable=False,
        default=OutboxStatusEnum.PENDING,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
