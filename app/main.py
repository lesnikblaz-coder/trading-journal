from fastapi import FastAPI

from app.exceptions.handler import register_exception_handlers

# routers
from app.routers.auth import router as auth_router
from app.routers.trading_system import router as trading_system_router
from app.routers.trade import router as trade_router
from app.routers.analytics import router as analytics_router


app = FastAPI()

register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(trading_system_router)
app.include_router(trade_router)
app.include_router(analytics_router)


# ---------- ROOT ----------
@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {"status": "TRUE"}