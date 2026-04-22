from src.application.usecases.order import CreateOrderUseCase, GetOrderUseCase
from src.infrastructure.db.session import get_session
from src.infrastructure.clients.capashino import CapashinoClient
from src.infrastructure.repositories.order import OrderRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

import src.settings


def get_capashino_client():
    return CapashinoClient(
        base_url=src.settings.CAPASHINO_BASE_URL, api_key=src.settings.CAPASHINO_API_KEY
    )


def order_repository(
    session: AsyncSession = Depends(get_session),
) -> OrderRepository:
    return OrderRepository(session=session)


def create_order_use_case(
    repository: OrderRepository = Depends(order_repository),
    client: CapashinoClient = Depends(get_capashino_client),
) -> CreateOrderUseCase:
    return CreateOrderUseCase(repository=repository, client=client)


def get_order_use_case(
    repository: OrderRepository = Depends(order_repository),
) -> GetOrderUseCase:
    return GetOrderUseCase(repository=repository)
