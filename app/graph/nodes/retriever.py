from app.crud.problem import check_if_solution_exists, fetch_problem_solution
from app.graph.state import ReviewInputState

async def retriever(state: ReviewInputState) :
    problem_id = state.problem_id
    language = state.language

    # problem_id에 해당하는 문제가 존재한다면
    if await check_if_solution_exists(problem_id, language):
        solution = await fetch_problem_solution(problem_id, language)
        return {
            "solution": solution
        }
    else:
        return {
            "solution": None
        }