from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=list[schemas.TransactionOut])
def list_transactions(
    month: str | None = Query(None, description="YYYY-MM"),
    type: str | None = None,
    category_id: int | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Transaction)
    if month:
        q = q.filter(func.strftime("%Y-%m", models.Transaction.occurred_at) == month)
    if type:
        q = q.filter(models.Transaction.type == type)
    if category_id:
        q = q.filter(models.Transaction.category_id == category_id)
    return q.order_by(desc(models.Transaction.occurred_at)).all()


@router.post("", response_model=schemas.TransactionOut)
def create_transaction(payload: schemas.TransactionCreate, db: Session = Depends(get_db)):
    cat = db.get(models.Category, payload.category_id)
    if not cat:
        raise HTTPException(400, "category not found")
    data = payload.model_dump()
    if data.get("occurred_at") is None:
        data["occurred_at"] = datetime.utcnow()
    obj = models.Transaction(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{tx_id}")
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Transaction, tx_id)
    if not obj:
        raise HTTPException(404, "transaction not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
