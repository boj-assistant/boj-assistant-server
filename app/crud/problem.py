from app.db.session import get_db_pool
from typing import Optional
import asyncpg
import json
import logging

logger = logging.getLogger(__name__)

async def check_if_promblem_exists(problem_id: int) -> bool:
    """problem_id가 존재하는지 확인"""
    db: asyncpg.Pool = await get_db_pool()
    
    async with db.acquire() as connection:
        result = await connection.fetchval("""
            SELECT EXISTS(SELECT 1 FROM problems WHERE problem_id = $1)
        """, problem_id)
        return result

async def check_if_solution_exists(problem_id: int, language: str) -> bool:
    """problem_id가 존재하고 해당 language의 solution이 존재하는지 확인"""
    db: asyncpg.Pool = await get_db_pool()
    
    async with db.acquire() as connection:
        result = await connection.fetchval("""
            SELECT EXISTS(
                SELECT 1 FROM problems 
                WHERE problem_id = $1 
                AND solution ? $2
            )
        """, problem_id, language)
        return result
        
async def fetch_problem_solution(problem_id: int, language: str) -> Optional[str]:
    db: asyncpg.Pool = await get_db_pool()
    
    async with db.acquire() as connection:
        # fetchval은 첫 번째 행의 첫 번째 컬럼값을 바로 리턴
        # problem_id에 해당하는 문제가 없거나 해당 key 값이 없을때 None 반환
        logger.info(f"Fetching solution from database for problem_id: {problem_id} and language: {language}")
        return await connection.fetchval("""
            SELECT solution ->> $1 FROM problems WHERE problem_id = $2
        """, language, problem_id)

async def create_problem_with_solution(problem_id: int, title: str, language: str, solution: str, tags: list[str]):
    """새로운 problem_id를 생성"""
    db: asyncpg.Pool = await get_db_pool()
    
    async with db.acquire() as connection:
        # solution을 jsonb로 변환: {language: solution_code} 형태
        solution_json = json.dumps({language: solution})
        logger.info(f"Saving new solution to database for problem_id: {problem_id} and language: {language}")
        await connection.execute("""
            INSERT INTO problems (problem_id, title, solution, tags) 
            VALUES ($1, $2, $3::jsonb, $4::text[])
        """, problem_id, title, solution_json, tags)

async def update_problem_solution(problem_id: int, language: str, solution: str):
    """기존 problem_id의 solution 컬럼에 language 키로 solution 추가"""
    db: asyncpg.Pool = await get_db_pool()
    
    async with db.acquire() as connection:
        # solution을 jsonb로 변환: {language: solution_code} 형태
        solution_json = json.dumps({language: solution})
        logger.info(f"Updating solution in database for problem_id: {problem_id} and language: {language}")
        await connection.execute("""
            UPDATE problems 
            SET solution = solution || $1::jsonb
            WHERE problem_id = $2
        """, solution_json, problem_id)