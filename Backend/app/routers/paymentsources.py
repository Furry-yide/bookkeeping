from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/payment-sources", tags=["payment-sources"])


@router.get("", response_model=list[schemas.PaymentSourceOut])
def list_sources(db: Session = Depends(get_db)):
    return db.query(models.PaymentSource).all()


@router.post("", response_model=schemas.PaymentSourceOut)
def create_source(payload: schemas.PaymentSourceCreate, db: Session = Depends(get_db)):
    obj = models.PaymentSource(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.PaymentSource, source_id)
    if not obj:
        raise HTTPException(404, "payment source not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
