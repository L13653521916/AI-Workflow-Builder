from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from database import get_db
from models import User, Workflow
from schemas import WorkflowCreate, WorkflowUpdate, WorkflowResponse
from security import get_current_user

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("", response_model=List[WorkflowResponse])
def list_workflows(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Workflow)
        .filter(Workflow.user_id == current_user.id)
        .order_by(func.coalesce(Workflow.updated_at, Workflow.created_at).desc())
        .all()
    )


@router.post("", response_model=WorkflowResponse, status_code=201)
def create_workflow(
    body: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wf = Workflow(user_id=current_user.id, name=body.name, description=body.description)
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return wf


@router.get("/{wf_id}", response_model=WorkflowResponse)
def get_workflow(
    wf_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wf = db.query(Workflow).filter(
        Workflow.id == wf_id, Workflow.user_id == current_user.id
    ).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return wf


@router.put("/{wf_id}", response_model=WorkflowResponse)
def update_workflow(
    wf_id: int,
    body: WorkflowUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wf = db.query(Workflow).filter(
        Workflow.id == wf_id, Workflow.user_id == current_user.id
    ).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(wf, field, value)

    db.commit()
    db.refresh(wf)
    return wf


@router.delete("/{wf_id}")
def delete_workflow(
    wf_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    wf = db.query(Workflow).filter(
        Workflow.id == wf_id, Workflow.user_id == current_user.id
    ).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.delete(wf)
    db.commit()
    return {"detail": "ok"}