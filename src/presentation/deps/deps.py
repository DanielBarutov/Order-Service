from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.session import get_session
from src.infrastructure.uow import UnitOfWork

from src.application.usecases.order import (
    CreateOrderUseCase,
    GetOrderUseCase,
    UpdateOrderUseCase,
)
from src.infrastructure.clients.storage_client import StorageClient
from src.infrastructure.clients.notification_client import NotificationClient
from src.infrastructure.clients.payment_client import PaymentClient

import src.settings


def get_storage_client() -> StorageClient:
    """Клиент для работы с хранилищем"""
    return StorageClient(
        base_url=src.settings.STORAGE_BASE_URL, api_key=src.settings.STORAGE_API_KEY
    )


def get_payment_client() -> PaymentClient:
    """Клиент для работы с платежами"""
    return PaymentClient(
        base_url=src.settings.PAYMENT_BASE_URL,
        api_key=src.settings.PAYMENT_API_KEY,
        callback_url=src.settings.PAYMENT_CALLBACK_URL,
    )


def get_notification_client() -> NotificationClient:
    """Клиент для работы с уведомлениями"""
    return NotificationClient(
        base_url=src.settings.NOTIFICATION_BASE_URL,
        api_key=src.settings.NOTIFICATION_API_KEY,
    )


def order_uow(
    session: AsyncSession = Depends(get_session),
) -> UnitOfWork:
    """Unit of Work для единой транзакции"""
    return UnitOfWork(session=session)


def create_order_use_case(
    uow: UnitOfWork = Depends(order_uow),
    storage_client: StorageClient = Depends(get_storage_client),
    payment_client: PaymentClient = Depends(get_payment_client),
    notification_client: NotificationClient = Depends(get_notification_client),
) -> CreateOrderUseCase:
    """Usecase для создания заказа"""
    return CreateOrderUseCase(
        unit_of_work=uow,
        storage_client=storage_client,
        payment_client=payment_client,
        notification_client=notification_client,
    )


def get_order_use_case(
    uow: UnitOfWork = Depends(order_uow),
) -> GetOrderUseCase:
    """Usecase для получения заказа"""
    return GetOrderUseCase(unit_of_work=uow)


def update_order_use_case(
    uow: UnitOfWork = Depends(order_uow),
) -> UpdateOrderUseCase:
    """Usecase для обновления заказа"""
    return UpdateOrderUseCase(unit_of_work=uow)
