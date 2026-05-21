from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.test_designs import router as test_designs_router
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="AI Test Design Support API",
    lifespan=lifespan,
)

app.include_router(health_router)
app.include_router(test_designs_router)