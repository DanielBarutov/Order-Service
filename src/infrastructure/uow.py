import contextlib
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


from src.infrastructure.repositories.inbox import InboxRepository
from src.infrastructure.repositories.outbox import OutboxRepository
from src.infrastructure.repositories.order import OrderRepository
from src.infrastructure.db.session import AsyncSessionLocal


class UnitOfWork:
    def __init__(self, session: async_sessionmaker[AsyncSessionLocal]) -> None:
        self._session = session

    @contextlib.asynccontextmanager
    async def __call__(self):
        async with self._session as s:
            try:
                yield _UnitOfWorkImplementation(s)
                await s.rollback()

            except Exception as e:
                await s.rollback()
                raise e


class _UnitOfWorkImplementation:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._order_repo = OrderRepository(session)
        self._outbox_repo = OutboxRepository(session)
        self._inbox_repo = InboxRepository(session)

    @property
    def orders(self) -> OrderRepository:
        return self._order_repo

    @property
    def outbox(self) -> OutboxRepository:
        return self._outbox_repo

    @property
    def inbox(self) -> InboxRepository:
        return self._inbox_repo

    async def commit(self) -> None:
        return await self._session.commit()
