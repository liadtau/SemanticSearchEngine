import chromadb
from core.config import settings

def get_chroma_client():
    return chromadb.PersistentClient(path=settings.CHROMA_PATH)

chroma_client = get_chroma_client()
