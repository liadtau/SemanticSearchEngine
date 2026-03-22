from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import router as api_router

app = FastAPI(title="Semantic Code Search Engine")

# Add CORS middleware to allow localhost frontend to access the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, accepting all origins. Can be restricted to localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Semantic Code Search Engine API is running"}
