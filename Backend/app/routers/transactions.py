from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime

from app.database import get_db
from app import models, schemas
from app.routers.auth import require_auth

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.get("", response_model=list[schemas.TransactionOut])
def list_transactions(
    month: str | None = Query(None, description="YYYY-MM"),
    day: str | None = Query(None, description="YYYY-MM-DD"),
    type: str | None = None,
    category_id: int | None = None,
    payment_source_id: int | None = None,
    db: Session = Depends(get_db),
):
    q = db.query(models.Transaction)
    if day:
        q = q.filter(func.strftime("%Y-%m-%d", models.Transaction.occurred_at) == day)
    elif month:
        q = q.filter(func.strftime("%Y-%m", models.Transaction.occurred_at) == month)
    if type:
        q = q.filter(models.Transaction.type == type)
    if category_id:
        q = q.filter(models.Transaction.category_id == category_id)
    if payment_source_id:
        q = q.filter(models.Transaction.payment_source_id == payment_source_id)
    return q.order_by(desc(models.Transaction.occurred_at)).all()


@router.post("", response_model=schemas.TransactionOut)
def create_transaction(payload: schemas.TransactionCreate, db: Session = Depends(get_db), _auth: str = Depends(require_auth)):
    if payload.type == "transfer":
        if not payload.payment_source_id or not payload.transfer_to_id:
            raise HTTPException(400, "转账需选择转出与转入支付源")
        if payload.payment_source_id == payload.transfer_to_id:
            raise HTTPException(400, "转出与转入支付源不能相同")
        if payload.amount <= 0:
            raise HTTPException(400, "转账金额必须大于 0")
    else:
        if not payload.category_id:
            raise HTTPException(400, "category not found")
        db.get(models.Category, payload.category_id)

    data = payload.model_dump()
    if data.get("occurred_at") is None:
        data["occurred_at"] = datetime.now()
    obj = models.Transaction(**data)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/{tx_id}", response_model=schemas.TransactionOut)
def update_transaction(tx_id: int, payload: schemas.TransactionCreate, db: Session = Depends(get_db), _auth: str = Depends(require_auth)):
    obj = db.get(models.Transaction, tx_id)
    if not obj:
        raise HTTPException(404, "transaction not found")
    if payload.type == "transfer":
        if not payload.payment_source_id or not payload.transfer_to_id:
            raise HTTPException(400, "转账需选择转出与转入支付源")
        if payload.payment_source_id == payload.transfer_to_id:
            raise HTTPException(400, "转出与转入支付源不能相同")
        if payload.amount <= 0:
            raise HTTPException(400, "转账金额必须大于 0")
        payload.category_id = None
    else:
        if not payload.category_id:
            raise HTTPException(400, "category not found")
        db.get(models.Category, payload.category_id)
        payload.transfer_to_id = None

    data = payload.model_dump()
    if data.get("occurred_at") is None:
        data["occurred_at"] = datetime.now()
    for k, v in data.items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{tx_id}")
def delete_transaction(tx_id: int, db: Session = Depends(get_db), _auth: str = Depends(require_auth)):
    obj = db.get(models.Transaction, tx_id)
    if not obj:
        raise HTTPException(404, "transaction not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
