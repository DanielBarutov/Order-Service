import datetime
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.models import OrderEntity, OrderStatusEnum
from src.presentation.api.router import router
from src.presentation.deps import deps


class StubCreateOrderUseCase:
    async def execute(self, order):
        return OrderEntity(
            id=uuid.uuid4(),
            user_id=order.user_id,
            quantity=order.quantity,
            item_id=order.item_id,
            idempotency_key=order.idempotency_key,
            status=OrderStatusEnum.NEW,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )


class StubGetOrderUseCase:
    async def execute(self, order_id):
        return OrderEntity(
            id=order_id,
            user_id="user_1",
            quantity=1,
            item_id=uuid.uuid4(),
            status=OrderStatusEnum.SHIPPED,
            created_at=datetime.datetime.now(datetime.timezone.utc),
            updated_at=datetime.datetime.now(datetime.timezone.utc),
        )


class StubOrderCallbackUseCase:
    async def execute(self, order_id, status, error_message=None):
        return None


def _build_app():
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[deps.create_order_use_case] = (
        lambda: StubCreateOrderUseCase()
    )
    app.dependency_overrides[deps.get_order_use_case] = lambda: StubGetOrderUseCase()
    app.dependency_overrides[deps.order_callback_use_case] = (
        lambda: StubOrderCallbackUseCase()
    )
    return app


def test_create_order_endpoint_returns_201():
    app = _build_app()
    client = TestClient(app)
    payload = {
        "user_id": "user_1",
        "quantity": 1,
        "item_id": str(uuid.uuid4()),
        "idempotency_key": "idem-1",
    }

    response = client.post("/api/orders", json=payload)

    assert response.status_code == 201
    assert response.json()["user_id"] == "user_1"
    assert response.json()["status"] == "new"


def test_get_order_endpoint_returns_200():
    app = _build_app()
    client = TestClient(app)
    order_id = uuid.uuid4()

    response = client.get(f"/api/orders/{order_id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(order_id)
    assert response.json()["status"] == "shipped"


def test_payment_callback_endpoint_returns_200():
    app = _build_app()
    client = TestClient(app)
    payload = {
        "payment_id": str(uuid.uuid4()),
        "order_id": str(uuid.uuid4()),
        "status": "succeeded",
        "amount": "10.00",
    }

    response = client.post("/api/orders/payment-callback", json=payload)

    assert response.status_code == 200
    assert response.json()["message"] == "Payment callback received"
