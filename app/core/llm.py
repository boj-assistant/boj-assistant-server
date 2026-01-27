from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=settings.GOOGLE_API_KEY,
    temperature=0.8,
    thinking_budget=0,
    top_p=0.5,  # 다양성과 일관성의 균형
)
logger.info(f"LLM initialized with settings: {settings}")