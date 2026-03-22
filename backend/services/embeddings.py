from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from core.config import settings
from db.database import chroma_client

# Initialize ChromaDB local collection using central client
collection = chroma_client.get_or_create_collection(name="codebase")

# Initialize Hugging Face Jina Embedding Model
# We set trust_remote_code=True as instructed for jina models
model = SentenceTransformer(settings.EMBEDDING_MODEL, trust_remote_code=True)

def index_chunks(chunks: List[Dict[str, Any]]):
    """Embeds and indexes code chunks in ChromaDB."""
    if not chunks:
        return
        
    global collection
    # Clear existing collection by deleting and recreating
    try:
        chroma_client.delete_collection(name="codebase")
    except Exception:
        pass
    collection = chroma_client.get_or_create_collection(name="codebase")
    
    # Process the chunks in batches to limit memory usage
    batch_size = 32
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [chunk["code_snippet"] for chunk in batch]
        
        # Calculate embeddings
        # model.encode returns a NumPy array by default, we convert to list
        embeddings = model.encode(texts).tolist()
        
        # Prepare metadata and IDs for Upsert
        ids = [f"chunk_{i+j}" for j in range(len(batch))]
        metadatas = []
        for chunk in batch:
            metadatas.append({
                "file_path": chunk.get("file_path", ""),
                "start_line": chunk.get("start_line", 0),
                "end_line": chunk.get("end_line", 0),
                "type": chunk.get("type", "unknown")
            })
            
        collection.upsert(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=texts
        )

def search_codebase(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Searches the ChromaDB codebase for a natural language query."""
    query_embedding = model.encode(query).tolist()
    
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )
    
    formatted_results = []
    if results.get('documents') and len(results['documents']) > 0:
        docs = results['documents'][0]
        metas = results['metadatas'][0]
        distances = results.get('distances', [[0]*len(docs)])[0]
        
        for doc, meta, dist in zip(docs, metas, distances):
            # Convert cosine distance to relevance string (heuristic approach)
            relevance = max(0.0, 1.0 - float(dist))
            relevance_pct = int(relevance * 100)
            
            formatted_results.append({
                "code_snippet": doc,
                "relevance_score": relevance_pct,
                **meta
            })
            
    return formatted_results
