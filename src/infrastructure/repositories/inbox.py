from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models import Inbox as InboxModel
from core.models import InboxEntity, InboxStatusEnum


class InboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_entity(inbox: InboxModel) -> InboxEntity:
        return InboxEntity(
            id=inbox.id,
            event_type=inbox.event_type,
            payload=inbox.payload,
            status=inbox.status,
            created_at=inbox.created_at,
            completed_at=inbox.completed_at,
        )

    async def create(self, inbox: InboxEntity) -> InboxEntity:
        inbox_model = InboxModel(
            id=inbox.id,
            event_type=inbox.event_type,
            payload=inbox.payload,
            status=inbox.status,
            created_at=inbox.created_at,
        )
        self.session.add(inbox_model)
        print("Inbox добавлен", inbox_model)
        return self._to_entity(inbox_model)

    async def get_pending_inbox(self) -> list[InboxEntity]:
        inbox_models = await self.session.execute(
            select(InboxModel).where(InboxModel.status == InboxStatusEnum.PENDING)
        )
        if not inbox_models:
            return []
        inbox_entities = [
            self._to_entity(inbox) for inbox in inbox_models.scalars().all()
        ]
        return inbox_entities

    async def update(self, inbox: InboxEntity) -> InboxEntity:
        inbox_model = InboxModel(
            id=inbox.id,
            event_type=inbox.event_type,
            payload=inbox.payload,
            status=inbox.status,
            created_at=inbox.created_at,
        )
        self.session.merge(inbox_model)
        print("Inbox мерджед", inbox_model)
        return self._to_entity(inbox_model)
