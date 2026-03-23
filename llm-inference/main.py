import os
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Optional
from transformers import pipeline, Pipeline
from sentence_transformers import SentenceTransformer

app = FastAPI(title="LLM Inference Service")

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "jinaai/jina-embeddings-v2-base-code")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")

embedding_model: Optional[SentenceTransformer] = None
llm_pipe: Optional[Pipeline] = None

def get_embedding_model() -> SentenceTransformer:
    """
    Lazy-loads and initializes the sentence transformer model for local CPU inference.
    
    Returns:
        SentenceTransformer: The loaded embedding model.
    """
    global embedding_model
    if embedding_model is None:
        print(f"Lazy Loading Embedding Model ({EMBEDDING_MODEL_NAME})...", flush=True)
        torch.set_num_threads(4) # Prevent CPU thread-explosion OOMs
        device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
        embedding_model = SentenceTransformer(
            EMBEDDING_MODEL_NAME, 
            trust_remote_code=True, 
            device=device,
            model_kwargs={"torch_dtype": torch.bfloat16}
        )
        embedding_model.max_seq_length = 2048 # Severe cap on attention matrices to block OOMs on large AST blocks
    return embedding_model

def get_llm_pipeline() -> Pipeline:
    """
    Lazy-loads and initializes the TinyLlama pipeline for chat synthesis.
    
    Returns:
        Pipeline: The loaded text-generation pipeline.
    """
    global llm_pipe
    if llm_pipe is None:
        print(f"Lazy Loading LLM Model ({LLM_MODEL_NAME})...", flush=True)
        device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")
        llm_pipe = pipeline(
            "text-generation", 
            model=LLM_MODEL_NAME, 
            device=device,
            torch_dtype=torch.bfloat16
        )
    return llm_pipe

@app.get("/health")
def health() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {"status": "ok", "message": "Inference server is active"}

class EmbedRequest(BaseModel):
    texts: List[str]

class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 256

@app.post("/embed")
def embed(req: EmbedRequest) -> Dict[str, List[List[float]]]:
    """
    Generates dense vector embeddings for a list of input texts.
    
    Args:
        req: EmbedRequest containing the strings to embed.
        
    Returns:
        Dict[str, List[List[float]]]: Dictionary containing the list of embeddings.
    """
    model = get_embedding_model()
    # Heavily throttle token pooling
    embeddings = model.encode(req.texts, batch_size=2).tolist()
    return {"embeddings": embeddings}

@app.post("/generate")
def generate(req: GenerateRequest) -> Dict[str, str]:
    """
    Generates a natural language response using the local LLM.
    
    Args:
        req: GenerateRequest containing the prompt and token limits.
        
    Returns:
        Dict[str, str]: Dictionary containing the generated text.
    """
    pipe = get_llm_pipeline()
    outputs = pipe(
        req.prompt, 
        max_new_tokens=req.max_new_tokens, 
        temperature=0.7, 
        top_k=50, 
        top_p=0.95, 
        truncation=True
    )
    generated = outputs[0]["generated_text"]
    response = generated.split("<|assistant|>")[-1].strip() if "<|assistant|>" in generated else generated
    return {"generated_text": response}
