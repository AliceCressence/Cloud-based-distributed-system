from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO
from ..database import get_db
from ..auth import get_current_user
from ..models import User
from ..schemas import FileListResponse, FileMetadata, FileChunkMap
from ..services.file_service import FileService

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload", response_model=FileMetadata)
async def upload_file(
    file: UploadFile = File(...),
    course_id: Optional[str] = None,
    folder_path: str = "/",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file to the distributed storage system"""
    db_file = await FileService.upload_file(
        db=db,
        user=current_user,
        file=file,
        course_id=course_id,
        folder_path=folder_path
    )
    return FileMetadata.model_validate(db_file)


@router.get("/", response_model=FileListResponse)
def list_files(
    course_id: Optional[str] = None,
    folder_path: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's files with optional filtering"""
    return FileService.get_user_files(
        db=db,
        user=current_user,
        course_id=course_id,
        folder_path=folder_path,
        skip=skip,
        limit=limit
    )


@router.get("/{file_id}", response_model=FileMetadata)
def get_file_info(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get file metadata"""
    from ..models import File, FileStatus
    db_file = db.query(File).filter(
        File.file_id == file_id,
        File.user_id == current_user.id,
        File.status == FileStatus.ACTIVE
    ).first()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileMetadata.model_validate(db_file)


@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a file"""
    # Get file metadata
    from ..models import File, FileStatus
    db_file = db.query(File).filter(
        File.file_id == file_id,
        File.user_id == current_user.id,
        File.status == FileStatus.ACTIVE
    ).first()
    
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Download file data
    file_data = await FileService.download_file(db, file_id, current_user)
    
    # Return as streaming response
    return StreamingResponse(
        BytesIO(file_data),
        media_type=db_file.content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{db_file.filename}"'
        }
    )


@router.delete("/{file_id}")
def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a file"""
    success = FileService.delete_file(db, file_id, current_user)
    return {"success": success, "message": "File deleted successfully"}


@router.get("/{file_id}/chunks", response_model=FileChunkMap)
def get_file_chunks(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chunk distribution for a file"""
    return FileService.get_file_chunks(db, file_id, current_user)
