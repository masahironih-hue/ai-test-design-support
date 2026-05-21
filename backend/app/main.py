from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.test_designs import router as test_designs_router


app = FastAPI(
    title="AI Test Design Support API",
    version="0.1.0",
)


app.include_router(health_router)
app.include_router(test_designs_router)
