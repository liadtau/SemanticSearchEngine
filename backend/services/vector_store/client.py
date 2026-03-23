import chromadb
from core.config import settings
from typing import List, Dict, Any

class ChromaVectorStore:
    def __init__(self):
        self._client = None
        
    @property
    def client(self):
        if self._client is None:
            self._client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        return self._client
        
    def get_collection(self):
        return self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME, 
            metadata={"hnsw:space": "cosine"}
        )
        
    def reset_collection(self):
        try:
            self.client.delete_collection(name=settings.COLLECTION_NAME)
        except Exception:
            pass
        return self.get_collection()

    def upsert_chunks(self, ids: List[str], embeddings: List[List[float]], metadatas: List[Dict[str, Any]], documents: List[str]):
        collection = self.get_collection()
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents
        )

    def search(self, query_embedding: List[float], top_k: int = 5) -> Dict[str, Any]:
        collection = self.get_collection()
        return collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

vector_store = ChromaVectorStore()
