import pytest
from backend.ingest_service import ingest_file
from fastapi import HTTPException
import os

# Mock PyPDFLoader and TextLoader if needed

def test_ingest_file_not_found(monkeypatch):
    monkeypatch.setattr('backend.ingest_service.UPLOAD_DIR', '/tmp/doesnotexist')
    with pytest.raises(HTTPException) as exc:
        ingest_file('missing.txt')
    assert exc.value.status_code == 404

# Add more tests for supported/unsupported file types as needed
