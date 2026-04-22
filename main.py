from fastapi import FastAPI
import uvicorn
from src.presentation.api.router import router

app = FastAPI(title="Order Service", version="0.1.0")

app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
