import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import tempfile
import zipfile
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_and_rag():
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
        zip_path = f.name
        
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.writestr("test1.py", "class Calculator:\n    def add(self, a, b):\n        print('adding numbers')\n        return a + b\n")
        
    with open(zip_path, "rb") as f:
        response = client.post("/api/upload", files={"file": ("dummy.zip", f, "application/zip")})
        
    os.remove(zip_path)
    assert response.status_code == 200
    
    print("Testing RAG search (this may download the LLM and take time)...")
    search_res = client.post("/api/search", json={"query": "how to add two numbers?"})
    
    assert search_res.status_code == 200
    res_json = search_res.json()
    
    print("\n================\nAgent Message:\n", res_json["agent_message"])
    assert len(res_json["references"]) > 0
    print("\nTop Relevance Score:", res_json["references"][0]["relevance_score"], "%\n================")
    
if __name__ == "__main__":
    test_upload_and_rag()
    print("RAG Search test passed successfully!")
