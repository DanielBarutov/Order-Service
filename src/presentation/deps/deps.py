from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.uow import UnitOfWork
from src.application.usecases.order import CreateOrderUseCase, GetOrderUseCase
from src.infrastructure.db.session import get_session
from src.infrastructure.clients.capashino import CapashinoClient
import src.settings


def get_capashino_client():
    return CapashinoClient(
        base_url=src.settings.CAPASHINO_BASE_URL, api_key=src.settings.CAPASHINO_API_KEY
    )


def order_uow(
    session: AsyncSession = Depends(get_session),
) -> UnitOfWork:
    return UnitOfWork(session=session)


def create_order_use_case(
    uow: UnitOfWork = Depends(order_uow),
    client: CapashinoClient = Depends(get_capashino_client),
) -> CreateOrderUseCase:
    return CreateOrderUseCase(unit_of_work=uow, client=client)


def get_order_use_case(
    uow: UnitOfWork = Depends(order_uow),
) -> GetOrderUseCase:
    return GetOrderUseCase(unit_of_work=uow)
