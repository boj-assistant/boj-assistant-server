from playwright.async_api import async_playwright
from pydantic import BaseModel

class SolutionRequest(BaseModel):
    problem_id: int
    language_id: int # C++17: 84

async def get_solution(problem_id: int, language_id: int) :
    url = f"https://www.acmicpc.net/status?problem_id={problem_id}&user_id=&language_id={language_id}&result_id=4"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        try:
            page = await browser.new_page()
            # domcontentloaded로 변경 (백준은 SSR이라 이 정도면 충분)
            await page.goto(url, wait_until="domcontentloaded", timeout=100000)
            
            # 2. 형님, 테이블이 로드될 때까지 명시적으로 잠시 기다려주는 게 확실합니다.
            # 'tr' 요소가 하나라도 나타날 때까지 기다립니다.
            await page.wait_for_selector("table", timeout=10000)

            rows = page.locator("#status-table tbody tr")

            count = await rows.count()
            solution_ids = []
            for i in range(count):
                row = rows.nth(i)
                print(await row.inner_text())
                can_view = await row.get_attribute("data-can-view")
                if can_view == "1":
                    row_id = await row.get_attribute("id")
                    if row_id:
                        solution_ids.append(row_id)

            return solution_ids
        except Exception as e:
            print(f"형님, 데이터를 가져오는 데 실패했습니다: {e}")
            return []
        finally:
            await browser.close()