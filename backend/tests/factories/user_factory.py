import uuid
from typing import Dict, Any, Optional
import random


def build_user(**kwargs) -> Dict[str, Any]:
    """构建用户测试数据
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 用户数据字典
    """
    username = kwargs.get("username") or f"user_{uuid.uuid4().hex[:8]}"
    email = kwargs.get("email") or f"{username}@example.com"
    password = kwargs.get("password") or "TestPass123456"
    
    return {
        "username": username,
        "email": email,
        "password": password,
        "nickname": kwargs.get("nickname", f"测试用户_{username[-4:]}"),
        "phone": kwargs.get("phone", f"138{random.randint(10000000, 99999999)}"),
        "timezone": kwargs.get("timezone", "Asia/Shanghai"),
        "language": kwargs.get("language", "zh-CN"),
        "currency": kwargs.get("currency", "CNY")
    }


def build_simple_user(**kwargs) -> Dict[str, Any]:
    """构建简单的用户数据（只包含必需字段）
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 简化的用户数据字典
    """
    username = kwargs.get("username") or f"user_{uuid.uuid4().hex[:8]}"
    
    return {
        "username": username,
        "email": kwargs.get("email", f"{username}@example.com"),
        "password": kwargs.get("password", "TestPass123456")
    }


def build_admin_user(**kwargs) -> Dict[str, Any]:
    """构建管理员用户数据
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 管理员用户数据字典
    """
    base_user = build_user(**kwargs)
    
    base_user.update({
        "username": kwargs.get("username", f"admin_{uuid.uuid4().hex[:8]}"),
        "email": kwargs.get("email", f"admin_{uuid.uuid4().hex[:8]}@example.com"),
        "nickname": kwargs.get("nickname", "测试管理员"),
        "is_admin": kwargs.get("is_admin", True)
    })
    
    return base_user


def build_verified_user(**kwargs) -> Dict[str, Any]:
    """构建已验证的用户数据
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 已验证用户数据字典
    """
    base_user = build_user(**kwargs)
    
    base_user.update({
        "is_verified": kwargs.get("is_verified", True),
        "is_active": kwargs.get("is_active", True)
    })
    
    return base_user


def build_inactive_user(**kwargs) -> Dict[str, Any]:
    """构建未激活的用户数据
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 未激活用户数据字典
    """
    base_user = build_user(**kwargs)
    
    base_user.update({
        "is_active": kwargs.get("is_active", False),
        "is_verified": kwargs.get("is_verified", False)
    })
    
    return base_user


def build_users_batch(count: int = 3, **kwargs) -> list[Dict[str, Any]]:
    """批量构建用户数据
    
    Args:
        count: 要生成的用户数量
        **kwargs: 可选的覆盖参数
        
    Returns:
        list[Dict[str, Any]]: 用户数据列表
    """
    users = []
    for i in range(count):
        user_kwargs = kwargs.copy()
        # 确保每个用户的用户名和邮箱不同
        if "username" not in user_kwargs:
            user_kwargs["username"] = f"user_{uuid.uuid4().hex[:8]}"
        if "email" not in user_kwargs:
            user_kwargs["email"] = f"{user_kwargs['username']}@example.com"
        users.append(build_user(**user_kwargs))
    
    return users


# 预定义的用户模板
USER_TEMPLATES = {
    "普通用户": {
        "nickname": "普通测试用户",
        "is_active": True,
        "is_verified": True,
        "is_admin": False
    },
    "管理员": {
        "nickname": "系统管理员",
        "is_active": True,
        "is_verified": True,
        "is_admin": True
    },
    "新注册用户": {
        "nickname": "新用户",
        "is_active": True,
        "is_verified": False,
        "is_admin": False
    },
    "禁用用户": {
        "nickname": "被禁用用户",
        "is_active": False,
        "is_verified": True,
        "is_admin": False
    }
}


def build_template_user(template_name: str, **kwargs) -> Dict[str, Any]:
    """根据模板构建用户数据
    
    Args:
        template_name: 模板名称
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 用户数据字典
        
    Raises:
        ValueError: 当模板不存在时
    """
    if template_name not in USER_TEMPLATES:
        raise ValueError(f"未知的用户模板: {template_name}，可用模板: {list(USER_TEMPLATES.keys())}")
    
    template = USER_TEMPLATES[template_name].copy()
    template.update(kwargs)
    
    return build_user(**template) 