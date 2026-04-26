import asyncio
import contextlib
import uuid

import pytest

from src.application.worker.inbox import InboxWorker
from src.application.worker.outbox import OutboxWorker
from src.core.models import InboxEntity, OutboxEntity


class DummyBroker:
    def __init__(self, mocker):
        self.send_message = mocker.AsyncMock()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None


class DummyUow:
    def __init__(self, mocker):
        self.orders = mocker.Mock()
        self.outbox = mocker.Mock()
        self.inbox = mocker.Mock()
        self.commit = mocker.AsyncMock()


class DummyUowFactory:
    def __init__(self, uow):
        self._uow = uow

    @contextlib.asynccontextmanager
    async def __call__(self):
        yield self._uow


@pytest.mark.asyncio
async def test_outbox_worker_processes_pending_entities(mocker, monkeypatch):
    uow = DummyUow(mocker)
    entity = OutboxEntity(
        event_type="order.paid",
        payload={"order_id": str(uuid.uuid4())},
    )
    updated_order = mocker.Mock(
        id=uuid.uuid4(),
        user_id="user_1",
        idempotency_key="idem",
        to_paid=mocker.Mock(),
    )
    updated_order.to_paid.return_value = updated_order
    uow.outbox.get_pending_outbox = mocker.AsyncMock(side_effect=[[entity], []])
    uow.outbox.update = mocker.AsyncMock()
    uow.orders.get_order = mocker.AsyncMock(return_value=updated_order)
    uow.orders.update_order = mocker.AsyncMock()
    uow_factory = DummyUowFactory(uow)
    broker = DummyBroker(mocker)
    notification_client = mocker.Mock()
    notification_client.create_notification = mocker.AsyncMock()

    sleep_calls = {"n": 0}

    async def fake_sleep(_):
        sleep_calls["n"] += 1
        if sleep_calls["n"] >= 2:
            raise asyncio.CancelledError()

    monkeypatch.setattr("src.application.worker.outbox.asyncio.sleep", fake_sleep)
    worker = OutboxWorker(uow_factory, broker, notification_client)

    with pytest.raises(asyncio.CancelledError):
        await worker.run()

    broker.send_message.assert_awaited_once()
    uow.outbox.update.assert_awaited()
    uow.commit.assert_awaited()
    notification_client.create_notification.assert_awaited()


@pytest.mark.asyncio
async def test_inbox_worker_processes_pending_entities(mocker, monkeypatch):
    uow = DummyUow(mocker)
    order_id = uuid.uuid4()
    entity = InboxEntity(
        event_type="order.shipped",
        payload={"order_id": str(order_id)},
    )
    order = mocker.Mock(
        id=order_id,
        user_id="user_1",
        idempotency_key="idem",
        to_shipped=mocker.Mock(),
    )
    order.to_shipped.return_value = order
    uow.inbox.get_pending_inbox = mocker.AsyncMock(side_effect=[[entity], []])
    uow.inbox.update = mocker.AsyncMock()
    uow.orders.get_order = mocker.AsyncMock(return_value=order)
    uow.orders.update_order = mocker.AsyncMock()
    uow_factory = DummyUowFactory(uow)
    notification_client = mocker.Mock()
    notification_client.create_notification = mocker.AsyncMock()

    sleep_calls = {"n": 0}

    async def fake_sleep(_):
        sleep_calls["n"] += 1
        if sleep_calls["n"] >= 2:
            raise asyncio.CancelledError()

    monkeypatch.setattr("src.application.worker.inbox.asyncio.sleep", fake_sleep)
    worker = InboxWorker(uow_factory, notification_client)

    with pytest.raises(asyncio.CancelledError):
        await worker.run()

    uow.inbox.update.assert_awaited()
    uow.orders.update_order.assert_awaited()
    uow.commit.assert_awaited()
    notification_client.create_notification.assert_awaited()
