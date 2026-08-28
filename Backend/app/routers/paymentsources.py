from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.routers.auth import require_auth

router = APIRouter(prefix="/api/payment-sources", tags=["payment-sources"])


@router.get("", response_model=list[schemas.PaymentSourceOut])
def list_sources(db: Session = Depends(get_db)):
    return db.query(models.PaymentSource).all()


@router.post("", response_model=schemas.PaymentSourceOut)
def create_source(payload: schemas.PaymentSourceCreate, db: Session = Depends(get_db), _auth: str = Depends(require_auth)):
    obj = models.PaymentSource(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db), _auth: str = Depends(require_auth)):
    obj = db.get(models.PaymentSource, source_id)
    if not obj:
        raise HTTPException(404, "payment source not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}


@router.put("/{source_id}", response_model=schemas.PaymentSourceOut)
def update_source(source_id: int, payload: schemas.PaymentSourceCreate, db: Session = Depends(get_db), _auth: str = Depends(require_auth)):
    obj = db.get(models.PaymentSource, source_id)
    if not obj:
        raise HTTPException(404, "payment source not found")
    obj.name = payload.name
    obj.icon = payload.icon
    db.commit()
    db.refresh(obj)
    return obj
