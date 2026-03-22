from fastapi import APIRouter, File, UploadFile
from services.ingestion import process_upload

router = APIRouter()

@router.post("/api/upload")
async def upload_archive(file: UploadFile = File(...)):
    """
    Endpoint for uploading a zipped codebase repository.
    Extracts the tree, scans for python files, and later parsing/embedding logic.
    """
    num_files = process_upload(file)
    return {
        "status": "success",
        "message": "Successfully processed archive.",
        "python_files_discovered": num_files
    }
