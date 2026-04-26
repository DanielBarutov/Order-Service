import datetime
import decimal
import uuid

import pytest

from src.core.models import NotificationEntity, PaymentEntity
from src.infrastructure.clients.notification_client import NotificationClient
from src.infrastructure.clients.payment_client import PaymentClient
from src.infrastructure.clients.storage_client import StorageClient


@pytest.mark.asyncio
async def test_storage_client_get_item_success(mocker):
    item_id = uuid.uuid4()
    mock_json = {
        "id": str(item_id),
        "name": "Mouse Pad",
        "price": "199.90",
        "available_qty": 7,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }

    mock_response = mocker.Mock()
    mock_response.json.return_value = mock_json
    mock_response.raise_for_status.return_value = None

    mock_client = mocker.Mock()
    mock_client.get = mocker.AsyncMock(return_value=mock_response)
    mock_async_client = mocker.patch(
        "src.infrastructure.clients.storage_client.httpx.AsyncClient"
    )
    mock_async_client.return_value.__aenter__.return_value = mock_client

    client = StorageClient(base_url="http://storage.local", api_key="secret")
    item = await client.get_item(item_id)

    assert item.id == item_id
    assert item.name == "Mouse Pad"
    assert item.available_qty == 7
    mock_client.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_payment_client_create_payment_success(mocker):
    payment_id = uuid.uuid4()
    order_id = uuid.uuid4()
    now = datetime.datetime.now(datetime.timezone.utc)
    payment = PaymentEntity(
        order_id=order_id,
        amount=decimal.Decimal("10.00"),
        idempotency_key="idem-1",
    )

    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "id": str(payment_id),
        "user_id": "user_1",
        "order_id": str(order_id),
        "amount": "10.00",
        "status": "succeeded",
        "idempotency_key": "idem-1",
        "created_at": now.isoformat(),
    }
    mock_response.raise_for_status.return_value = None

    mock_client = mocker.Mock()
    mock_client.post = mocker.AsyncMock(return_value=mock_response)
    mock_async_client = mocker.patch(
        "src.infrastructure.clients.payment_client.httpx.AsyncClient"
    )
    mock_async_client.return_value.__aenter__.return_value = mock_client

    client = PaymentClient(
        base_url="http://pay.local",
        api_key="key",
        callback_url="https://order.local/callback",
    )
    created = await client.create_payment(payment)

    assert str(created.id) == str(payment_id)
    assert str(created.order_id) == str(order_id)
    assert created.status == "succeeded"
    mock_client.post.assert_awaited_once()


@pytest.mark.asyncio
async def test_notification_client_create_notification_success(mocker):
    ref_id = uuid.uuid4()
    notification_id = uuid.uuid4()
    now = datetime.datetime.now(datetime.timezone.utc)

    mock_response = mocker.Mock()
    mock_response.json.return_value = {
        "id": str(notification_id),
        "user_id": "user_1",
        "message": "PAID",
        "reference_id": str(ref_id),
        "created_at": now.isoformat(),
    }
    mock_response.raise_for_status.return_value = None

    mock_client = mocker.Mock()
    mock_client.post = mocker.AsyncMock(return_value=mock_response)
    mock_async_client = mocker.patch(
        "src.infrastructure.clients.notification_client.httpx.AsyncClient"
    )
    mock_async_client.return_value.__aenter__.return_value = mock_client

    client = NotificationClient(base_url="http://notify.local", api_key="key")
    created = await client.create_notification(
        NotificationEntity(message="PAID", reference_id=ref_id),
        idempotency_key="idem_paid",
    )

    assert created.message == "PAID"
    assert created.reference_id == ref_id
    mock_client.post.assert_awaited_once()
