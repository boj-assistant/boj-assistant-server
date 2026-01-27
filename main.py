from contextlib import asynccontextmanager
from app.db.session import init_db_pool, close_db_pool
from app.core.config import settings
from app.core.prompts import load_prompt
import app.core.logger as logger
from fastapi import FastAPI
from app.api import review

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_prompt()
    await init_db_pool()
    yield
    await close_db_pool()

app = FastAPI(lifespan=lifespan)

app.include_router(review.router)

@app.get("/health")
async def health_check():
    return {"message": "server is running..."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT)