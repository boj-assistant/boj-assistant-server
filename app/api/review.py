from app.schemas.review import ReviewCreateRequest, ReviewCreateResponse
from app.service.graph import call_graph
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/v1", tags=["reviews"])

@router.post("/reviews")
async def create_review(request: ReviewCreateRequest) -> ReviewCreateResponse:
    review =  await call_graph(request)
    if review is None:
        raise HTTPException(status_code=400, detail="Failed to generate review")
    return ReviewCreateResponse(review=review)