"""
认证相关依赖注入
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from jose import JWTError, jwt, ExpiredSignatureError

from app.db.database import get_db
from app.models.database.user import User
from app.core.config import settings
from app.core.exceptions.custom import AuthenticationError, AuthorizationError
from app.core.logging.logger import app_logger as logger

# JWT安全方案 - 自动模式会在没有Authorization头时抛出403
# 我们使用非自动模式来自己处理认证逻辑
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前认证用户
    
    Args:
        credentials: JWT认证凭据
        db: 数据库会话
        
    Returns:
        User: 当前用户对象
        
    Raises:
        AuthenticationError: 认证失败
    """
    try:
        # 检查是否提供了认证头
        if credentials is None:
            logger.warning("缺少认证头")
            raise AuthenticationError("需要认证")
        
        if not credentials.credentials:
            logger.warning("认证令牌为空")
            raise AuthenticationError("无效的认证令牌")
        # 解码JWT令牌
        payload = jwt.decode(
            credentials.credentials, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        
        if user_id is None or username is None:
            logger.warning(f"JWT令牌缺少必要字段: user_id={user_id}, username={username}")
            raise AuthenticationError("无效的认证令牌")
            
    except ExpiredSignatureError:
        logger.warning("JWT令牌已过期")
        raise AuthenticationError("认证令牌已过期")
    except JWTError as e:
        logger.warning(f"JWT解码失败: {str(e)}")
        raise AuthenticationError("无效的认证令牌")
    
    # 查询用户
    user = db.query(User).filter(User.id == UUID(user_id)).first()
    if user is None:
        logger.warning(f"用户不存在: user_id={user_id}")
        raise AuthenticationError("用户不存在")
    
    if not user.is_active:
        logger.warning(f"用户已禁用: user_id={user_id}")
        raise AuthenticationError("用户已禁用")
    
    logger.info(f"用户认证成功: user_id={user_id}, username={username}")
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前管理员用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        User: 管理员用户对象
        
    Raises:
        AuthorizationError: 权限不足
    """
    if not current_user.is_admin:
        logger.warning(f"非管理员用户尝试访问管理员接口: user_id={current_user.id}")
        raise AuthorizationError("需要管理员权限")
    
    logger.info(f"管理员权限验证成功: user_id={current_user.id}")
    return current_user


async def require_user_or_admin(
    target_user_id: UUID,
    current_user: User = Depends(get_current_user)
) -> User:
    """
    要求是目标用户本人或管理员
    
    Args:
        target_user_id: 目标用户ID
        current_user: 当前用户
        
    Returns:
        User: 验证通过的用户对象
        
    Raises:
        AuthorizationError: 权限不足
    """
    if current_user.id != target_user_id and not current_user.is_admin:
        logger.warning(f"权限检查失败: current_user_id={current_user.id}, target_user_id={target_user_id}")
        raise AuthorizationError("只能访问自己的资源或需要管理员权限")
    
    logger.info(f"权限验证成功: current_user_id={current_user.id}, target_user_id={target_user_id}")
    return current_user


async def require_resource_owner(
    resource_user_id: UUID,
    current_user: User = Depends(get_current_user)
) -> User:
    """
    要求资源所有者权限
    
    Args:
        resource_user_id: 资源所属用户ID
        current_user: 当前用户
        
    Returns:
        User: 验证通过的用户对象
        
    Raises:
        AuthorizationError: 权限不足
    """
    if current_user.id != resource_user_id:
        logger.warning(f"资源权限检查失败: current_user_id={current_user.id}, resource_user_id={resource_user_id}")
        raise AuthorizationError("只能访问自己的资源")
    
    logger.info(f"资源权限验证成功: current_user_id={current_user.id}")
    return current_user


# 可选认证（允许未认证用户）
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    可选的用户认证（允许未认证）
    
    Args:
        credentials: JWT认证凭据（可选）
        db: 数据库会话
        
    Returns:
        Optional[User]: 用户对象或None
    """
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except AuthenticationError:
        return None 