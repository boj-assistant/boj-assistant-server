from langchain_core.messages import SystemMessage, HumanMessage
from playwright.async_api import async_playwright
from app.graph.state import ReviewInputState
from app.graph.utils import get_language_id
from app.core.config import settings
from tavily import TavilyClient
from app.core.llm import llm
from typing import Optional
import logging

logger = logging.getLogger(__name__)

tavily_client = TavilyClient(api_key=settings.TAVILY_API_KEY)

async def search_solution_from_boj(problem_id: int, language: str) -> Optional[str] :

    language_id = get_language_id(language)
    
    status_url = f"https://www.acmicpc.net/status?problem_id={problem_id}&user_id=&language_id={language_id}&result_id=4"
    base_url = "https://www.acmicpc.net"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        
        try:
            # context를 명시적으로 생성하고 권한 설정
            context = await browser.new_context(
                permissions=["clipboard-read", "clipboard-write"],
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()

            await context.add_cookies([{
                "name": "bojautologin",
                "value": settings.BOJ_COOKIE,
                "url": "https://www.acmicpc.net"
            }])

            # domcontentloaded로 변경 (백준은 SSR이라 이 정도면 충분)
            await page.goto(status_url, wait_until="domcontentloaded", timeout=30000)
            
            # 테이블이 로드될 때까지 대기 (더 구체적인 셀렉터 사용)
            await page.wait_for_selector("#status-table tbody tr", timeout=30000)

            hrefs = await page.evaluate("""
                () => {
                return [...document.querySelectorAll(
                    '#status-table tbody tr td:nth-child(7) a'
                )].map(a => a.getAttribute('href'));
                }
            """)

            await page.goto(f"{base_url}{hrefs[0]}", wait_until="domcontentloaded", timeout=30000)
            
            # 복사 버튼이 나타날 때까지 대기
            await page.wait_for_selector("button.copy-button", timeout=10000)
            await page.click("button.copy-button")

            solution = await page.evaluate(
                "() => navigator.clipboard.readText()"
            )
            logger.info(f"Solution fetched from BOJ: {solution}")
            return solution

        except Exception as e:
            logger.error(f"Error fetching solution from BOJ: {e}")
            return None
        finally:
            await browser.close()

async def search_solution_from_web(problem_id:int, language: str) -> Optional[str]:
    query = f"백준 {problem_id} {language}"

    search_result = tavily_client.search(
        query,
        search_depth="advanced",
        max_results = 3,
        include_raw_content=True    
    )

    urls = [item.get("url") for item in search_result.get("results", [])[:3]]
    logger.info(f"Tavily search urls: {urls}")

    # 검색 결과가 없으면 None 반환
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

    return solution

async def searcher(state: ReviewInputState) :
    problem_id = state.problem_id
    language = state.language

    # 백준 크롤링 시도
    solution = await search_solution_from_boj(problem_id, language)
    if solution is None:
        # 웹 검색 시도
        solution = await search_solution_from_web(problem_id, language)

    return {
        "solution": solution
    }