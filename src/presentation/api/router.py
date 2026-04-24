from fastapi import APIRouter

from src.presentation.api.v1.order import router as order_router
from src.presentation.api.v1.payment_callback import router as payment_callback_router

router = APIRouter(prefix="/api")

router.include_router(order_router)
router.include_router(payment_callback_router)
