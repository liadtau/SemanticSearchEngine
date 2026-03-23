import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.upload import router as upload_router
from api.routes.search import router as search_router
from core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(title=settings.PROJECT_NAME)

# Add CORS middleware to allow localhost frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, accepting all origins. Can be restricted to localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(search_router)

@app.get("/")
def read_root():
    return {"message": f"{settings.PROJECT_NAME} API is running"}
