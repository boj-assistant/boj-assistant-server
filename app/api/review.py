from fastapi import APIRouter, Query
from app.service.crawler import get_solution

router = APIRouter(prefix="/api/v1", tags=["reviews"])

@router.get("/reviews")
async def get_reviews(
    problem_id: int = Query(..., description="문제 ID"),
    language_id: int = Query(..., description="언어 ID")
):
    solution = await get_solution(problem_id, language_id)
    return solution