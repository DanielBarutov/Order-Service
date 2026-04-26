import contextlib
import datetime
import decimal
import uuid

import pytest

from src.application.usecases.order import (
    CreateOrderUseCase,
    GetOrderUseCase,
    OrderCallbackUseCase,
)
from src.core.models import ItemEntity, OrderEntity, OrderStatusEnum


class DummyUow:
    def __init__(self):
        self.orders = type("OrdersRepo", (), {})()
        self.outbox = type("OutboxRepo", (), {})()
        self.commit = None


class DummyUowFactory:
    def __init__(self, uow):
        self._uow = uow

    @contextlib.asynccontextmanager
    async def __call__(self):
        yield self._uow


@pytest.mark.asyncio
async def test_create_order_usecase_happy_path(mocker):
    uow = DummyUow()
    uow.orders.get_order_by_idempotency_key = mocker.AsyncMock(return_value=None)
    created_order = OrderEntity(
        user_id="user_1",
        quantity=2,
        item_id=uuid.uuid4(),
        idempotency_key="idem-key",
    )
    uow.orders.create_order = mocker.AsyncMock(return_value=created_order)
    uow.commit = mocker.AsyncMock()
    uow_factory = DummyUowFactory(uow)

    storage_client = mocker.Mock()
    storage_client.get_item = mocker.AsyncMock(
        return_value=ItemEntity(
            id=created_order.item_id,
            name="Item",
            price=decimal.Decimal("100"),
            available_qty=5,
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
    )
    payment_client = mocker.Mock()
    payment_client.create_payment = mocker.AsyncMock()
    notification_client = mocker.Mock()
    notification_client.create_notification = mocker.AsyncMock()

    usecase = CreateOrderUseCase(
        unit_of_work=uow_factory,
        storage_client=storage_client,
        payment_client=payment_client,
        notification_client=notification_client,
    )

    result = await usecase.execute(created_order)

    assert result == created_order
    uow.orders.create_order.assert_awaited_once()
    uow.commit.assert_awaited_once()
    payment_client.create_payment.assert_awaited_once()
    notification_client.create_notification.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_order_usecase_returns_existing_by_idempotency(mocker):
    existing = OrderEntity(user_id="user_1", quantity=1, item_id=uuid.uuid4())
    uow = DummyUow()
    uow.orders.get_order_by_idempotency_key = mocker.AsyncMock(return_value=existing)
    uow.orders.create_order = mocker.AsyncMock()
    uow.commit = mocker.AsyncMock()
    uow_factory = DummyUowFactory(uow)

    storage_client = mocker.Mock()
    payment_client = mocker.Mock()
    notification_client = mocker.Mock()

    usecase = CreateOrderUseCase(
        unit_of_work=uow_factory,
        storage_client=storage_client,
        payment_client=payment_client,
        notification_client=notification_client,
    )

    result = await usecase.execute(
        OrderEntity(
            user_id="user_1",
            quantity=1,
            item_id=uuid.uuid4(),
            idempotency_key="same-key",
        )
    )

    assert result == existing
    uow.orders.create_order.assert_not_called()


@pytest.mark.asyncio
async def test_create_order_usecase_raises_when_not_enough_stock(mocker):
    uow = DummyUow()
    uow.orders.get_order_by_idempotency_key = mocker.AsyncMock(return_value=None)
    uow.orders.create_order = mocker.AsyncMock()
    uow.commit = mocker.AsyncMock()
    uow_factory = DummyUowFactory(uow)

    storage_client = mocker.Mock()
    storage_client.get_item = mocker.AsyncMock(
        return_value=ItemEntity(
            id=uuid.uuid4(),
            name="Item",
            price=decimal.Decimal("100"),
            available_qty=0,
            created_at=datetime.datetime.now(datetime.timezone.utc),
        )
    )
    payment_client = mocker.Mock()
    notification_client = mocker.Mock()

    usecase = CreateOrderUseCase(
        unit_of_work=uow_factory,
        storage_client=storage_client,
        payment_client=payment_client,
        notification_client=notification_client,
    )

    with pytest.raises(ValueError):
        await usecase.execute(
            OrderEntity(user_id="u", quantity=1, item_id=uuid.uuid4())
        )


@pytest.mark.asyncio
async def test_get_order_usecase_returns_order(mocker):
    order = OrderEntity(user_id="user_1", quantity=2, item_id=uuid.uuid4())
    uow = DummyUow()
    uow.orders.get_order = mocker.AsyncMock(return_value=order)
    uow_factory = DummyUowFactory(uow)

    usecase = GetOrderUseCase(unit_of_work=uow_factory)
    result = await usecase.execute(order.id)

    assert result == order
    uow.orders.get_order.assert_awaited_once_with(order.id)


@pytest.mark.asyncio
async def test_order_callback_usecase_creates_outbox_event(mocker):
    order = OrderEntity(
        user_id="user_1",
        quantity=2,
        item_id=uuid.uuid4(),
        idempotency_key="idem",
        status=OrderStatusEnum.PAID,
    )
    uow = DummyUow()
    uow.orders.get_order = mocker.AsyncMock(return_value=order)
    uow.outbox.create = mocker.AsyncMock()
    uow.commit = mocker.AsyncMock()
    uow_factory = DummyUowFactory(uow)

    usecase = OrderCallbackUseCase(unit_of_work=uow_factory)
    result = await usecase.execute(order.id, "succeeded")

    assert result == order
    uow.outbox.create.assert_awaited_once()
    uow.commit.assert_awaited_once()
