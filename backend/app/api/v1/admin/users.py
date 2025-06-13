"""
管理员用户管理 API
"""
from fastapi import APIRouter, Depends, Query, Path
from typing import Optional, Union
from uuid import UUID

from app.api.dependencies.auth import get_current_admin_user
from app.db.database import get_db
from app.models.database.user import User
from app.models.schemas.admin import (
    UserStatusUpdateRequest, UserPermissionsUpdateRequest, UserDeletionRequest,
    AdminUserListResponse, AdminUserDetailsResponse, AdminLoginLogsResponse,
    AdminUserStatisticsResponse
)
from app.utils.response import ApiResponse, ApiPagedResponse
from app.services.admin_service import AdminUserService
from app.utils.response import ResponseUtil

router = APIRouter(prefix="/users", tags=["管理员-用户管理"])


@router.get(
    "/list",
    response_model=ApiPagedResponse,
    summary="获取用户列表",
    description="管理员获取系统用户列表，支持搜索和筛选"
)
async def get_users_list(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    search: Optional[str] = Query("", description="搜索关键词（用户名、邮箱、昵称）"),
    is_active: Optional[bool] = Query(None, description="过滤用户状态：true=激活，false=禁用"),
    is_admin: Optional[bool] = Query(None, description="过滤管理员：true=管理员，false=普通用户"),
    is_verified: Optional[bool] = Query(None, description="过滤验证状态：true=已验证，false=未验证"),
    current_admin: User = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """获取用户列表（管理员权限）"""
    search_keyword = search.strip() if search else None
    
    admin_service = AdminUserService(db)
    users, pagination_info = admin_service.get_users_list(
        page=page,
        page_size=page_size,
        search=search_keyword,
        is_active=is_active,
        is_admin=is_admin,
        is_verified=is_verified
    )
    
    return ResponseUtil.paginated(
        items=users,
        total=pagination_info.total,
        page=page,
        page_size=page_size,
        message="用户列表查询成功"
    )


@router.get(
    "/{user_id}/details",
    response_model=ApiResponse,
    summary="获取用户详情",
    description="管理员获取指定用户的详细信息"
)
async def get_user_details(
    user_id: UUID = Path(..., description="用户ID"),
    current_admin: User = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """获取用户详情（管理员权限）"""
    admin_service = AdminUserService(db)
    user_details = admin_service.get_user_details(user_id)
    
    return ResponseUtil.success(
        data=user_details,
        message="用户详情查询成功"
    )


@router.put(
    "/{user_id}/status",
    response_model=ApiResponse,
    summary="更新用户状态",
    description="管理员更新用户的激活状态"
)
async def update_user_status(
    user_id: UUID = Path(..., description="用户ID"),
    status_update: UserStatusUpdateRequest = ...,
    current_admin: User = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """更新用户状态（管理员权限）"""
    admin_service = AdminUserService(db)
    updated_user = admin_service.update_user_status(
        user_id=user_id,
        status_update=status_update,
        admin_user_id=current_admin.id
    )
    
    return ResponseUtil.success(
        data=updated_user,
        message=f"用户状态已更新为{'激活' if status_update.is_active else '禁用'}"
    )


@router.put(
    "/{user_id}/permissions",
    response_model=ApiResponse,
    summary="更新用户权限",
    description="管理员更新用户的权限（管理员权限、验证状态）"
)
async def update_user_permissions(
    user_id: UUID = Path(..., description="用户ID"),
    permissions_update: UserPermissionsUpdateRequest = ...,
    current_admin: User = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """更新用户权限（管理员权限）"""
    admin_service = AdminUserService(db)
    updated_user = admin_service.update_user_permissions(
        user_id=user_id,
        permissions_update=permissions_update,
        admin_user_id=current_admin.id
    )
    
    return ResponseUtil.success(
        data=updated_user,
        message="用户权限已更新"
    )


@router.get(
    "/{user_id}/login-logs",
    response_model=ApiPagedResponse,
    summary="获取用户登录日志",
    description="管理员获取指定用户的登录日志"
)
async def get_user_login_logs(
    user_id: UUID = Path(..., description="用户ID"),
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    current_admin: User = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """获取用户登录日志（管理员权限）"""
    admin_service = AdminUserService(db)
    login_logs, pagination_info = admin_service.get_user_login_logs(
        user_id=user_id,
        page=page,
        page_size=page_size
    )
    
    return ResponseUtil.paginated(
        items=login_logs,
        total=pagination_info['total'],
        page=page,
        page_size=page_size,
        message="登录日志查询成功"
    )


@router.delete(
    "/{user_id}/delete",
    response_model=ApiResponse,
    summary="删除用户",
    description="管理员删除指定用户（谨慎操作）"
)
async def delete_user(
    user_id: UUID = Path(..., description="用户ID"),
    deletion_request: UserDeletionRequest = ...,
    current_admin: User = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """删除用户（管理员权限）"""
    admin_service = AdminUserService(db)
    admin_service.delete_user(
        user_id=user_id,
        deletion_request=deletion_request,
        admin_user_id=current_admin.id
    )
    
    return ResponseUtil.deleted(message="用户已成功删除")


@router.get(
    "/statistics",
    response_model=ApiResponse,
    summary="获取用户统计",
    description="管理员获取系统用户统计信息"
)
async def get_user_statistics(
    current_admin: User = Depends(get_current_admin_user),
    db = Depends(get_db)
):
    """获取用户统计信息（管理员权限）"""
    admin_service = AdminUserService(db)
    statistics = admin_service.get_user_statistics()
    
    return ResponseUtil.success(
        data=statistics,
        message="用户统计查询成功"
    ) 