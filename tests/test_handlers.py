import contextlib

import pytest

from src.infrastructure.kafka.handlers import (
    handle_order_cancelled,
    handle_order_shipped,
)


class DummyUow:
    def __init__(self, mocker):
        self.inbox = mocker.Mock()
        self.inbox.create = mocker.AsyncMock()
        self.commit = mocker.AsyncMock()


class DummyUowFactory:
    def __init__(self, uow):
        self._uow = uow

    @contextlib.asynccontextmanager
    async def __call__(self):
        yield self._uow


@pytest.mark.asyncio
async def test_handle_order_shipped_creates_inbox_and_commits(mocker):
    uow = DummyUow(mocker)
    uow_factory = DummyUowFactory(uow)

    await handle_order_shipped(
        {"event_type": "order.shipped", "order_id": "abc"},
        uow_factory,
    )

    uow.inbox.create.assert_awaited_once()
    uow.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_order_cancelled_creates_inbox_and_commits(mocker):
    uow = DummyUow(mocker)
    uow_factory = DummyUowFactory(uow)

    await handle_order_cancelled(
        {"event_type": "order.cancelled", "order_id": "abc", "reason": "test"},
        uow_factory,
    )

    uow.inbox.create.assert_awaited_once()
    uow.commit.assert_awaited_once()
