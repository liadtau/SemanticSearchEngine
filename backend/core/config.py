import os

class Settings:
    PROJECT_NAME: str = "Semantic Code Search Engine API"
    
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "chroma")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", "8000"))
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "codebase")
    
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://llm:8002")

settings = Settings()
