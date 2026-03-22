from fastapi import APIRouter
from schemas.search import SearchQuery, SearchResponseModel, ReferenceModel
from services.embeddings import search_codebase
from services.llm import generate_rag_response

router = APIRouter()

@router.post("/api/search", response_model=SearchResponseModel)
async def search(query: SearchQuery):
    """
    Endpoint for querying the codebase using natural language.
    Synthesizes the LLM reply using augmented chunks.
    """
    results = search_codebase(query.query)
    
    # Extract structural chunks for context
    snippets = [res["code_snippet"] for res in results]
    
    # Agent chat synthesis
    agent_message = "No relevant code found."
    if snippets:
        try:
            agent_message = generate_rag_response(query.query, snippets)
        except Exception as e:
            agent_message = f"Error generating response: {str(e)}"
            
    references = [ReferenceModel(**res) for res in results]
            
    return SearchResponseModel(
        agent_message=agent_message,
        references=references
    )
