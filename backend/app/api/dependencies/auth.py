"""认证相关依赖注入 - API v1"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.logging.logger import get_logger
from app.models.schemas.auth import UserProfile

# 导入认证服务
from services.auth_service import AuthService

logger = get_logger("auth.dependencies")
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserProfile:
    """
    获取当前登录用户 - API v1
    
    验证JWT令牌并返回用户信息：
    - 验证令牌有效性和过期时间
    - 检查用户是否存在且激活
    - 返回用户的完整资料信息
    
    抛出异常：
    - AuthenticationError: 令牌无效、过期或用户不存在
    - AuthorizationError: 用户被禁用
    """
    try:
        token = credentials.credentials
        logger.debug("验证JWT访问令牌", token=token[:20] + "...")
        
        # 使用认证服务验证令牌
        auth_service = AuthService(db)
        user_profile = auth_service.verify_access_token(token)
        
        if not user_profile:
            logger.warning("JWT令牌验证失败", token=token[:20] + "...")
            raise AuthenticationError("访问令牌无效或已过期，请重新登录")
        
        # 检查用户状态
        if not user_profile.is_active:
            logger.warning("已禁用用户尝试访问", user_id=user_profile.id, username=user_profile.username)
            raise AuthorizationError("账户已被禁用，请联系管理员")
        
        logger.debug("用户认证成功", user_id=user_profile.id, username=user_profile.username)
        return user_profile
        
    except AuthenticationError:
        raise
    except AuthorizationError:
        raise  
    except Exception as e:
        logger.error("用户认证异常", error=str(e), token=token[:20] + "..." if 'token' in locals() else "N/A")
        raise AuthenticationError("认证服务异常，请稍后重试")


def require_admin(
    current_user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """
    要求管理员权限 - API v1
    
    检查当前用户是否为管理员：
    - 用户必须已通过认证
    - 用户必须具有管理员权限
    - 用户必须处于激活状态
    
    抛出异常：
    - AuthorizationError: 用户不是管理员
    """
    if not current_user.is_admin:
        logger.warning("非管理员用户尝试访问管理接口", user_id=current_user.id, username=current_user.username)
        raise AuthorizationError("需要管理员权限才能访问此接口")
    
    logger.debug("管理员权限验证通过", user_id=current_user.id, username=current_user.username)
    return current_user


def require_user_or_admin(
    target_user_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """
    要求是目标用户本人或管理员 - API v1
    
    用于需要访问特定用户数据的接口：
    - 用户只能访问自己的数据
    - 管理员可以访问任何用户的数据
    
    参数：
    - target_user_id: 目标用户ID
    
    抛出异常：
    - AuthorizationError: 既不是目标用户本人也不是管理员
    """
    if str(current_user.id) != str(target_user_id) and not current_user.is_admin:
        logger.warning("用户尝试访问其他用户数据", 
                      current_user=current_user.id, 
                      target_user=target_user_id)
        raise AuthorizationError("只能访问自己的数据，或需要管理员权限")
    
    return current_user


def require_resource_owner(
    resource_user_id: str,
    current_user: UserProfile = Depends(get_current_user)
) -> UserProfile:
    """
    要求资源所有者权限 - API v1
    
    用于需要操作特定用户资源的接口：
    - 只有资源的所有者可以操作
    - 管理员不能直接操作用户的私人资源
    
    参数：
    - resource_user_id: 资源所属用户ID
    
    抛出异常：
    - AuthorizationError: 不是资源所有者
    """
    if str(current_user.id) != str(resource_user_id):
        logger.warning("用户尝试访问非自有资源", 
                      current_user=current_user.id, 
                      resource_owner=resource_user_id)
        raise AuthorizationError("只能操作自己的资源")
    
    return current_user


def get_optional_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserProfile:
    """
    获取可选的当前用户 - API v1
    
    用于可选认证的接口：
    - 如果提供有效令牌，返回用户信息
    - 如果没有令牌或令牌无效，返回None
    - 不会抛出认证异常
    """
    if not credentials:
        return None
        
    try:
        return get_current_user(credentials, db)
    except (AuthenticationError, AuthorizationError):
        logger.debug("可选用户认证失败，返回匿名访问")
        return None
    except Exception as e:
        logger.warning("可选用户认证异常", error=str(e))
        return None 