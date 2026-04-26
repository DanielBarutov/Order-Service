import datetime
import uuid

import pytest

from src.core.models import InboxEntity, OutboxEntity
from src.infrastructure.repositories.inbox import InboxRepository
from src.infrastructure.repositories.order import OrderRepository
from src.infrastructure.repositories.outbox import OutboxRepository


class ScalarResult:
    def __init__(self, value):
        self._value = value

    def scalar(self):
        return self._value

    def scalars(self):
        class _Scalars:
            def __init__(self, value):
                self._value = value

            def all(self):
                return self._value

        return _Scalars(self._value)


@pytest.mark.asyncio
async def test_order_repository_get_order_raises_if_missing(mocker):
    session = mocker.Mock()
    session.execute = mocker.AsyncMock(return_value=ScalarResult(None))
    repo = OrderRepository(session)
    assert await repo.get_order(uuid.uuid4()) is None


@pytest.mark.asyncio
async def test_order_repository_create_order_adds_model(mocker):
    session = mocker.Mock()
    repo = OrderRepository(session)
    order = mocker.Mock(
        id=uuid.uuid4(),
        user_id="user_1",
        quantity=1,
        item_id=uuid.uuid4(),
        idempotency_key="idem",
        status="new",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        updated_at=datetime.datetime.now(datetime.timezone.utc),
    )

    result = await repo.create_order(order)

    assert result == order
    session.add.assert_called_once()


@pytest.mark.asyncio
async def test_outbox_repository_get_pending_returns_entities(mocker):
    session = mocker.Mock()
    model = mocker.Mock(
        id=uuid.uuid4(),
        event_type="order.paid",
        payload={"order_id": str(uuid.uuid4())},
        status="pending",
        created_at=datetime.datetime.now(datetime.timezone.utc),
        completed_at=None,
    )
    session.execute = mocker.AsyncMock(return_value=ScalarResult([model]))
    repo = OutboxRepository(session)

    result = await repo.get_pending_outbox()

    assert len(result) == 1
    assert result[0].event_type == "order.paid"


@pytest.mark.asyncio
async def test_inbox_repository_update_calls_merge(mocker):
    session = mocker.Mock()
    session.merge = mocker.AsyncMock()
    repo = InboxRepository(session)
    entity = InboxEntity(
        id=uuid.uuid4(),
        event_type="order.shipped",
        payload={"order_id": str(uuid.uuid4())},
    )

    updated = await repo.update(entity)

    assert updated.id == entity.id
    session.merge.assert_awaited_once()


@pytest.mark.asyncio
async def test_outbox_repository_update_calls_merge(mocker):
    session = mocker.Mock()
    session.merge = mocker.AsyncMock()
    repo = OutboxRepository(session)
    entity = OutboxEntity(
        id=uuid.uuid4(),
        event_type="order.paid",
        payload={"order_id": str(uuid.uuid4())},
    )

    updated = await repo.update(entity)

    assert updated.id == entity.id
    session.merge.assert_awaited_once()
