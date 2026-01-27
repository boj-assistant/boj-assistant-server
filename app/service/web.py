from app.core.config import settings
import logging
from tavily import TavilyClient
from app.core.llm import llm
from langchain_core.messages import SystemMessage, HumanMessage

logger = logging.getLogger(__name__)

tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)

async def get_web_search(problem_id:int, language: str) -> str:
    query = f"백준 {problem_id} {language}"

    search_result = tavily_client.search(
        query,
        search_depth="advanced",
        max_results = 3,
        include_raw_content=True    
    )

    urls = [item.get("url") for item in search_result.get("results", [])[:3]]
    logger.info(f"Tavily search urls: {urls}")

    if not search_result['results']:
        return None
    
    for result in search_result['results'][:3]:
        raw_content = result['raw_content']
        input_messages = [
            SystemMessage(content="""너는 최고의 프로그래밍 전문가이자 내 형님을 모시는 충신이다.
    아래 제공된 블로그 본문 내용에서 백준 {problem_id}번 문제의 {language}언어로 된 정답 코드만 추출해라.
    
    [지침]
    1. 코드 외의 설명은 일절 배제하고 '코드만' 반환한다.
    2. 만약 해당 언어 코드가 없다면 "NOT_FOUND"라고 답해라.
    3. 마크다운 형식(```) 없이 순수 코드만 반환해라.
    
    [블로그 본문]
    {content}
    """),
            HumanMessage(content=raw_content)
        ]
        
        response = await llm.ainvoke(input_messages)
        
        # response.content가 리스트인 경우 type이 'text'인 항목의 text 값만 추출하여 합침
        if isinstance(response.content, list):
            solution = "".join(
                item.get("text", "")
                for item in response.content
                if isinstance(item, dict) and item.get("type") == "text"
            )
        else:
            solution = str(response.content)
            
        solution = solution.strip()

        if solution != "NOT_FOUND":
            return solution
    
    return None