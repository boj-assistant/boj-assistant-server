from playwright.async_api import async_playwright
from app.core.config import settings
import logging
from typing import Optional

logger = logging.getLogger(__name__)

async def fetch_solution_from_boj(problem_id: int, language_id: int) -> Optional[str] :
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