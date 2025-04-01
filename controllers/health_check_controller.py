from fastapi import APIRouter

router = APIRouter(tags=["Health Check"])

@router.get("/health-check")
async def health_check():
    return {"status": "ok"}