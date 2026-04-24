import typing
from contextlib import AbstractAsyncContextManager

from src.application.ports.order_repo import OrderRepositoryPort


class UnitOfWorkFactoryPort(typing.Protocol):
    @property
    def orders(self) -> OrderRepositoryPort: ...

    async def commit(self) -> None: ...


class UnitOfWorkPort(typing.Protocol):
    def __call__(self) -> AbstractAsyncContextManager[UnitOfWorkFactoryPort]: ...
