from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel
from services.ingestion import process_upload
from services.embeddings import index_chunks, search_codebase

router = APIRouter()

@router.post("/api/upload")
async def upload_archive(file: UploadFile = File(...)):
    """
    Endpoint for uploading a zipped codebase repository.
    Extracts the tree, scans for python files, and later parsing/embedding logic.
    """
    result = process_upload(file)
    chunks = result.get("chunks", [])
    
    # Store embeddings in local database if chunks were generated
    if chunks:
        index_chunks(chunks)

    return {
        "status": "success",
        "message": "Successfully processed archive and chunked python files.",
        "python_files_discovered": result["python_files_discovered"],
        "total_chunks": result["total_chunks"]
    }

class SearchQuery(BaseModel):
    query: str

@router.post("/api/search")
async def search(query: SearchQuery):
    """
    Endpoint for querying the codebase using natural language.
    """
    results = search_codebase(query.query)
    return {"results": results}
