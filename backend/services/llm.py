import torch
from transformers import pipeline
from core.config import settings

print(f"Loading LLM Model ({settings.LLM_MODEL})...")
# Using a quantized or smaller model capable of running locally
device = "mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu")

pipe = pipeline(
    "text-generation", 
    model=settings.LLM_MODEL, 
    device=device
)
print(f"LLM Model loaded on {device}!")

def generate_rag_response(query: str, snippets: list[str]) -> str:
    """Uses a local LLM to synthesize a natural language response based on code snippets."""
    snippets_text = "\n\n---\n\n".join(snippets)
    prompt = f"""<|system|>
You are an expert programming assistant. Given the following code snippets retrieved from the user's codebase, answer the user's question clearly and concisely.
Code Snippets:
{snippets_text}
</s>
<|user|>
{query}
</s>
<|assistant|>
"""
    
    outputs = pipe(
        prompt, 
        max_new_tokens=256, 
        temperature=0.7, 
        top_k=50, 
        top_p=0.95, 
        truncation=True
    )
    
    generated = outputs[0]["generated_text"]
    # Provide just the new generated text
    response = generated.split("<|assistant|>")[-1].strip()
    return response
