import tempfile
import zipfile
import os
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_upload():
    # create dummy zip
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as f:
        zip_path = f.name
        
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        zipf.writestr("test1.py", "print('hello')")
        zipf.writestr("venv/test2.py", "print('hello venv')") # Should be ignored
        zipf.writestr("test3.txt", "hello txt") # Not a python file
        # Test traversal
        # Path traversal with `../` might fail zip creation but let's test extraction
        
    with open(zip_path, "rb") as f:
        response = client.post("/api/upload", files={"file": ("dummy.zip", f, "application/zip")})
        
    os.remove(zip_path)
    
    print("Response status:", response.status_code)
    print("Response JSON:", response.json())
    
    assert response.status_code == 200
    assert response.json()["python_files_discovered"] == 1 # Because venv ignored, and test3.txt is not py

if __name__ == "__main__":
    test_upload()
    print("Test passed successfully!")
