import asyncio
import contextlib
from collections.abc import AsyncIterator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

import src.settings
from src.application.usecases.order import UpdateOrderUseCase
from src.infrastructure.db.session import AsyncSessionLocal
from src.infrastructure.kafka.consumer import KafkaConsumer
from src.infrastructure.kafka.handlers import (
    handle_order_cancelled,
    handle_order_shipped,
)
from src.infrastructure.kafka.producer import KafkaProducer
from src.infrastructure.uow import UnitOfWork


@contextlib.asynccontextmanager
async def _session_scope() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def build_update_order_use_case(
    producer: KafkaProducer,
) -> UpdateOrderUseCase:
    class _UowFactory:
        def __call__(self):
            @contextlib.asynccontextmanager
            async def _ctx():
                async with _session_scope() as session:
                    uow = UnitOfWork(session=session)
                    async with uow() as impl:
                        yield impl

            return _ctx()

    return UpdateOrderUseCase(unit_of_work=_UowFactory(), broker=producer)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    producer = KafkaProducer(bootstrap_servers=src.settings.KAFKA_BOOTSTRAP_SERVERS)
    consumer = KafkaConsumer(bootstrap_servers=src.settings.KAFKA_BOOTSTRAP_SERVERS)

    update_order_uc = build_update_order_use_case(producer)

    async def on_order_shipped(event: dict) -> None:
        await handle_order_shipped(event, update_order_uc)

    async def on_order_cancelled(event: dict) -> None:
        await handle_order_cancelled(event, update_order_uc)

    consumer_task = None

    try:
        for attempt in range(5):
            try:
                await producer.start()
                break
            except Exception as e:
                print(f"Продюсер не запустился, попытка {attempt + 1}: {e}")
                if attempt == 4:
                    raise
                await asyncio.sleep(10)

        for attempt in range(5):
            try:
                await consumer.start()
                break
            except Exception as e:
                print(f"Консюмер не запустился, попытка {attempt + 1}: {e}")
                if attempt == 4:
                    raise
                await asyncio.sleep(10)

        consumer_task = asyncio.create_task(
            consumer.run(on_order_shipped, on_order_cancelled)
        )

        yield

    finally:
        if consumer_task:
            consumer_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await consumer_task

        with contextlib.suppress(Exception):
            await consumer.stop()

        with contextlib.suppress(Exception):
            await producer.stop()
