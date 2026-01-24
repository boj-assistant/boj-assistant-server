"""
매번 각 파일에서 load_dotenv()할 필요가 없다
.env 파일을 읽어 환경변수를 모두 해당 클래스로 로드해줌
특정 설정값이 없으면 바로 ValidationError 발생
"""
from pydantic_settings import BaseSettings
from pydantic import computed_field

class Settings(BaseSettings):

    PORT: int
    
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    
    GOOGLE_API_KEY: str
    
    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # 정의되지 않은 환경 변수는 무시

settings = Settings()