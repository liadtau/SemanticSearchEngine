from pydantic import BaseModel

class UploadResponseModel(BaseModel):
    status: str
    message: str
    python_files_discovered: int
    total_chunks: int
