from app.schemas.review import ReviewCreateResponse
from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import llm
from app.core.prompts import get_reviewer_prompt
from app.graph.state import ReviewState
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

async def reviewer(state: ReviewState):
    problem_id = state.problem_id
    solution = state.solution
    code = state.code

    problem_url = f"https://www.acmicpc.net/problem/{problem_id}"
    
    if solution is None:
        return {
            "review": None
        }

    # 캐시된 프롬프트 템플릿 사용
    template = get_review_template()
    chain = template | llm
    response = await chain.ainvoke({
        "problem_url": problem_url,
        "correct_solution": solution,
        "wrong_code": code
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
    return {
        "review": review_text
    }