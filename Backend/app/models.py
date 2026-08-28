from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    type = Column(String(10), nullable=False)  # income / expense
    icon = Column(String(20), default="💰")

    transactions = relationship("Transaction", back_populates="category")


class PaymentSource(Base):
    __tablename__ = "payment_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    icon = Column(String(20), default="💳")

    transactions = relationship("Transaction", back_populates="payment_source")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(200), nullable=False)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(String(10), nullable=False)  # income / expense
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    payment_source_id = Column(Integer, ForeignKey("payment_sources.id"), nullable=True)
    note = Column(Text, default="")
    occurred_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    category = relationship("Category", back_populates="transactions")
    payment_source = relationship("PaymentSource", back_populates="transactions")


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String(7), nullable=False, unique=True)  # YYYY-MM
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    limit_amount = Column(Float, nullable=False)
    note = Column(Text, default="")
