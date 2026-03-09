import pytest
from backend.chat_service import chat_with_file
from fastapi import HTTPException
import os

def test_chat_file_not_found(monkeypatch):
    monkeypatch.setattr('backend.chat_service.UPLOAD_DIR', '/tmp/doesnotexist')
    with pytest.raises(HTTPException) as exc:
        chat_with_file('missing.txt', 'What is this?')
    assert exc.value.status_code == 404

# Add more tests for supported/unsupported file types as needed
