"""
File Storage and Evidence Upload Utilities.
Secures uploaded evidence, validates extensions and file size limits.
"""

import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "pdf"}

def allowed_file(filename: str) -> bool:
    """Checks whether the filename has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_evidence_file(file_storage) -> tuple[str, str, str]:
    """
    Saves an uploaded file safely to the configured upload folder.
    Returns (relative_file_path, file_type, original_filename)
    """
    if not file_storage or not file_storage.filename:
        raise ValueError("No file provided.")

    original_filename = secure_filename(file_storage.filename)
    if not allowed_file(original_filename):
        raise ValueError(f"File type not permitted. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")

    ext = original_filename.rsplit(".", 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
    
    upload_dir = current_app.config.get("UPLOAD_FOLDER", "backend/uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    full_path = os.path.join(upload_dir, unique_filename)
    file_storage.save(full_path)

    mime_type = file_storage.content_type or (f"image/{ext}" if ext != "pdf" else "application/pdf")
    relative_path = f"uploads/{unique_filename}"
    
    return relative_path, mime_type, original_filename
