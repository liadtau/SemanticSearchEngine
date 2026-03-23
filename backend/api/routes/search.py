import logging
from fastapi import APIRouter
from schemas.search import SearchQuery, SearchResponseModel, ReferenceModel
from services.vector_store.client import vector_store
from services.llm.client import llm_client

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()

@router.post("/api/search", response_model=SearchResponseModel)
async def search(query: SearchQuery) -> SearchResponseModel:
    """
    Endpoint for querying the codebase using natural language.
    
    This function orchestrates:
    1. Query embedding generation via the LLM service.
    2. Semantic search in ChromaDB.
    3. Retrieval-Augmented Generation (RAG) to synthesize a final answer.
    
    Args:
        query: SearchQuery containing the user's natural language question.
        
    Returns:
        SearchResponseModel: The synthesized agent reply along with relevant code references.
    """
    logger.info(f"Search query received: '{query.query}'")
    # Create remote embedding
    query_embedding = llm_client.embed([query.query])[0]
    
    # Remote HTTP Search Chroma
    results = vector_store.search(query_embedding, top_k=5)
    
    formatted_results = []
    snippets = []
    
    if results.get('documents') and len(results['documents']) > 0:
        docs = results['documents'][0]
        metas = results['metadatas'][0]
        distances = results.get('distances', [[0]*len(docs)])[0]
        
        for doc, meta, dist in zip(docs, metas, distances):
            # Convert cosine distance to relevance percentage (cosine distance: 0 is identical)
            relevance = max(0.0, 1.0 - float(dist))
            formatted_results.append({
                "code_snippet": doc,
                "relevance_score": int(relevance * 100),
                **meta
            })
            snippets.append(doc)
            
    # Agent chat synthesis
    agent_message = "No relevant code found."
    if snippets:
        snippets_text = "\n\n---\n\n".join(snippets)
        prompt = f"""<|system|>
You are an expert programming assistant. Given the following code snippets retrieved from the user's codebase, answer the user's question clearly and concisely.
Code Snippets:
{snippets_text}
</s>
<|user|>
{query.query}
</s>
<|assistant|>
"""
        try:
            agent_message = llm_client.generate_answer(prompt)
        except Exception as e:
            agent_message = f"Error generating response: {str(e)}"
            
    references = [ReferenceModel(**res) for res in formatted_results]
    
    top_score = formatted_results[0]['relevance_score'] if formatted_results else 0
    logger.info(f"Returned {len(formatted_results)} search results. Top score: {top_score}")
            
    return SearchResponseModel(
        agent_message=agent_message,
        references=references
    )
