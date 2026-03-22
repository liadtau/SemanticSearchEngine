import os
import shutil
import tempfile
import zipfile
import tarfile
from typing import Union
from pathlib import Path
from fastapi import UploadFile, HTTPException
from services.parser import chunk_python_file

def is_safe_path(base_dir: Union[str, Path], target_path: Union[str, Path]) -> bool:
    """Ensure the target path is within the base directory to prevent path traversal."""
    base_dir = Path(base_dir).resolve()
    target_path = (base_dir / target_path).resolve()
    return target_path.is_relative_to(base_dir)

def safe_extract_zip(archive_path: Union[str, Path], target_dir: Union[str, Path]):
    target_dir = Path(target_dir)
    with zipfile.ZipFile(archive_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            if not is_safe_path(target_dir, member):
                raise HTTPException(status_code=400, detail=f"Path traversal detected in zip archive: {member}")
        zip_ref.extractall(target_dir)

def safe_extract_tar(archive_path: Union[str, Path], target_dir: Union[str, Path]):
    target_dir = Path(target_dir)
    with tarfile.open(archive_path, 'r:*') as tar_ref:
        for member in tar_ref.getmembers():
            if not is_safe_path(target_dir, member.name):
                raise HTTPException(status_code=400, detail=f"Path traversal detected in tar archive: {member.name}")
        
        # Python 3.12+ supports filter='data' but we do manual checks for broader compatibility
        tar_ref.extractall(target_dir)

def process_upload(file: UploadFile) -> dict:
    filename = file.filename or ""
    if not (filename.endswith('.zip') or filename.endswith('.tar.gz') or filename.endswith('.tar') or filename.endswith('.tgz')):
        raise HTTPException(status_code=400, detail="Invalid file type. Only .zip and .tar.gz are supported.")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        archive_path = temp_dir_path / filename
        
        # Save the uploaded file safely
        try:
            with open(archive_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")
            
        # Extract the file safely
        try:
            if filename.endswith('.zip'):
                safe_extract_zip(archive_path, temp_dir_path)
            else:
                safe_extract_tar(archive_path, temp_dir_path)
        except tarfile.TarError as e:
            raise HTTPException(status_code=400, detail=f"Invalid tar archive: {str(e)}")
        except zipfile.BadZipFile as e:
            raise HTTPException(status_code=400, detail=f"Invalid zip archive: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error extracting archive: {str(e)}")

        # Find all python files, ignoring specific unneeded directories
        py_files = []
        ignore_dirs = {'.git', 'venv', '.tox', '__pycache__', 'env', '.env'}
        
        for root, dirs, files in os.walk(temp_dir_path):
            # Modify 'dirs' in-place so os.walk skips ignored directories traversing downwards
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            for file_name in files:
                if file_name.endswith('.py'):
                    py_files.append(os.path.join(root, file_name))
        
        all_chunks = []
        for py_file in py_files:
            chunks = chunk_python_file(py_file, str(temp_dir_path))
            all_chunks.extend(chunks)
        
        return {
            "python_files_discovered": len(py_files),
            "total_chunks": len(all_chunks)
        }
