from fastapi import APIRouter, File, UploadFile
from services.ingestion import process_upload

router = APIRouter()

@router.post("/api/upload")
async def upload_archive(file: UploadFile = File(...)):
    """
    Endpoint for uploading a zipped codebase repository.
    Extracts the tree, scans for python files, and later parsing/embedding logic.
    """
    result = process_upload(file)
    return {
        "status": "success",
        "message": "Successfully processed archive and chunked python files.",
        "python_files_discovered": result["python_files_discovered"],
        "total_chunks": result["total_chunks"]
    }
