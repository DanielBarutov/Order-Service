from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import OutboxEntity, OutboxStatusEnum
from src.infrastructure.db.models import Outbox as OutboxModel


class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _to_entity(outbox: OutboxModel) -> OutboxEntity:
        return OutboxEntity(
            id=outbox.id,
            event_type=outbox.event_type,
            payload=outbox.payload,
            status=outbox.status,
            created_at=outbox.created_at,
            completed_at=outbox.completed_at,
        )

    async def create(self, outbox: OutboxEntity) -> OutboxEntity:
        outbox_model = OutboxModel(
            id=outbox.id,
            event_type=outbox.event_type,
            payload=outbox.payload,
            status=outbox.status,
            created_at=outbox.created_at,
        )
        self.session.add(outbox_model)
        return self._to_entity(outbox_model)

    async def get_pending_outbox(self) -> list[OutboxEntity]:
        outbox_models = await self.session.execute(
            select(OutboxModel).where(OutboxModel.status == OutboxStatusEnum.PENDING)
        )
        if not outbox_models:
            return []
        outbox_entities = [
            self._to_entity(outbox) for outbox in outbox_models.scalars().all()
        ]
        return outbox_entities

    async def update(self, outbox: OutboxEntity) -> OutboxEntity:
        outbox_model = OutboxModel(
            id=outbox.id,
            event_type=outbox.event_type,
            payload=outbox.payload,
            status=outbox.status,
            created_at=outbox.created_at,
        )
        await self.session.merge(outbox_model)
        return self._to_entity(outbox_model)
