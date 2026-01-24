from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=settings.GOOGLE_API_KEY,
    temperature=0.4,
    # max_tokens=4000,
    # top_p=0.95,  # 다양성과 일관성의 균형
    # top_k=40,
)