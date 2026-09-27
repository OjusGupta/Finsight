from langchain_groq import ChatGroq
from backend.app.core.config import settings

def get_llm():
    if settings.GROQ_API_KEY:
        return ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=0,
            groq_api_key=settings.GROQ_API_KEY,
        )
    raise ValueError("No GROQ_API_KEY provided.")
