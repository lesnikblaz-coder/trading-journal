from fastapi import FastAPI

from app.exceptions.handler import register_exception_handlers

# routers
from app.routers.auth import router as auth_router


app = FastAPI()

register_exception_handlers(app)

app.include_router(auth_router)


# ---------- ROOT ----------
@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {"status": "TRUE"}