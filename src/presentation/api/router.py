from fastapi import APIRouter

from src.presentation.api.v1.order import router as order_router

router = APIRouter(prefix="/api")

router.include_router(order_router)
