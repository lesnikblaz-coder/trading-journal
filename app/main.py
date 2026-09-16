from google import genai
from fastapi import FastAPI
from contextlib import asynccontextmanager


from app.exceptions.handler import register_exception_handlers
from app.core.config import settings

# routers
from app.routers.auth import router as auth_router
from app.routers.trading_system import router as trading_system_router
from app.routers.trade import router as trade_router
from app.routers.analytics import router as analytics_router
from app.routers.ai import router as ai_router


@asynccontextmanager
async def lifespan(lifespan_app: FastAPI):

    gemini = genai.Client(
        api_key=settings.GEMINI_API_KEY
    )

    lifespan_app.state.gemini = gemini.aio

    yield

    await gemini.aio.aclose()


app = FastAPI(lifespan=lifespan)


register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(trading_system_router)
app.include_router(trade_router)
app.include_router(analytics_router)
app.include_router(ai_router)


# ---------- ROOT ----------
@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {"status": "TRUE"}