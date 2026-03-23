import httpx
from core.config import settings
from typing import List

class HttpLLMClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    def embed(self, texts: List[str]) -> List[List[float]]:
        # Connects to dedicated LLM inference container
        response = httpx.post(f"{self.base_url}/embed", json={"texts": texts}, timeout=120.0)
        response.raise_for_status()
        return response.json()["embeddings"]

    def generate_answer(self, prompt: str, max_new_tokens: int = 256) -> str:
        response = httpx.post(f"{self.base_url}/generate", json={
            "prompt": prompt,
            "max_new_tokens": max_new_tokens
        }, timeout=120.0)
        response.raise_for_status()
        return response.json()["generated_text"]

llm_client = HttpLLMClient(settings.LLM_BASE_URL)
