import typing
from contextlib import AbstractAsyncContextManager

from application.ports.inbox_repo import InboxRepositoryPort
from application.ports.outbox_repo import OutboxRepositoryPort
from src.application.ports.order_repo import OrderRepositoryPort


class UnitOfWorkFactoryPort(typing.Protocol):
    @property
    def orders(self) -> OrderRepositoryPort: ...
    @property
    def outbox(self) -> OutboxRepositoryPort: ...
    @property
    def inbox(self) -> InboxRepositoryPort: ...
    async def commit(self) -> None: ...


class UnitOfWorkPort(typing.Protocol):
    def __call__(self) -> AbstractAsyncContextManager[UnitOfWorkFactoryPort]: ...
