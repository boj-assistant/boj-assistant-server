from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

_reviewer_prompt: Optional[str] = None

def load_prompt() -> str:
    global _reviewer_prompt
    
    if _reviewer_prompt is None:
        # 프로젝트 루트 디렉토리 기준으로 reviewer.md 찾기
        project_root = Path(__file__).parent.parent.parent
        prompt_file = project_root / "reviewer.md"
        
        try:
            with open(prompt_file, "r", encoding="utf-8") as f:
                _reviewer_prompt = f.read()
            logger.info(f"프롬프트 파일 로드 완료: {prompt_file}")
        except FileNotFoundError:
            logger.error(f"프롬프트 파일을 찾을 수 없습니다: {prompt_file}")
            raise
        except Exception as e:
            logger.error(f"프롬프트 파일 로드 중 오류 발생: {e}")
            raise
    
    return _reviewer_prompt

def get_reviewer_prompt() -> str:
    """
    캐시된 reviewer 프롬프트를 반환합니다.
    load_reviewer_prompt()가 먼저 호출되어야 합니다.
    """
    if _reviewer_prompt is None:
        raise RuntimeError("프롬프트가 아직 로드되지 않았습니다. lifespan에서 load_reviewer_prompt()를 먼저 호출하세요.")
    return _reviewer_prompt 
