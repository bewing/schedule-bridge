from contextlib import asynccontextmanager
from functools import lru_cache

from fastapi import FastAPI, APIRouter
from fastapi.responses import RedirectResponse
import httpx

from .config import Settings
from .api.router import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with httpx.AsyncClient() as client:
        yield {"client": client}


docs_router = APIRouter()


@lru_cache()
def get_settings():
    return Settings()


def get_application() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.PROJECT_TITLE,
        debug=settings.DEBUG,
        version=str(settings.VERSION),
        lifespan=lifespan,
    )

    @app.get("/", include_in_schema=False)
    def docs_redirect():
        return RedirectResponse("/docs")

    app.include_router(api_router, prefix=settings.API_PREFIX)

    return app
