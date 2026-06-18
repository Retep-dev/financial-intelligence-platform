from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File

from services.ingestion.storage.file_storage import save_file
from services.ingestion.service import create_document_record

router = APIRouter(
    prefix="/documents",
    tags=["Documents"]
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    file_path = save_file(file)

    document = create_document_record(
        original_filename=file.filename,
        file_path=file_path
    )

    return {
        "document_id": document.id,
        "filename": document.file_name,
        "file_type": document.document_type,
        "stored_file": document.stored_file_name,
        "file_path": document.file_path,
        "status": "uploaded_successfully"
    }
