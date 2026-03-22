import os

class Settings:
    PROJECT_NAME: str = "Semantic Code Search Engine"
    
    # Resolve path for local ChromaDB storage
    CHROMA_PATH: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "chroma_data")
    
    EMBEDDING_MODEL: str = "jinaai/jina-embeddings-v2-base-code"
    LLM_MODEL: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    
settings = Settings()
