"""
依赖注入模块

提供API层的所有依赖注入函数，包括认证、权限控制和服务层依赖。
"""

from .auth import (
    get_current_user,
    require_admin,
    require_user_or_admin,
    require_resource_owner,
    get_optional_user
)

from .services import (
    get_auth_service,
    get_users_service,
    get_cards_service,
    get_transactions_service,
    get_annual_fee_service,
    get_reminder_service,
    get_recommendation_service,
    get_statistics_service
)

__all__ = [
    # 认证依赖
    "get_current_user",
    "require_admin", 
    "require_user_or_admin",
    "require_resource_owner",
    "get_optional_user",
    
    # 服务依赖
    "get_auth_service",
    "get_users_service",
    "get_cards_service", 
    "get_transactions_service",
    "get_annual_fee_service",
    "get_reminder_service",
    "get_recommendation_service",
    "get_statistics_service"
] 