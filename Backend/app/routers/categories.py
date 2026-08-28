from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime

from app.database import get_db
from app import models, schemas
from app.routers.auth import require_auth

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[schemas.CategoryOut])
def list_categories(type: str | None = None, db: Session = Depends(get_db)):
    q = db.query(models.Category)
    if type:
        q = q.filter(models.Category.type == type)
    return q.all()


@router.post("", response_model=schemas.CategoryOut)
def create_category(payload: schemas.CategoryCreate, db: Session = Depends(get_db), _auth: str = Depends(require_auth)):
    if payload.type not in ("income", "expense"):
        raise HTTPException(400, "type must be income or expense")
    obj = models.Category(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), _auth: str = Depends(require_auth)):
    obj = db.get(models.Category, category_id)
    if not obj:
        raise HTTPException(404, "category not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}


@router.put("/{category_id}", response_model=schemas.CategoryOut)
def update_category(category_id: int, payload: schemas.CategoryCreate, db: Session = Depends(get_db), _auth: str = Depends(require_auth)):
    obj = db.get(models.Category, category_id)
    if not obj:
        raise HTTPException(404, "category not found")
    if payload.type not in ("income", "expense"):
        raise HTTPException(400, "type must be income or expense")
    obj.name = payload.name
    obj.type = payload.type
    obj.icon = payload.icon
    db.commit()
    db.refresh(obj)
    return obj
