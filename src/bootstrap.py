import asyncio
import contextlib

from fastapi import FastAPI


import src.settings
from src.application.worker.inbox import InboxWorker
from src.application.worker.outbox import OutboxWorker
from src.infrastructure.db.session import AsyncSessionLocal
from src.infrastructure.kafka.consumer import KafkaConsumer
from src.infrastructure.kafka.producer import KafkaProducer
from src.infrastructure.kafka.handlers import (
    handle_order_cancelled,
    handle_order_shipped,
)
from src.infrastructure.uow import UnitOfWork


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.kafka_consumer = KafkaConsumer(
        bootstrap_servers=src.settings.KAFKA_BOOTSTRAP_SERVERS
    )
    broker = KafkaProducer(bootstrap_servers=src.settings.KAFKA_BOOTSTRAP_SERVERS)
    uow = UnitOfWork(session=AsyncSessionLocal)

    async def on_order_shipped(event: dict) -> None:
        await handle_order_shipped(event, uow)

    async def on_order_cancelled(event: dict) -> None:
        await handle_order_cancelled(event, uow)

    consumer_task = None

    inbox_worker = InboxWorker(uow)
    outbox_worker = OutboxWorker(uow, broker)

    inbox_task = asyncio.create_task(inbox_worker.run())
    outbox_task = asyncio.create_task(outbox_worker.run())

    try:
        await app.state.kafka_consumer.start()

        consumer_task = asyncio.create_task(
            app.state.kafka_consumer.run(on_order_shipped, on_order_cancelled)
        )

        yield

    finally:
        if consumer_task:
            consumer_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await consumer_task

        with contextlib.suppress(Exception):
            await app.state.kafka_consumer.stop()

        if inbox_task:
            inbox_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await inbox_task

        if outbox_task:
            outbox_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await outbox_task
