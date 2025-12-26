import tempfile
import os

def save_temp_pdf(file_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        return tmp.name  # return full path

def delete_temp_file(path):
    if os.path.exists(path):
        os.remove(path)
