"""
认证相关API路由（适配pydantic 2.x，使用pyjwt）
"""
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from app.models.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, AuthResponse, RefreshTokenRequest
from app.services.auth_service import AuthService
from app.db.database import SessionLocal, get_db
from app.utils.response import ResponseUtil
import jwt
from app.core.config import settings
from datetime import datetime, timedelta, timezone

router = APIRouter(
    prefix="/auth",
    tags=["认证"],
    responses={404: {"description": "未找到"}}
)

@router.post("/register", response_model=AuthResponse, summary="用户注册", response_description="注册成功返回用户信息和令牌")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    用户注册接口
    """
    user = AuthService.register(db, data)
    tokens = AuthService.create_tokens(user)
    # 显式组装响应字段，类型转换
    resp_data = {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "nickname": user.nickname,
        "phone": user.phone,
        "avatar_url": user.avatar_url,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "is_admin": user.is_admin,
        "timezone": user.timezone,
        "language": user.language,
        "currency": user.currency,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "email_verified_at": user.email_verified_at.isoformat() if user.email_verified_at else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        **tokens
    }
    return ResponseUtil.success(
        data=resp_data,
        model=AuthResponse
    )

@router.post("/login/username", response_model=AuthResponse, summary="用户名登录", response_description="登录成功返回用户信息和令牌")
def login_username(
    data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户名密码登录接口
    """
    user = AuthService.authenticate(db, data)
    tokens = AuthService.create_tokens(user)
    resp_data = {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "nickname": user.nickname,
        "phone": user.phone,
        "avatar_url": user.avatar_url,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "is_admin": user.is_admin,
        "timezone": user.timezone,
        "language": user.language,
        "currency": user.currency,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "email_verified_at": user.email_verified_at.isoformat() if user.email_verified_at else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        **tokens
    }
    return ResponseUtil.success(
        data=resp_data,
        model=AuthResponse
    )

@router.post("/refresh-token", response_model=TokenResponse, summary="刷新令牌", response_description="刷新访问令牌")
def refresh_token(
    data: RefreshTokenRequest
):
    """
    刷新JWT访问令牌接口
    """
    try:
        payload = jwt.decode(data.refresh_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise jwt.InvalidTokenError
        user_id = payload["sub"]
        access_payload = {
            "sub": user_id,
            "exp": datetime.now(timezone(timedelta(hours=8))) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.now(timezone(timedelta(hours=8)))
        }
        access_token = jwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return ResponseUtil.success(
            data={
                "access_token": access_token,
                "refresh_token": data.refresh_token,
                "token_type": "bearer"
            },
            model=TokenResponse
        )
    except jwt.ExpiredSignatureError:
        return ResponseUtil.error(message="刷新令牌已过期", code=401)
    except jwt.InvalidTokenError:
        return ResponseUtil.error(message="无效的刷新令牌", code=401) 