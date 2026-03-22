import os
import tempfile
import zipfile
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload_and_search():
    # 1. Upload dummy zip
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
        zip_path = f.name
        
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.writestr("test1.py", "class Calculator:\n    def add(self, a, b):\n        print('adding numbers')\n        return a + b\n")
        
    with open(zip_path, "rb") as f:
        response = client.post("/api/upload", files={"file": ("dummy.zip", f, "application/zip")})
        
    os.remove(zip_path)
    print("Upload Response:", response.json())
    assert response.status_code == 200
    
    # 2. Search
    search_res = client.post("/api/search", json={"query": "addition of two numbers"})
    
    # Note: the very first time the model runs, it downloads weights. TestClient might timeout if we don't have enough time,
    # but since it's local synchronous test, it should wait indefinitely.
    print("Search Response:", search_res.status_code)
    
    assert search_res.status_code == 200
    results = search_res.json()["results"]
    assert len(results) > 0
    print("Top result snippet:")
    print(results[0]["code_snippet"])
    
if __name__ == "__main__":
    test_upload_and_search()
    print("Search and Embedding test passed successfully!")
