from app.crud.problem import check_if_promblem_exists, check_if_solution_exists, create_problem_with_solution, update_problem_solution
from graph.state import ReviewInputState, ReviewOutputState
from app.schemas.review import ReviewCreateRequest
from fastapi import BackgroundTasks
from graph.main import graph
from typing import Optional
import logging
import httpx

logger = logging.getLogger(__name__)

async def get_problem_tags(problem_id: int) :
    url = f"https://solved.ac/api/v3/problem/show?problemId={problem_id}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
    logger.info(f"Solution tags fetched from API: {data}")
    return data.get("titleKo"), [tag.get("key") for tag in data.get("tags", [])]

async def call_graph(
    request: ReviewCreateRequest,
    background_tasks: BackgroundTasks
) -> Optional[str]:
    
    problem_id = request.problem_id
    language = request.language
    code = request.code
    
    input_state = ReviewInputState(problem_id, language, code)
    output_state: ReviewOutputState = await graph.ainvoke(input_state)
    solution = output_state.get("solution")
    review = output_state.get("review")

    if solution is None:
        return None

    solution_exists = await check_if_solution_exists(problem_id, language)
    problem_exists = await check_if_promblem_exists(problem_id)
    
    # 만약 해당 문제의 정답코드가 없다면
    if not solution_exists:

        # 만약 문제 정보는 존재한다면 정답코드만 업데이트
        if problem_exists:
            background_tasks.add_task(
                update_problem_solution,
                problem_id,
                language,
                solution,
            )
        # 만약 문제 정보도 없다면
        else:
            # 문제 정보 조회하기
            (title, tags) = await get_problem_tags(problem_id)
            background_tasks.add_task(
                create_problem_with_solution,
                problem_id,
                title,
                language,
                solution,
                tags,
            )
    return review