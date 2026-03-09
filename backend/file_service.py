import os
import logging
from fastapi import HTTPException

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))


def save_file(file):
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())
        logging.info(f"Uploaded file: {file.filename}")
        return file.filename
    except Exception as e:
        logging.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {e}")


def list_files():
    try:
        if not os.path.exists(UPLOAD_DIR):
            logging.error(f"UPLOAD_DIR does not exist: {UPLOAD_DIR}")
            raise HTTPException(status_code=500, detail=f"UPLOAD_DIR does not exist: {UPLOAD_DIR}")
        files = os.listdir(UPLOAD_DIR)
        logging.info(f"Listing files: {files}")
        return files
    except Exception as e:
        logging.error(f"File listing failed: {e}")
        raise HTTPException(status_code=500, detail=f"File listing failed: {e}")
