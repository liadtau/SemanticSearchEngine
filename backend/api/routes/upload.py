import logging
from fastapi import APIRouter, File, UploadFile, BackgroundTasks
from schemas.ingestion import UploadResponseModel
from services.ingestion import process_upload
from services.vector_store.client import vector_store
from services.llm.client import llm_client

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()

@router.post("/api/upload", response_model=UploadResponseModel)
async def upload_archive(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Endpoint for uploading a zipped codebase repository.
    Extracts the tree, scans for python files, and delegates embedding to a BackgroundTask.
    """
    logger.info(f"Starting upload for file: {file.filename}")
    result = process_upload(file)
    chunks = result.get("chunks", [])
    
    if chunks:
        vector_store.reset_collection()
        
        def background_upsert(chunks_to_process):
            batch_size = 2
            logger.info(f"Commencing background embedding for {len(chunks_to_process)} chunks...")
            for i in range(0, len(chunks_to_process), batch_size):
                batch = chunks_to_process[i:i + batch_size]
                texts = [chunk["code_snippet"] for chunk in batch]
                
                try:
                    embeddings = llm_client.embed(texts)
                    ids = [f"chunk_{i+j}" for j in range(len(batch))]
                    metadatas = [
                        {
                            "file_path": c.get("file_path", ""),
                            "start_line": c.get("start_line", 0),
                            "end_line": c.get("end_line", 0),
                            "type": c.get("type", "unknown")
                        } for c in batch
                    ]
                    vector_store.upsert_chunks(ids, embeddings, metadatas, texts)
                except Exception as e:
                    logger.error(f"Error embedding batch at chunk index {i}: {e}")
            logger.info("Background embedding sequence fully complete.")

        # Queue the heavy ML embedding sequence safely to the background worker pool
        background_tasks.add_task(background_upsert, chunks)
        
    logger.info(f"Successfully unpacked {result['total_chunks']} chunks from {result['python_files_discovered']} Python files. Passing embedding loop to background task scheduler.")

    return UploadResponseModel(
        status="success",
        message="Successfully processed archive and chunked python files.",
        python_files_discovered=result["python_files_discovered"],
        total_chunks=result["total_chunks"]
    )
