"""
用户资料管理API路由 - Level 2权限
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.logging import app_logger
from app.db.database import get_db
from app.services.user_service import UserService
from app.models.schemas.user import (
    UserProfileResponse,
    UserProfileUpdateRequest,
    ChangePasswordRequest,
    LoginLogResponse,
    AccountDeletionRequest,
    WechatBindingResponse,
    UserStatisticsResponse
)
from app.utils.response import ApiResponse, ApiPagedResponse
from app.utils.response import ResponseUtil
from app.api.dependencies.auth import get_current_user
from app.models.database.user import User

router = APIRouter(prefix="/profile", tags=["v1-用户-个人资料"])

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """获取用户服务实例"""
    return UserService(db)

@router.get(
    "/info",
    response_model=ApiResponse[UserProfileResponse],
    summary="获取个人信息",
    description="获取当前用户的个人资料信息",
)
async def get_user_info(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """获取用户个人信息"""
    try:
        profile = user_service.get_user_profile(str(current_user.id))
        return ResponseUtil.success(data=profile, message="获取个人信息成功")
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"获取个人信息失败: {str(e)}")
        return ResponseUtil.error(message="获取个人信息失败")

@router.put(
    "/update",
    response_model=ApiResponse[UserProfileResponse],
    summary="更新个人资料",
    description="更新当前用户的个人资料信息",
)
async def update_user_profile(
    update_data: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """更新用户个人资料"""
    try:
        profile = user_service.update_user_profile(str(current_user.id), update_data)
        return ResponseUtil.success(data=profile, message="个人资料更新成功")
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"个人资料更新失败: {str(e)}")
        return ResponseUtil.error(message="个人资料更新失败")

@router.post(
    "/change-password",
    response_model=ApiResponse[bool],
    summary="修改密码",
    description="修改当前用户的登录密码",
)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """修改用户密码"""
    try:
        success = user_service.change_password(str(current_user.id), password_data)
        return ResponseUtil.success(data=success, message="密码修改成功")
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"密码修改失败: {str(e)}")
        return ResponseUtil.error(message="密码修改失败")

@router.get(
    "/login-logs",
    response_model=ApiPagedResponse[LoginLogResponse],
    summary="个人登录日志",
    description="获取当前用户的登录日志记录",
)
async def get_login_logs(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """获取用户登录日志"""
    try:
        logs, total = user_service.get_user_login_logs(
            str(current_user.id), page, page_size
        )
        
        return ResponseUtil.paginated(
            items=logs,
            total=total,
            page=page,
            page_size=page_size,
            message="获取登录日志成功"
        )
    except Exception as e:
        app_logger.error(f"获取登录日志失败: {str(e)}")
        return ResponseUtil.error(message="获取登录日志失败")

@router.post(
    "/logout",
    response_model=ApiResponse[bool],
    summary="退出登录",
    description="退出当前用户的登录状态",
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """用户退出登录"""
    try:
        # 记录退出登录日志
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        user_service.record_login_log(
            user_id=str(current_user.id),
            login_type="logout",
            login_method="api",
            ip_address=ip_address,
            user_agent=user_agent,
            is_success=True
        )
        
        # TODO: 在实际应用中，这里应该将JWT令牌加入黑名单
        # 或者使用Redis存储活跃令牌，退出时删除
        
        app_logger.info(f"用户退出登录: {current_user.username}")
        return ResponseUtil.success(data=True, message="退出登录成功")
    except Exception as e:
        app_logger.error(f"退出登录失败: {str(e)}")
        return ResponseUtil.error(message="退出登录失败")

@router.delete(
    "/account",
    response_model=ApiResponse[bool],
    summary="注销账户",
    description="注销当前用户账户（软删除）",
)
async def delete_account(
    deletion_data: AccountDeletionRequest,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """注销用户账户"""
    try:
        success = user_service.delete_user_account(str(current_user.id), deletion_data)
        return ResponseUtil.success(data=success, message="账户注销成功")
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"账户注销失败: {str(e)}")
        return ResponseUtil.error(message="账户注销失败")

@router.get(
    "/wechat-bindings",
    response_model=ApiResponse[List[WechatBindingResponse]],
    summary="微信绑定信息",
    description="获取当前用户的微信绑定信息",
)
async def get_wechat_bindings(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """获取用户微信绑定信息"""
    try:
        bindings = user_service.get_user_wechat_bindings(str(current_user.id))
        return ResponseUtil.success(data=bindings, message="获取微信绑定信息成功")
    except Exception as e:
        app_logger.error(f"获取微信绑定信息失败: {str(e)}")
        return ResponseUtil.error(message="获取微信绑定信息失败")

@router.get(
    "/statistics",
    response_model=ApiResponse[UserStatisticsResponse],
    summary="个人统计信息",
    description="获取当前用户的统计信息（卡片、交易、积分等）",
)
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """获取用户统计信息"""
    try:
        stats = user_service.get_user_statistics(str(current_user.id))
        return ResponseUtil.success(data=stats, message="获取统计信息成功")
    except Exception as e:
        app_logger.error(f"获取统计信息失败: {str(e)}")
        return ResponseUtil.error(message="获取统计信息失败") 