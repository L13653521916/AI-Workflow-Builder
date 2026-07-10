import os
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from config import settings
from database import get_db
from models import User, KnowledgeBase, Document
from schemas import KnowledgeBaseCreate, KnowledgeBaseResponse, DocumentResponse
from security import get_current_user

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}


def _ensure_upload_dir():
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


def _get_kb_or_404(db: Session, kb_id: int, user_id: int) -> KnowledgeBase:
    kb = db.query(KnowledgeBase).filter(
        KnowledgeBase.id == kb_id,
        KnowledgeBase.user_id == user_id,
    ).first()
    if not kb:
        raise HTTPException(status_code=404, detail="Knowledge base not found")
    return kb


def _kb_upload_dir(kb_id: int) -> Path:
    return Path(settings.UPLOAD_DIR) / str(kb_id)


@router.get("", response_model=List[KnowledgeBaseResponse])
def list_knowledge_bases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kbs = (
        db.query(KnowledgeBase)
        .filter(KnowledgeBase.user_id == current_user.id)
        .order_by(KnowledgeBase.created_at.desc())
        .all()
    )
    return [KnowledgeBaseResponse.from_orm_model(kb) for kb in kbs]


@router.post("", response_model=KnowledgeBaseResponse, status_code=201)
def create_knowledge_base(
    body: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kb = KnowledgeBase(
        user_id=current_user.id,
        name=body.name,
        description=body.description,
    )
    db.add(kb)
    db.commit()
    db.refresh(kb)
    _kb_upload_dir(kb.id).mkdir(parents=True, exist_ok=True)
    return KnowledgeBaseResponse.from_orm_model(kb)


@router.delete("/{kb_id}")
def delete_knowledge_base(
    kb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kb = _get_kb_or_404(db, kb_id, current_user.id)

    upload_dir = _kb_upload_dir(kb_id)
    if upload_dir.exists():
        shutil.rmtree(upload_dir, ignore_errors=True)

    db.delete(kb)
    db.commit()
    return {"detail": "ok"}


@router.get("/{kb_id}/documents", response_model=List[DocumentResponse])
def list_documents(
    kb_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _get_kb_or_404(db, kb_id, current_user.id)
    docs = (
        db.query(Document)
        .filter(Document.kb_id == kb_id)
        .order_by(Document.created_at.desc())
        .all()
    )
    return [DocumentResponse.from_orm_model(doc) for doc in docs]


@router.post("/{kb_id}/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    kb_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kb = _get_kb_or_404(db, kb_id, current_user.id)

    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    _ensure_upload_dir()
    upload_dir = _kb_upload_dir(kb_id)
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = file.filename.replace("..", "").replace("/", "").replace("\\", "")
    file_path = upload_dir / safe_name

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    doc = Document(
        kb_id=kb_id,
        filename=safe_name,
        file_path=str(file_path),
        chunk_count=0,
        status="ready",
    )
    db.add(doc)
    kb.doc_count = (kb.doc_count or 0) + 1
    db.commit()
    db.refresh(doc)
    return DocumentResponse.from_orm_model(doc)


@router.delete("/{kb_id}/documents/{doc_id}")
def delete_document(
    kb_id: int,
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    kb = _get_kb_or_404(db, kb_id, current_user.id)
    doc = db.query(Document).filter(
        Document.id == doc_id,
        Document.kb_id == kb_id,
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    db.delete(doc)
    kb.doc_count = max((kb.doc_count or 1) - 1, 0)
    db.commit()
    return {"detail": "ok"}
