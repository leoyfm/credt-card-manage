"""
用户管理路由

包含用户管理相关的API接口，如用户列表、用户详情、用户状态管理等。
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from models.users import (
    UserProfile,
    UserUpdateRequest,
    UserStatsInfo,
    LoginLogInfo,
    WechatBindingInfo
)
from models.response import ApiResponse, ApiPagedResponse
from routers.auth import get_current_user
from services.users_service import UsersService
from utils.response import ResponseUtil

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/users", tags=["用户管理"])

# 导入数据库依赖
from database import get_db


@router.get(
    "/",
    response_model=ApiPagedResponse[UserProfile],
    summary="获取用户列表",
    response_description="返回分页的用户列表"
)
async def get_users_list(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    keyword: str = Query("", description="搜索关键词，支持用户名、邮箱、昵称模糊搜索"),
    is_active: Optional[bool] = Query(None, description="筛选激活状态用户"),
    is_verified: Optional[bool] = Query(None, description="筛选已验证用户"),
    is_admin: Optional[bool] = Query(None, description="筛选管理员用户"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户列表接口
    
    支持分页和多条件筛选：
    - 支持按用户名、邮箱、昵称进行模糊搜索
    - 支持按激活状态、验证状态、管理员状态筛选
    - 支持分页查询
    
    注意：只有管理员才能查看所有用户列表
    """
    try:
        # 检查权限：只有管理员才能查看用户列表
        if not current_user.is_admin:
            return ResponseUtil.error(
                message="权限不足，只有管理员才能查看用户列表",
                code=403
            )
        
        users_service = UsersService(db)
        users, total = users_service.get_users_list(
            page=page,
            page_size=page_size,
            keyword=keyword,
            is_active=is_active,
            is_verified=is_verified,
            is_admin=is_admin
        )
        
        logger.info(f"管理员 {current_user.username} 查看用户列表")
        return ResponseUtil.paginated(
            items=users,
            total=total,
            page=page,
            page_size=page_size,
            message="获取用户列表成功"
        )
        
    except Exception as e:
        logger.error(f"获取用户列表异常 - {str(e)}")
        return ResponseUtil.error(message="获取用户列表失败，请稍后重试")


@router.get(
    "/{user_id}",
    response_model=ApiResponse[UserProfile],
    summary="获取用户详情",
    response_description="返回指定用户的详细信息"
)
async def get_user_detail(
    user_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户详情接口
    
    获取指定用户的详细信息。
    - 普通用户只能查看自己的详情
    - 管理员可以查看任意用户的详情
    """
    try:
        # 权限检查：只能查看自己的信息，或者管理员可以查看任意用户
        if current_user.id != user_id and not current_user.is_admin:
            return ResponseUtil.error(
                message="权限不足，只能查看自己的用户信息",
                code=403
            )
        
        users_service = UsersService(db)
        user = users_service.get_user_by_id(user_id)
        
        if not user:
            return ResponseUtil.not_found(message="用户不存在")
        
        logger.info(f"用户 {current_user.username} 查看用户详情 - target_user_id: {user_id}")
        return ResponseUtil.success(
            data=user,
            message="获取用户详情成功"
        )
        
    except Exception as e:
        logger.error(f"获取用户详情异常 - {str(e)}")
        return ResponseUtil.error(message="获取用户详情失败，请稍后重试")


@router.put(
    "/{user_id}/status",
    response_model=ApiResponse[UserProfile],
    summary="更新用户状态",
    response_description="返回更新后的用户信息"
)
async def update_user_status(
    user_id: UUID,
    is_active: bool = Query(..., description="是否激活"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户状态接口
    
    管理员可以激活或禁用用户账户。
    - 禁用用户后，用户将无法登录
    - 激活用户后，用户可以正常登录
    
    注意：只有管理员才能修改用户状态
    """
    try:
        # 检查权限：只有管理员才能修改用户状态
        if not current_user.is_admin:
            return ResponseUtil.error(
                message="权限不足，只有管理员才能修改用户状态",
                code=403
            )
        
        # 不能修改自己的状态
        if current_user.id == user_id:
            return ResponseUtil.error(
                message="不能修改自己的账户状态",
                code=400
            )
        
        users_service = UsersService(db)
        user = users_service.update_user_status(user_id, is_active)
        
        if not user:
            return ResponseUtil.not_found(message="用户不存在")
        
        status_text = "激活" if is_active else "禁用"
        logger.info(f"管理员 {current_user.username} {status_text}用户 - target_user_id: {user_id}")
        return ResponseUtil.success(
            data=user,
            message=f"用户状态更新成功，已{status_text}该用户"
        )
        
    except Exception as e:
        logger.error(f"更新用户状态异常 - {str(e)}")
        return ResponseUtil.error(message="更新用户状态失败，请稍后重试")


@router.put(
    "/{user_id}/admin",
    response_model=ApiResponse[UserProfile],
    summary="设置管理员权限",
    response_description="返回更新后的用户信息"
)
async def update_user_admin_status(
    user_id: UUID,
    is_admin: bool = Query(..., description="是否为管理员"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    设置用户管理员权限接口
    
    超级管理员可以设置或取消其他用户的管理员权限。
    
    注意：只有超级管理员才能修改管理员权限
    """
    try:
        # 检查权限：只有管理员才能修改管理员权限
        if not current_user.is_admin:
            return ResponseUtil.error(
                message="权限不足，只有管理员才能修改管理员权限",
                code=403
            )
        
        # 不能修改自己的管理员权限
        if current_user.id == user_id:
            return ResponseUtil.error(
                message="不能修改自己的管理员权限",
                code=400
            )
        
        users_service = UsersService(db)
        user = users_service.update_user_admin_status(user_id, is_admin)
        
        if not user:
            return ResponseUtil.not_found(message="用户不存在")
        
        permission_text = "设置" if is_admin else "取消"
        logger.info(f"管理员 {current_user.username} {permission_text}管理员权限 - target_user_id: {user_id}")
        return ResponseUtil.success(
            data=user,
            message=f"管理员权限更新成功，已{permission_text}该用户的管理员权限"
        )
        
    except Exception as e:
        logger.error(f"更新管理员权限异常 - {str(e)}")
        return ResponseUtil.error(message="更新管理员权限失败，请稍后重试")


@router.delete(
    "/{user_id}",
    response_model=ApiResponse[dict],
    summary="删除用户",
    response_description="返回删除结果"
)
async def delete_user(
    user_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除用户接口
    
    彻底删除用户账户及相关数据。
    - 只有管理员才能删除用户
    - 不能删除自己的账户
    - 删除操作不可逆，请谨慎使用
    
    注意：这是危险操作，会删除用户的所有相关数据
    """
    try:
        # 检查权限：只有管理员才能删除用户
        if not current_user.is_admin:
            return ResponseUtil.error(
                message="权限不足，只有管理员才能删除用户",
                code=403
            )
        
        # 不能删除自己的账户
        if current_user.id == user_id:
            return ResponseUtil.error(
                message="不能删除自己的账户",
                code=400
            )
        
        users_service = UsersService(db)
        success = users_service.delete_user(user_id)
        
        if not success:
            return ResponseUtil.not_found(message="用户不存在")
        
        logger.warning(f"管理员 {current_user.username} 删除用户 - target_user_id: {user_id}")
        return ResponseUtil.success(
            data={"deleted": True},
            message="用户删除成功"
        )
        
    except Exception as e:
        logger.error(f"删除用户异常 - {str(e)}")
        return ResponseUtil.error(message="删除用户失败，请稍后重试")


@router.get(
    "/{user_id}/login-logs",
    response_model=ApiPagedResponse[LoginLogInfo],
    summary="获取用户登录日志",
    response_description="返回用户的登录历史记录"
)
async def get_user_login_logs(
    user_id: UUID,
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户登录日志接口
    
    查看用户的登录历史记录，包括登录时间、IP地址、设备信息等。
    - 普通用户只能查看自己的登录日志
    - 管理员可以查看任意用户的登录日志
    """
    try:
        # 权限检查：只能查看自己的登录日志，或者管理员可以查看任意用户
        if current_user.id != user_id and not current_user.is_admin:
            return ResponseUtil.error(
                message="权限不足，只能查看自己的登录日志",
                code=403
            )
        
        users_service = UsersService(db)
        logs, total = users_service.get_user_login_logs(user_id, page, page_size)
        
        logger.info(f"用户 {current_user.username} 查看登录日志 - target_user_id: {user_id}")
        return ResponseUtil.paginated(
            items=logs,
            total=total,
            page=page,
            page_size=page_size,
            message="获取登录日志成功"
        )
        
    except Exception as e:
        logger.error(f"获取登录日志异常 - {str(e)}")
        return ResponseUtil.error(message="获取登录日志失败，请稍后重试")


@router.get(
    "/{user_id}/wechat-binding",
    response_model=ApiResponse[WechatBindingInfo],
    summary="获取微信绑定信息",
    response_description="返回用户的微信绑定信息"
)
async def get_user_wechat_binding(
    user_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户微信绑定信息接口
    
    查看用户的微信绑定状态和信息。
    - 普通用户只能查看自己的微信绑定信息
    - 管理员可以查看任意用户的微信绑定信息
    """
    try:
        # 权限检查：只能查看自己的微信绑定信息，或者管理员可以查看任意用户
        if current_user.id != user_id and not current_user.is_admin:
            return ResponseUtil.error(
                message="权限不足，只能查看自己的微信绑定信息",
                code=403
            )
        
        users_service = UsersService(db)
        wechat_binding = users_service.get_user_wechat_binding(user_id)
        
        if not wechat_binding:
            return ResponseUtil.not_found(message="该用户未绑定微信")
        
        logger.info(f"用户 {current_user.username} 查看微信绑定信息 - target_user_id: {user_id}")
        return ResponseUtil.success(
            data=wechat_binding,
            message="获取微信绑定信息成功"
        )
        
    except Exception as e:
        logger.error(f"获取微信绑定信息异常 - {str(e)}")
        return ResponseUtil.error(message="获取微信绑定信息失败，请稍后重试")


@router.get(
    "/statistics/overview",
    response_model=ApiResponse[UserStatsInfo],
    summary="获取用户统计信息",
    response_description="返回用户相关的统计数据"
)
async def get_users_statistics(
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户统计信息接口
    
    返回用户相关的统计数据，包括：
    - 总用户数
    - 活跃用户数
    - 已验证用户数
    - 今日新增用户数
    - 今日登录次数
    
    注意：只有管理员才能查看用户统计信息
    """
    try:
        # 检查权限：只有管理员才能查看统计信息
        if not current_user.is_admin:
            return ResponseUtil.error(
                message="权限不足，只有管理员才能查看统计信息",
                code=403
            )
        
        users_service = UsersService(db)
        stats = users_service.get_users_statistics()
        
        logger.info(f"管理员 {current_user.username} 查看用户统计信息")
        return ResponseUtil.success(
            data=stats,
            message="获取用户统计信息成功"
        )
        
    except Exception as e:
        logger.error(f"获取用户统计信息异常 - {str(e)}")
        return ResponseUtil.error(message="获取用户统计信息失败，请稍后重试") 