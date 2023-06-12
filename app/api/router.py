import fastapi
from .v1 import router as v1_router

router = fastapi.APIRouter()
router.include_router(v1_router, prefix="/v1")
