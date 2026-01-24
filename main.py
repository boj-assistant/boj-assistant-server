from contextlib import asynccontextmanager
from app.db.session import init_db_pool, close_db_pool
from app.core.config import settings
import app.core.logger as logger
from fastapi import FastAPI
from app.api import review

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 프롬프트 로드 (한 번만 실행)
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