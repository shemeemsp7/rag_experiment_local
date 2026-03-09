import os
import tempfile
import pytest
from backend.file_service import save_file, list_files
from fastapi import UploadFile

class DummyUploadFile:
    def __init__(self, filename, content):
        self.filename = filename
        self.file = tempfile.TemporaryFile()
        self.file.write(content)
        self.file.seek(0)

@pytest.fixture
def setup_tmp_dir(monkeypatch):
    tmp_dir = tempfile.mkdtemp()
    monkeypatch.setattr('backend.file_service.UPLOAD_DIR', tmp_dir)
    yield tmp_dir
    os.rmdir(tmp_dir)

def test_save_file_and_list_files(setup_tmp_dir):
    file = DummyUploadFile('test.txt', b'hello world')
    filename = save_file(file)
    assert filename == 'test.txt'
    files = list_files()
    assert 'test.txt' in files
