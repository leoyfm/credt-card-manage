"""
管理员用户管理接口 - API v1

提供管理员管理系统用户的相关功能：
- 查看用户列表
- 查看用户详情
- 用户状态管理
- 权限管理
- 删除用户
- 用户统计分析

权限等级：Level 3 - 需要管理员认证，可以管理所有用户数据
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.api.dependencies.auth import require_admin, get_current_user
from app.db.connection import get_db
from app.models.schemas.auth import UserProfile
from app.models.schemas.admin import (
    AdminUserListResponse,
    AdminUserDetailResponse,
    AdminUserStatsResponse,
    UserStatusUpdateRequest,
    UserPermissionUpdateRequest,
    AdminUserOperationLog
)
from app.models.schemas.common import ApiResponse, ApiPagedResponse, SuccessMessage
from app.utils.response import ResponseUtil
from app.core.logging.logger import get_logger

# 导入原有服务
from services.users_service import UsersService
from services.auth_service import AuthService
from sqlalchemy.orm import Session

logger = get_logger("api.admin.users")

# 创建路由器 - 管理员用户管理
router = APIRouter(
    prefix="/users",
    tags=["管理员用户管理"],
    dependencies=[Depends(require_admin)],
    responses={
        401: {"description": "未授权 - 需要登录"},
        403: {"description": "权限不足 - 需要管理员权限"},
        404: {"description": "资源不存在"},
        500: {"description": "服务器内部错误"}
    }
)


@router.get(
    "/",
    response_model=ApiPagedResponse[AdminUserListResponse],
    summary="获取用户列表",
    response_description="返回系统用户列表（管理员视图）"
)
async def get_users_list(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    keyword: str = Query("", description="搜索关键词，支持用户名、邮箱、昵称模糊搜索"),
    is_active: Optional[bool] = Query(None, description="筛选激活状态用户"),
    is_verified: Optional[bool] = Query(None, description="筛选已验证用户"),
    is_admin: Optional[bool] = Query(None, description="筛选管理员用户"),
    sort_by: str = Query("created_at", description="排序字段：created_at, last_login_at, username"),
    sort_order: str = Query("desc", description="排序方向：asc, desc"),
    current_admin: UserProfile = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    管理员获取用户列表接口
    
    获取系统中所有用户的列表信息：
    - 支持多条件筛选和搜索
    - 支持多字段排序
    - 包含用户基础信息和统计数据
    - 用户隐私信息已脱敏处理
    """
    try:
        logger.info("管理员查看用户列表", 
                   admin_id=current_admin.id, 
                   admin_username=current_admin.username,
                   filters={"keyword": keyword, "is_active": is_active, "is_verified": is_verified, "is_admin": is_admin})
        
        users_service = UsersService(db)
        users, total = users_service.get_admin_users_list(
            page=page,
            page_size=page_size,
            keyword=keyword,
            is_active=is_active,
            is_verified=is_verified,
            is_admin=is_admin,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return ResponseUtil.paginated(
            items=users,
            total=total,
            page=page,
            page_size=page_size,
            message="获取用户列表成功"
        )
        
    except ValueError as e:
        logger.warning("用户列表查询参数错误", error=str(e), admin_id=current_admin.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("获取用户列表异常", error=str(e), admin_id=current_admin.id)
        return ResponseUtil.error("获取用户列表失败，请稍后重试")


@router.get(
    "/{user_id}",
    response_model=ApiResponse[AdminUserDetailResponse],
    summary="获取用户详情",
    response_description="返回指定用户的详细信息（管理员视图）"
)
async def get_user_detail(
    user_id: UUID,
    current_admin: UserProfile = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    管理员获取用户详情接口
    
    获取指定用户的详细信息：
    - 用户基础信息（隐私信息已脱敏）
    - 账户状态和设置
    - 详细统计信息
    - 活动记录和行为分析
    """
    try:
        logger.info("管理员查看用户详情", 
                   admin_id=current_admin.id, 
                   admin_username=current_admin.username,
                   target_user_id=user_id)
        
        users_service = UsersService(db)
        user_detail = users_service.get_admin_user_detail(user_id)
        
        if not user_detail:
            return ResponseUtil.not_found("用户不存在")
        
        return ResponseUtil.success(
            data=user_detail,
            message="获取用户详情成功"
        )
        
    except Exception as e:
        logger.error("获取用户详情异常", error=str(e), admin_id=current_admin.id, target_user_id=user_id)
        return ResponseUtil.error("获取用户详情失败，请稍后重试")


@router.put(
    "/{user_id}/status",
    response_model=ApiResponse[SuccessMessage],
    summary="更新用户状态",
    response_description="返回用户状态更新结果"
)
async def update_user_status(
    user_id: UUID,
    status_data: UserStatusUpdateRequest,
    request: Request,
    current_admin: UserProfile = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    管理员更新用户状态接口
    
    管理员可以激活或禁用用户账户：
    - 禁用用户后，用户将无法登录和使用系统
    - 激活用户后，用户可以正常使用系统
    - 必须提供状态变更原因
    - 操作将被记录到审计日志
    """
    try:
        # 防止管理员修改自己的状态
        if current_admin.id == user_id:
            return ResponseUtil.validation_error("不能修改自己的账户状态")
        
        logger.info("管理员更新用户状态", 
                   admin_id=current_admin.id, 
                   admin_username=current_admin.username,
                   target_user_id=user_id,
                   new_status=status_data.is_active,
                   reason=status_data.reason)
        
        users_service = UsersService(db)
        
        # 获取目标用户信息
        target_user = users_service.get_user_by_id(user_id)
        if not target_user:
            return ResponseUtil.not_found("用户不存在")
        
        # 记录操作前状态
        old_status = target_user.is_active
        
        # 更新用户状态
        success = users_service.admin_update_user_status(
            user_id=user_id,
            is_active=status_data.is_active,
            admin_id=current_admin.id,
            reason=status_data.reason
        )
        
        if not success:
            return ResponseUtil.error("更新用户状态失败")
        
        # 记录管理员操作日志
        try:
            client_ip = request.client.host if request.client else "unknown"
            users_service.log_admin_operation(
                admin_id=current_admin.id,
                target_user_id=user_id,
                operation_type="status_update",
                operation_description=f"用户状态从 {'激活' if old_status else '禁用'} 变更为 {'激活' if status_data.is_active else '禁用'}",
                before_value={"is_active": old_status},
                after_value={"is_active": status_data.is_active},
                reason=status_data.reason,
                ip_address=client_ip
            )
        except Exception as log_error:
            logger.warning("记录管理员操作日志失败", error=str(log_error))
        
        status_text = "激活" if status_data.is_active else "禁用"
        return ResponseUtil.success(
            data={"message": f"用户状态已更新为{status_text}", "timestamp": None},
            message=f"用户状态更新成功，已{status_text}该用户"
        )
        
    except ValueError as e:
        logger.warning("用户状态更新参数错误", error=str(e), admin_id=current_admin.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("更新用户状态异常", error=str(e), admin_id=current_admin.id, target_user_id=user_id)
        return ResponseUtil.error("更新用户状态失败，请稍后重试")


@router.put(
    "/{user_id}/permission",
    response_model=ApiResponse[SuccessMessage],
    summary="更新用户权限",
    response_description="返回用户权限更新结果"
)
async def update_user_permission(
    user_id: UUID,
    permission_data: UserPermissionUpdateRequest,
    request: Request,
    current_admin: UserProfile = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    管理员更新用户权限接口
    
    管理员可以授予或撤销用户的管理员权限：
    - 授予管理员权限后，用户可以访问管理功能
    - 撤销管理员权限后，用户只能访问普通用户功能
    - 必须提供权限变更原因
    - 操作将被记录到审计日志
    """
    try:
        # 防止管理员修改自己的权限
        if current_admin.id == user_id:
            return ResponseUtil.validation_error("不能修改自己的管理员权限")
        
        logger.info("管理员更新用户权限", 
                   admin_id=current_admin.id, 
                   admin_username=current_admin.username,
                   target_user_id=user_id,
                   new_permission=permission_data.is_admin,
                   reason=permission_data.reason)
        
        users_service = UsersService(db)
        
        # 获取目标用户信息
        target_user = users_service.get_user_by_id(user_id)
        if not target_user:
            return ResponseUtil.not_found("用户不存在")
        
        # 记录操作前权限
        old_permission = target_user.is_admin
        
        # 更新用户权限
        success = users_service.admin_update_user_permission(
            user_id=user_id,
            is_admin=permission_data.is_admin,
            admin_id=current_admin.id,
            reason=permission_data.reason
        )
        
        if not success:
            return ResponseUtil.error("更新用户权限失败")
        
        # 记录管理员操作日志
        try:
            client_ip = request.client.host if request.client else "unknown"
            users_service.log_admin_operation(
                admin_id=current_admin.id,
                target_user_id=user_id,
                operation_type="permission_update",
                operation_description=f"用户权限从 {'管理员' if old_permission else '普通用户'} 变更为 {'管理员' if permission_data.is_admin else '普通用户'}",
                before_value={"is_admin": old_permission},
                after_value={"is_admin": permission_data.is_admin},
                reason=permission_data.reason,
                ip_address=client_ip
            )
        except Exception as log_error:
            logger.warning("记录管理员操作日志失败", error=str(log_error))
        
        permission_text = "管理员" if permission_data.is_admin else "普通用户"
        return ResponseUtil.success(
            data={"message": f"用户权限已更新为{permission_text}", "timestamp": None},
            message=f"用户权限更新成功，已设置为{permission_text}"
        )
        
    except ValueError as e:
        logger.warning("用户权限更新参数错误", error=str(e), admin_id=current_admin.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("更新用户权限异常", error=str(e), admin_id=current_admin.id, target_user_id=user_id)
        return ResponseUtil.error("更新用户权限失败，请稍后重试")


@router.delete(
    "/{user_id}",
    response_model=ApiResponse[SuccessMessage],
    summary="删除用户",
    response_description="返回用户删除结果"
)
async def delete_user(
    user_id: UUID,
    reason: str = Query(..., min_length=10, max_length=200, description="删除原因，必须详细说明"),
    force: bool = Query(False, description="是否强制删除（即使有关联数据）"),
    request: Request = Depends(lambda: None),
    current_admin: UserProfile = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    管理员删除用户接口
    
    管理员可以删除用户账户：
    - 删除用户将移除所有相关数据
    - 必须提供详细的删除原因
    - 可选择是否强制删除（忽略关联数据）
    - 操作不可逆转，请谨慎使用
    
    ⚠️ 危险操作：此操作将永久删除用户和所有相关数据
    """
    try:
        # 防止管理员删除自己
        if current_admin.id == user_id:
            return ResponseUtil.validation_error("不能删除自己的账户")
        
        logger.warning("管理员请求删除用户", 
                      admin_id=current_admin.id, 
                      admin_username=current_admin.username,
                      target_user_id=user_id,
                      reason=reason,
                      force=force)
        
        users_service = UsersService(db)
        
        # 获取目标用户信息
        target_user = users_service.get_user_by_id(user_id)
        if not target_user:
            return ResponseUtil.not_found("用户不存在")
        
        # 检查是否可以删除
        if not force:
            dependency_check = users_service.check_user_dependencies(user_id)
            if dependency_check.get("has_dependencies", False):
                return ResponseUtil.validation_error(
                    f"用户存在关联数据，无法删除。关联数据：{dependency_check.get('dependencies', [])}。如需强制删除，请使用force=true参数"
                )
        
        # 执行删除
        success = users_service.admin_delete_user(
            user_id=user_id,
            admin_id=current_admin.id,
            reason=reason,
            force=force
        )
        
        if not success:
            return ResponseUtil.error("删除用户失败")
        
        # 记录管理员操作日志
        try:
            client_ip = request.client.host if request.client else "unknown"
            users_service.log_admin_operation(
                admin_id=current_admin.id,
                target_user_id=user_id,
                operation_type="user_deletion",
                operation_description=f"删除用户 {target_user.username} ({target_user.email})",
                before_value={"user_exists": True, "username": target_user.username, "email": target_user.email},
                after_value={"user_exists": False},
                reason=reason,
                ip_address=client_ip
            )
        except Exception as log_error:
            logger.warning("记录管理员操作日志失败", error=str(log_error))
        
        logger.warning("管理员删除用户成功", 
                      admin_id=current_admin.id, 
                      target_user_id=user_id,
                      target_username=target_user.username)
        
        return ResponseUtil.success(
            data={"message": "用户已删除", "timestamp": None},
            message="用户删除成功"
        )
        
    except ValueError as e:
        logger.warning("删除用户参数错误", error=str(e), admin_id=current_admin.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("删除用户异常", error=str(e), admin_id=current_admin.id, target_user_id=user_id)
        return ResponseUtil.error("删除用户失败，请稍后重试")


@router.get(
    "/statistics",
    response_model=ApiResponse[AdminUserStatsResponse],
    summary="获取用户统计信息",
    response_description="返回系统用户统计数据"
)
async def get_users_statistics(
    current_admin: UserProfile = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    管理员获取用户统计信息接口
    
    获取系统用户的全面统计数据：
    - 用户数量统计和趋势
    - 活跃度分析
    - 地域分布
    - 设备类型分布
    - 账户状态分布
    """
    try:
        logger.info("管理员查看用户统计信息", admin_id=current_admin.id, admin_username=current_admin.username)
        
        users_service = UsersService(db)
        stats = users_service.get_admin_users_statistics()
        
        return ResponseUtil.success(
            data=stats,
            message="获取用户统计信息成功"
        )
        
    except Exception as e:
        logger.error("获取用户统计信息异常", error=str(e), admin_id=current_admin.id)
        return ResponseUtil.error("获取用户统计信息失败，请稍后重试")


@router.get(
    "/operation-logs",
    response_model=ApiPagedResponse[AdminUserOperationLog],
    summary="获取管理员操作日志",
    response_description="返回管理员用户管理操作的审计日志"
)
async def get_admin_operation_logs(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    operation_type: Optional[str] = Query(None, description="操作类型筛选"),
    admin_id: Optional[UUID] = Query(None, description="操作管理员ID筛选"),
    target_user_id: Optional[UUID] = Query(None, description="目标用户ID筛选"),
    days: int = Query(30, ge=1, le=365, description="查询最近多少天的记录，默认30天"),
    current_admin: UserProfile = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    管理员获取操作日志接口
    
    获取管理员用户管理操作的审计日志：
    - 支持多条件筛选
    - 记录操作详情和变更内容
    - 包含操作时间和IP地址
    - 用于审计和追踪管理操作
    """
    try:
        logger.info("管理员查看操作日志", admin_id=current_admin.id, admin_username=current_admin.username)
        
        users_service = UsersService(db)
        logs, total = users_service.get_admin_operation_logs(
            page=page,
            page_size=page_size,
            operation_type=operation_type,
            admin_id=admin_id,
            target_user_id=target_user_id,
            days=days
        )
        
        return ResponseUtil.paginated(
            items=logs,
            total=total,
            page=page,
            page_size=page_size,
            message="获取操作日志成功"
        )
        
    except Exception as e:
        logger.error("获取操作日志异常", error=str(e), admin_id=current_admin.id)
        return ResponseUtil.error("获取操作日志失败，请稍后重试") 