"""
用户个人资料管理接口 - API v1

提供用户管理自己资料的相关功能：
- 查看个人信息
- 修改个人资料  
- 修改密码
- 查看登录日志
- 微信绑定管理
- 账户注销

权限等级：Level 2 - 需要用户认证，只能操作自己的数据
"""

import logging
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.api.dependencies.auth import get_current_user
from app.db.connection import get_db
from app.models.schemas.auth import UserProfile
from app.models.schemas.user import (
    UserUpdateRequest,
    UserPasswordChangeRequest,
    LoginLogInfo,
    WechatBindingInfo,
    UserProfileResponse,
    UserStatsInfo,
    UserActivityInfo
)
from app.models.schemas.common import ApiResponse, ApiPagedResponse, SuccessMessage
from app.utils.response import ResponseUtil
from app.core.logging.logger import get_logger

# 导入原有服务
from services.users_service import UsersService
from services.auth_service import AuthService
from sqlalchemy.orm import Session

logger = get_logger("api.user.profile")

# 创建路由器 - 用户个人资料管理
router = APIRouter(
    prefix="/profile",
    tags=["用户个人资料"],
    responses={
        401: {"description": "未授权 - 需要登录"},
        403: {"description": "权限不足"},
        404: {"description": "资源不存在"},
        500: {"description": "服务器内部错误"}
    }
)


@router.get(
    "/",
    response_model=ApiResponse[UserProfileResponse],
    summary="获取个人资料",
    response_description="返回当前用户的完整个人资料信息"
)
async def get_my_profile(
    include_stats: bool = Query(False, description="是否包含统计信息"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取个人资料接口
    
    获取当前登录用户的完整个人资料：
    - 基础信息：用户名、邮箱、昵称等
    - 账户状态：激活状态、验证状态等
    - 偏好设置：时区、语言、货币等
    - 可选统计信息：信用卡数量、交易统计等
    """
    try:
        logger.info("用户获取个人资料", user_id=current_user.id, username=current_user.username)
        
        users_service = UsersService(db)
        
        # 获取用户基础信息
        user_detail = users_service.get_user_by_id(current_user.id)
        if not user_detail:
            logger.warning("用户资料不存在", user_id=current_user.id)
            return ResponseUtil.not_found("用户资料不存在")
        
        # 构建响应数据
        response_data = {
            "id": user_detail.id,
            "username": user_detail.username,
            "email": user_detail.email,
            "nickname": user_detail.nickname,
            "phone": user_detail.phone,
            "avatar_url": user_detail.avatar_url,
            "is_active": user_detail.is_active,
            "is_verified": user_detail.is_verified,
            "is_admin": user_detail.is_admin,
            "timezone": user_detail.timezone,
            "language": user_detail.language,
            "currency": user_detail.currency,
            "last_login_at": user_detail.last_login_at,
            "email_verified_at": user_detail.email_verified_at,
            "created_at": user_detail.created_at,
            "updated_at": user_detail.updated_at
        }
        
        # 可选包含统计信息
        if include_stats:
            try:
                stats = users_service.get_user_statistics(current_user.id)
                response_data["stats"] = stats
            except Exception as e:
                logger.warning("获取用户统计信息失败", error=str(e), user_id=current_user.id)
                response_data["stats"] = None
        
        return ResponseUtil.success(
            data=response_data,
            message="获取个人资料成功"
        )
        
    except Exception as e:
        logger.error("获取个人资料异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取个人资料失败，请稍后重试")


@router.put(
    "/",
    response_model=ApiResponse[UserProfileResponse],
    summary="更新个人资料",
    response_description="返回更新后的用户资料信息"
)
async def update_my_profile(
    update_data: UserUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新个人资料接口
    
    用户可以更新自己的以下信息：
    - 昵称
    - 手机号
    - 头像URL
    - 时区设置
    - 语言偏好
    - 默认货币
    
    注意：用户名和邮箱不能通过此接口修改
    """
    try:
        logger.info("用户更新个人资料", user_id=current_user.id, username=current_user.username)
        
        users_service = UsersService(db)
        
        # 更新用户资料
        updated_user = users_service.update_user_profile(
            user_id=current_user.id,
            update_data=update_data.dict(exclude_unset=True)
        )
        
        if not updated_user:
            return ResponseUtil.not_found("用户不存在")
        
        logger.info("用户资料更新成功", user_id=current_user.id)
        return ResponseUtil.success(
            data=updated_user,
            message="个人资料更新成功"
        )
        
    except ValueError as e:
        logger.warning("用户资料更新参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("更新个人资料异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("更新个人资料失败，请稍后重试")


@router.put(
    "/password",
    response_model=ApiResponse[SuccessMessage],
    summary="修改密码",
    response_description="返回密码修改结果"
)
async def change_password(
    password_data: UserPasswordChangeRequest,
    request: Request,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码接口
    
    用户修改自己的登录密码：
    - 需要提供当前密码进行验证
    - 新密码必须满足安全要求
    - 修改成功后所有会话将失效，需要重新登录
    """
    try:
        logger.info("用户请求修改密码", user_id=current_user.id, username=current_user.username)
        
        auth_service = AuthService(db)
        
        # 验证当前密码
        is_valid = auth_service.verify_password(
            username=current_user.username,
            password=password_data.current_password
        )
        
        if not is_valid:
            logger.warning("用户密码验证失败", user_id=current_user.id)
            return ResponseUtil.error("当前密码错误", code=400)
        
        # 更新密码
        success = auth_service.change_user_password(
            user_id=current_user.id,
            new_password=password_data.new_password
        )
        
        if not success:
            return ResponseUtil.error("密码修改失败，请稍后重试")
        
        # 记录密码修改日志
        try:
            client_ip = request.client.host if request.client else "unknown"
            auth_service.log_security_event(
                user_id=current_user.id,
                event_type="password_changed",
                ip_address=client_ip,
                user_agent=request.headers.get("user-agent", "unknown"),
                details={"changed_by": "user_self"}
            )
        except Exception as log_error:
            logger.warning("记录密码修改日志失败", error=str(log_error))
        
        logger.info("用户密码修改成功", user_id=current_user.id)
        return ResponseUtil.success(
            data={"message": "密码修改成功，请重新登录", "timestamp": None},
            message="密码修改成功，所有会话已失效，请重新登录"
        )
        
    except ValueError as e:
        logger.warning("密码修改参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("修改密码异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("修改密码失败，请稍后重试")


@router.get(
    "/login-logs",
    response_model=ApiPagedResponse[LoginLogInfo],
    summary="获取登录日志",
    response_description="返回当前用户的登录历史记录"
)
async def get_my_login_logs(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    days: int = Query(30, ge=1, le=365, description="查询最近多少天的记录，默认30天"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取登录日志接口
    
    获取当前用户的登录历史记录：
    - 登录时间和IP地址
    - 登录方式和设备信息
    - 登录成功或失败状态
    - 地理位置信息（如果可用）
    """
    try:
        logger.info("用户查看登录日志", user_id=current_user.id, username=current_user.username)
        
        users_service = UsersService(db)
        logs, total = users_service.get_user_login_logs(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            days=days
        )
        
        return ResponseUtil.paginated(
            items=logs,
            total=total,
            page=page,
            page_size=page_size,
            message="获取登录日志成功"
        )
        
    except Exception as e:
        logger.error("获取登录日志异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取登录日志失败，请稍后重试")


@router.get(
    "/wechat-binding",
    response_model=ApiResponse[WechatBindingInfo],
    summary="获取微信绑定信息",
    response_description="返回当前用户的微信绑定状态"
)
async def get_my_wechat_binding(
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取微信绑定信息接口
    
    获取当前用户的微信绑定状态：
    - 绑定状态和绑定时间
    - 微信昵称和头像（已脱敏）
    - 绑定是否激活
    """
    try:
        logger.info("用户查看微信绑定信息", user_id=current_user.id, username=current_user.username)
        
        users_service = UsersService(db)
        wechat_info = users_service.get_user_wechat_binding(current_user.id)
        
        if not wechat_info:
            return ResponseUtil.not_found("尚未绑定微信账户")
        
        return ResponseUtil.success(
            data=wechat_info,
            message="获取微信绑定信息成功"
        )
        
    except Exception as e:
        logger.error("获取微信绑定信息异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取微信绑定信息失败，请稍后重试")


@router.delete(
    "/wechat-binding",
    response_model=ApiResponse[SuccessMessage],
    summary="解除微信绑定",
    response_description="返回解绑结果"
)
async def unbind_wechat(
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    解除微信绑定接口
    
    用户可以主动解除微信账户绑定：
    - 解绑后将无法使用微信登录
    - 需要使用用户名/手机号登录
    """
    try:
        logger.info("用户请求解除微信绑定", user_id=current_user.id, username=current_user.username)
        
        users_service = UsersService(db)
        success = users_service.unbind_wechat(current_user.id)
        
        if not success:
            return ResponseUtil.not_found("微信绑定不存在或已解除")
        
        logger.info("用户微信解绑成功", user_id=current_user.id)
        return ResponseUtil.success(
            data={"message": "微信绑定已解除", "timestamp": None},
            message="微信绑定解除成功"
        )
        
    except Exception as e:
        logger.error("解除微信绑定异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("解除微信绑定失败，请稍后重试")


@router.get(
    "/activity",
    response_model=ApiResponse[UserActivityInfo],
    summary="获取活动信息",
    response_description="返回当前用户的活动统计信息"
)
async def get_my_activity(
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取活动信息接口
    
    获取当前用户的活动统计：
    - 登录活动统计
    - 最近操作时间
    - 活跃会话数量
    """
    try:
        logger.info("用户查看活动信息", user_id=current_user.id, username=current_user.username)
        
        users_service = UsersService(db)
        activity_info = users_service.get_user_activity_info(current_user.id)
        
        return ResponseUtil.success(
            data=activity_info,
            message="获取活动信息成功"
        )
        
    except Exception as e:
        logger.error("获取活动信息异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取活动信息失败，请稍后重试")


@router.delete(
    "/",
    response_model=ApiResponse[SuccessMessage],
    summary="注销账户",
    response_description="返回注销结果"
)
async def delete_my_account(
    confirmation: str = Query(..., description="确认删除，必须输入 'DELETE_MY_ACCOUNT'"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    注销账户接口
    
    用户主动注销自己的账户：
    - 需要明确确认操作
    - 将删除所有相关数据
    - 操作不可逆转
    
    ⚠️ 危险操作：此操作将永久删除账户和所有相关数据
    """
    try:
        # 确认操作
        if confirmation != "DELETE_MY_ACCOUNT":
            return ResponseUtil.validation_error("请输入正确的确认文本：DELETE_MY_ACCOUNT")
        
        logger.warning("用户请求注销账户", user_id=current_user.id, username=current_user.username)
        
        users_service = UsersService(db)
        success = users_service.delete_user_account(current_user.id)
        
        if not success:
            return ResponseUtil.error("账户注销失败，请联系客服")
        
        logger.warning("用户账户注销成功", user_id=current_user.id, username=current_user.username)
        return ResponseUtil.success(
            data={"message": "账户已注销", "timestamp": None},
            message="账户注销成功，感谢您的使用"
        )
        
    except Exception as e:
        logger.error("注销账户异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("注销账户失败，请稍后重试或联系客服") 