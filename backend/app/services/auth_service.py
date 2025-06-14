"""
认证服务模块（适配pydantic 2.x，使用pyjwt实现JWT）
"""
from sqlalchemy.orm import Session
from app.models.database.user import User
from app.models.schemas.auth import RegisterRequest, LoginRequest
from app.core.config import settings
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
import uuid
from datetime import datetime, timedelta, timezone
import jwt
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """
    认证服务，包含注册、登录、密码加密、JWT生成等
    """
    @staticmethod
    def get_password_hash(password: str) -> str:
        """生成密码哈希"""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """校验密码"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def register(db: Session, data: RegisterRequest) -> User:
        """用户注册"""
        if db.query(User).filter(User.username == data.username).first():
            from app.core.logging import app_logger
            app_logger.warning(f"注册失败: 用户名已存在 {data.username}")
            raise HTTPException(status_code=400, detail="用户名已存在")
        if db.query(User).filter(User.email == data.email).first():
            from app.core.logging import app_logger
            app_logger.warning(f"注册失败: 邮箱已存在 {data.email}")
            raise HTTPException(status_code=400, detail="邮箱已存在")
        user = User(
            id=uuid.uuid4(),
            username=data.username,
            email=data.email,
            password_hash=AuthService.get_password_hash(data.password),
            nickname=data.nickname,
            is_active=True,
            is_admin=False,
            is_verified=False
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        from app.core.logging import app_logger
        app_logger.info(f"用户注册成功: {user.username} ({user.id})")
        return user

    @staticmethod
    def authenticate(db: Session, data: LoginRequest) -> User:
        """用户名密码登录"""
        user = db.query(User).filter(User.username == data.username).first()
        if not user or not AuthService.verify_password(data.password, user.password_hash):
            from app.core.logging import app_logger
            app_logger.warning(f"登录失败: 用户名或密码错误 {data.username}")
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        if not user.is_active:
            from app.core.logging import app_logger
            app_logger.warning(f"登录失败: 账号被禁用 {data.username}")
            raise HTTPException(status_code=403, detail="账号已被禁用")
        from app.core.logging import app_logger
        app_logger.info(f"用户登录成功: {user.username} ({user.id})")
        return user

    @staticmethod
    def create_tokens(user: User) -> dict:
        """生成JWT访问令牌和刷新令牌"""
        now = datetime.now( timezone(timedelta(hours=8)))
        access_payload = {
            "sub": str(user.id),
            "username": user.username,
            "role": "admin" if user.is_admin else "user",
            "exp": now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": now
        }
        refresh_payload = {
            "sub": str(user.id),
            "type": "refresh",
            "exp": now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
            "iat": now
        }
        access_token = jwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def decode_token(token: str, verify_exp: bool = True) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": verify_exp})
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="令牌已过期")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="无效令牌")

    @staticmethod
    def get_current_user(request: Request, db: Session = Depends()):
        """FastAPI依赖：获取当前用户"""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="缺少认证信息")
        token = auth_header.split(" ", 1)[1]
        payload = AuthService.decode_token(token)
        user = db.query(User).filter(User.id == payload["sub"]).first()
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        return user 