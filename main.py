import logging

from fastapi import FastAPI
import uvicorn

from src.bootstrap import lifespan
from src.presentation.api.router import router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s",
)
logger = logging.getLogger("order-service")

app = FastAPI(title="Order Service", version="0.1.0", lifespan=lifespan)
app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="error")
