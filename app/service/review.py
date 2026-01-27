from app.crud.problem import fetch_problem_solution, create_problem_with_solution, update_problem_solution, check_if_promblem_exists
from app.service.crawler import fetch_solution_from_boj
from app.schemas.review import ReviewCreateRequest, ReviewResponse
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import llm
from app.core.prompts import get_reviewer_prompt
import asyncio
import httpx
from typing import Literal
import logging

logger = logging.getLogger(__name__)

def get_review_template() -> ChatPromptTemplate:
    system_prompt = get_reviewer_prompt()
    
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Problem URL:
{problem_url}

Correct Solution:
```{correct_solution}```

Student's Wrong Code:
```{wrong_code}```"""),
    ])

def get_language_id(language: Literal["java8", "node.js", "python3", "c++17"]) -> str:
    return {
        "java8": "3",
        "node.js": "17",
        "python3": "28",
        "c++17": "84"
    }[language]

async def get_problem_tags(problem_id: int) :
    url = f"https://solved.ac/api/v3/problem/show?problemId={problem_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
    logger.info(f"Solution tags fetched from API: {data}")
    return data.get("titleKo"), [tag.get("key") for tag in data.get("tags", [])]

async def get_problem_solution(problem_id: int, language: Literal["java8", "node.js", "python3", "c++17"]) -> str:
    
    # 1. language_id 가져오기
    language_id = get_language_id(language)

    # 2. problem_id에 해당하는 문제가 존재하는지 확인
    exists = await check_if_promblem_exists(problem_id)
    if exists:
        solution = await fetch_problem_solution(problem_id, language)
        if solution is None:
            solution = await fetch_solution_from_boj(problem_id, language_id)
            await update_problem_solution(problem_id, language, solution)
    else:
        # 3. problem_id에 해당하는 문제가 존재하지 않는 경우, 문제 정보와 정답 코드 모두 가져오기
        (title, tags), solution = await asyncio.gather(
            get_problem_tags(problem_id),
            fetch_solution_from_boj(problem_id, language_id),
        )
        # 4. problem_id에 해당하는 문제가 존재하지 않는 경우, 문제 정보와 정답 코드를 데이터베이스에 저장
        await create_problem_with_solution(problem_id, title, language, solution, tags)
    
    return solution

async def get_review(request: ReviewCreateRequest) -> ReviewResponse:
    problem_url = f"https://www.acmicpc.net/problem/{request.problem_id}"
    correct_solution = await get_problem_solution(request.problem_id, request.language)
    if correct_solution is None:
        return ReviewResponse(review="Error fetching solution from BOJ")

    wrong_code = request.code

    # 캐시된 프롬프트 템플릿 사용
    template = get_review_template()
    chain = template | llm
    response = await chain.ainvoke({
        "problem_url": problem_url,
        "correct_solution": correct_solution,
        "wrong_code": wrong_code
    })
    
    # response.content가 리스트인 경우 type이 'text'인 항목의 text 값만 추출하여 합침
    if isinstance(response.content, list):
        review_text = "".join(
            item.get("text", "")
            for item in response.content
            if isinstance(item, dict) and item.get("type") == "text"
        )
    else:
        review_text = str(response.content)
    
    logger.info(f"Review response: {review_text}")
    return ReviewResponse(review=review_text)