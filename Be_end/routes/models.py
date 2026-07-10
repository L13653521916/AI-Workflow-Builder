from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from openai import OpenAI

from database import get_db
from models import User, ModelProfile
from schemas import (
    ModelProfileCreate,
    ModelProfileUpdate,
    ModelProfileResponse,
    ModelProfileDetail,
    ModelTestRequest,
    DEFAULT_MODEL_CONFIG,
)
from security import get_current_user

router = APIRouter(prefix="/models", tags=["models"])


def _merge_config(config) -> dict:
    merged = {**DEFAULT_MODEL_CONFIG}
    if not config:
        return merged
    for section, values in config.items():
        if section in merged and isinstance(values, dict):
            merged[section] = {**merged[section], **values}
        else:
            merged[section] = values
    return merged


def _get_profile_or_404(db: Session, profile_id: int, user_id: int) -> ModelProfile:
    profile = db.query(ModelProfile).filter(
        ModelProfile.id == profile_id,
        ModelProfile.user_id == user_id,
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Model profile not found")
    return profile


def _clear_default(db: Session, user_id: int, exclude_id=None):
    q = db.query(ModelProfile).filter(
        ModelProfile.user_id == user_id,
        ModelProfile.is_default == True,
    )
    if exclude_id:
        q = q.filter(ModelProfile.id != exclude_id)
    for p in q.all():
        p.is_default = False


@router.get("", response_model=List[ModelProfileResponse])
def list_model_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profiles = (
        db.query(ModelProfile)
        .filter(ModelProfile.user_id == current_user.id)
        .order_by(ModelProfile.is_default.desc(), ModelProfile.updated_at.desc(), ModelProfile.created_at.desc())
        .all()
    )
    return [ModelProfileResponse.from_orm_model(p) for p in profiles]


@router.post("", response_model=ModelProfileDetail, status_code=201)
def create_model_profile(
    body: ModelProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if body.is_default:
        _clear_default(db, current_user.id)

    profile = ModelProfile(
        user_id=current_user.id,
        name=body.name,
        provider=body.provider,
        base_url=body.base_url.rstrip("/"),
        api_key=body.api_key,
        model_id=body.model_id,
        config_json=_merge_config(body.config_json),
        is_default=body.is_default,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return ModelProfileDetail.from_orm_model(profile)


@router.get("/{profile_id}", response_model=ModelProfileDetail)
def get_model_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_profile_or_404(db, profile_id, current_user.id)
    return ModelProfileDetail.from_orm_model(profile)


@router.put("/{profile_id}", response_model=ModelProfileDetail)
def update_model_profile(
    profile_id: int,
    body: ModelProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_profile_or_404(db, profile_id, current_user.id)
    data = body.model_dump(exclude_unset=True)

    if data.get("is_default"):
        _clear_default(db, current_user.id, exclude_id=profile_id)

    if "base_url" in data and data["base_url"]:
        data["base_url"] = data["base_url"].rstrip("/")
    if "config_json" in data and data["config_json"] is not None:
        data["config_json"] = _merge_config(data["config_json"])

    for field, value in data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return ModelProfileDetail.from_orm_model(profile)


@router.delete("/{profile_id}")
def delete_model_profile(
    profile_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_profile_or_404(db, profile_id, current_user.id)
    db.delete(profile)
    db.commit()
    return {"detail": "ok"}


@router.post("/{profile_id}/test")
def test_model_profile(
    profile_id: int,
    body: ModelTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = _get_profile_or_404(db, profile_id, current_user.id)

    try:
        client = OpenAI(api_key=profile.api_key, base_url=profile.base_url)
        resp = client.chat.completions.create(
            model=profile.model_id,
            messages=[{"role": "user", "content": body.message}],
            max_tokens=64,
        )
        content = resp.choices[0].message.content if resp.choices else ""
        return {
            "success": True,
            "reply": content,
            "model": profile.model_id,
            "baseUrl": profile.base_url,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
