from pydantic import BaseModel, Field
from typing import Literal

class ReviewCreateRequest(BaseModel):
    problem_id: int = Field(..., gt=0, description="문제 번호는 양수여야 합니다.")
    language: Literal["java8", "node.js", "python3", "c++17"] = Field(..., description="지원되는 언어는 java8, node.js, python3, c++17 입니다.")
    code: str = Field(..., min_length=10, description="코드는 최소 10자 이상이어야 합니다.")

class ReviewResponse(BaseModel):
    review: str = Field(..., description="리뷰는 문자열 형태로 반환됩니다.")

class ProblemResponse(BaseModel):
    problem_id: int = Field(..., gt=0, description="문제 번호는 양수여야 합니다.")
    title: str = Field(..., min_length=1, description="문제 제목은 최소 1자 이상이어야 합니다.")