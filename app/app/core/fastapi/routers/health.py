from fastapi import APIRouter
from app.core.fastapi.models.base_models import HealthResponse

router = APIRouter()

@router.get("/")
async def health_check():
    # return {"status" : "up"}
    return HealthResponse(status="up")