from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.security import verify_password, create_token, hash_password, decode_token

router = APIRouter(prefix="/api/auth", tags=["auth"])

bearer = HTTPBearer(auto_error=False)


def require_auth(creds: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    if not creds or not creds.credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "需要登录后才能操作")
    username = decode_token(creds.credentials)
    if not username:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "登录已失效，请重新登录")
    return username


class LoginIn(BaseModel):
    username: str
    password: str


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=LoginOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户名或密码错误")
    return {"access_token": create_token(user.username)}


@router.get("/status")
def auth_status(db: Session = Depends(get_db)):
    return {"initialized": db.query(models.User).count() > 0}


@router.post("/setup", response_model=LoginOut)
def setup(payload: LoginIn, db: Session = Depends(get_db)):
    if db.query(models.User).count() > 0:
        raise HTTPException(400, "系统已初始化，请直接登录")
    username = payload.username.strip()
    if not username or not payload.password:
        raise HTTPException(400, "用户名和密码不能为空")
    if len(payload.password) < 6:
        raise HTTPException(400, "密码至少 6 位")
    user = models.User(username=username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"access_token": create_token(user.username)}


@router.get("/me")
def me(username: str = Depends(require_auth)):
    return {"username": username}
