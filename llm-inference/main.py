import os
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from transformers import pipeline
from sentence_transformers import SentenceTransformer

app = FastAPI(title="LLM Inference Service")

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "jinaai/jina-embeddings-v2-base-code")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")

embedding_model = None
llm_pipe = None

def get_embedding_model():
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
    return embedding_model

def get_llm_pipeline():
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
def health():
    return {"status": "ok", "message": "Inference server is active"}

class EmbedRequest(BaseModel):
    texts: List[str]

class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 256

@app.post("/embed")
def embed(req: EmbedRequest):
    model = get_embedding_model()
    embeddings = model.encode(req.texts).tolist()
    return {"embeddings": embeddings}

@app.post("/generate")
def generate(req: GenerateRequest):
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
