"""认证相关依赖注入"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.logging.logger import get_logger

logger = get_logger("auth.dependencies")
security = HTTPBearer()

# 临时用户配置，稍后会连接真实的服务
class MockUser:
    def __init__(self, user_id: str, username: str):
        self.user_id = user_id
        self.username = username
        self.is_active = True

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取当前登录用户"""
    
    token = credentials.credentials
    
    # 临时实现 - 稍后会连接真实的认证服务
    logger.info("验证访问令牌", token=token[:20] + "...")
    
    # 简单的令牌验证逻辑（后续会替换为真实的JWT验证）
    if not token or token == "invalid":
        logger.warning("无效的访问令牌")
        raise AuthenticationError("令牌无效或已过期")
    
    # 返回模拟用户（后续会连接真实的用户服务）
    return MockUser("user-123", "test_user")

def get_current_admin_user(
    current_user = Depends(get_current_user)
):
    """获取当前管理员用户"""
    
    # 临时实现 - 检查管理员权限
    if not hasattr(current_user, 'is_admin') or not getattr(current_user, 'is_admin', False):
        logger.warning("非管理员用户尝试访问管理接口", user_id=current_user.user_id)
        raise AuthorizationError("需要管理员权限")
    
    return current_user

def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """获取可选的当前用户（不强制要求登录）"""
    
    if not credentials:
        return None
        
    try:
        return get_current_user(credentials, db)
    except AuthenticationError:
        return None 