from datetime import datetime
from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str
    type: str  # income / expense
    icon: str = "💰"


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class PaymentSourceBase(BaseModel):
    name: str
    icon: str = "💳"


class PaymentSourceCreate(PaymentSourceBase):
    pass


class PaymentSourceOut(PaymentSourceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class TransactionBase(BaseModel):
    amount: float
    type: str  # income / expense
    category_id: int
    payment_source_id: int | None = None
    note: str = ""
    occurred_at: datetime | None = None


class TransactionCreate(TransactionBase):
    pass


class TransactionOut(TransactionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category: CategoryOut | None = None
    payment_source: PaymentSourceOut | None = None


class BudgetBase(BaseModel):
    month: str  # YYYY-MM
    category_id: int | None = None
    limit_amount: float
    note: str = ""


class BudgetCreate(BudgetBase):
    pass


class BudgetOut(BudgetBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class StatsSummary(BaseModel):
    month: str
    total_income: float
    total_expense: float
    balance: float
    by_category: list[dict]
