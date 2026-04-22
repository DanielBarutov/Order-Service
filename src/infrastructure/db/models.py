import datetime
import uuid

from sqlalchemy import UUID, String, Column, Integer, Enum, DateTime
from sqlalchemy.orm import DeclarativeBase

from src.core.models import OrderStatusEnum


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class Order(Base):
    __tablename__ = "orders"

    id = Column(UUID, primary_key=True, unique=True, default=uuid.uuid4)
    user_id = Column(String, nullable=False)
    quantity = Column(Integer)
    item_id = Column(UUID, nullable=False)
    status = Column(
        Enum(OrderStatusEnum, name="statusenum"),
        nullable=False,
        default=OrderStatusEnum.NEW,
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)
    updated_at = Column(
        DateTime(timezone=True), nullable=False, default=utc_now, onupdate=utc_now
    )
