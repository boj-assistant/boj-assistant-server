from fastapi import APIRouter
from app.schemas.review import ReviewCreateRequest, ReviewResponse
from app.service.review import get_review

router = APIRouter(prefix="/api/v1", tags=["reviews"])

@router.post("/reviews")
async def create_review(request: ReviewCreateRequest) -> ReviewResponse:
    return await get_review(request)