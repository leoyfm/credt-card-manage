"""
用户认证路由

包含用户注册、登录、登出、验证码等认证相关的API接口。
"""

import logging
from datetime import timedelta
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from models.users import (
    UserRegisterRequest,
    UsernamePasswordLogin,
    PhonePasswordLogin, 
    PhoneCodeLogin,
    WechatLoginRequest,
    LoginResponse,
    UserProfile,
    UserUpdateRequest,
    ChangePasswordRequest,
    ResetPasswordRequest,
    SendCodeRequest,
    VerifyCodeRequest,
    RefreshTokenRequest,
    LogoutRequest
)
from models.response import ApiResponse
from services.auth_service import AuthService
from utils.auth import AuthUtils, IPUtils
from utils.response import ResponseUtil

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/auth", tags=["用户认证"])

# 安全依赖
security = HTTPBearer()

# 数据库依赖（需要根据实际项目配置）
def get_db():
    """获取数据库会话"""
    # TODO: 实现数据库依赖注入
    pass

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> UserProfile:
    """
    获取当前登录用户
    
    从JWT令牌中解析用户信息，用于需要认证的接口。
    """
    token = credentials.credentials
    payload = AuthUtils.verify_access_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌格式错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    auth_service = AuthService(db)
    user = auth_service.get_user_profile(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# ==================== 用户注册相关 ====================

@router.post(
    "/register",
    response_model=ApiResponse[UserProfile],
    summary="用户注册",
    response_description="注册成功，返回用户信息"
)
async def register(
    register_data: UserRegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    用户注册接口
    
    支持用户名、邮箱注册，可选手机号验证。
    - 用户名：3-20位字符，支持字母、数字、下划线
    - 邮箱：标准邮箱格式
    - 密码：8-30位字符，包含字母和数字
    - 手机号：可选，需要验证码验证
    - 昵称：可选，默认使用用户名
    """
    try:
        auth_service = AuthService(db)
        ip_address = IPUtils.get_client_ip(request)
        
        user_profile = auth_service.register_user(register_data, ip_address)
        
        logger.info(f"用户注册成功 - username: {register_data.username}")
        return ResponseUtil.success(
            data=user_profile,
            message="注册成功"
        )
        
    except ValueError as e:
        logger.warning(f"用户注册失败 - {str(e)}")
        return ResponseUtil.error(message=str(e))
    except Exception as e:
        logger.error(f"用户注册异常 - {str(e)}")
        return ResponseUtil.error(message="注册失败，请稍后重试")


# ==================== 用户登录相关 ====================

@router.post(
    "/login/username",
    response_model=ApiResponse[LoginResponse],
    summary="用户名密码登录",
    response_description="登录成功，返回访问令牌和用户信息"
)
async def login_with_username_password(
    login_data: UsernamePasswordLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    用户名密码登录接口
    
    支持用户名或邮箱登录：
    - username: 用户名或邮箱地址
    - password: 用户密码
    - remember_me: 是否记住登录状态（可选）
    
    登录成功返回JWT访问令牌，有效期24小时。
    """
    try:
        auth_service = AuthService(db)
        ip_address = IPUtils.get_client_ip(request)
        
        login_response = auth_service.login_with_username_password(login_data, ip_address)
        
        logger.info(f"用户名密码登录成功 - username: {login_data.username}")
        return ResponseUtil.success(
            data=login_response,
            message="登录成功"
        )
        
    except ValueError as e:
        logger.warning(f"用户名密码登录失败 - {str(e)}")
        return ResponseUtil.error(message=str(e))
    except Exception as e:
        logger.error(f"用户名密码登录异常 - {str(e)}")
        return ResponseUtil.error(message="登录失败，请稍后重试")


@router.post(
    "/login/phone",
    response_model=ApiResponse[LoginResponse],
    summary="手机号密码登录",
    response_description="登录成功，返回访问令牌和用户信息"
)
async def login_with_phone_password(
    login_data: PhonePasswordLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    手机号密码登录接口
    
    使用手机号和密码进行登录：
    - phone: 手机号码，支持中国大陆手机号格式
    - password: 用户密码
    - remember_me: 是否记住登录状态（可选）
    """
    try:
        auth_service = AuthService(db)
        ip_address = IPUtils.get_client_ip(request)
        
        login_response = auth_service.login_with_phone_password(login_data, ip_address)
        
        logger.info(f"手机号密码登录成功 - phone: {login_data.phone}")
        return ResponseUtil.success(
            data=login_response,
            message="登录成功"
        )
        
    except ValueError as e:
        logger.warning(f"手机号密码登录失败 - {str(e)}")
        return ResponseUtil.error(message=str(e))
    except Exception as e:
        logger.error(f"手机号密码登录异常 - {str(e)}")
        return ResponseUtil.error(message="登录失败，请稍后重试")


@router.post(
    "/login/phone-code",
    response_model=ApiResponse[LoginResponse],
    summary="手机号验证码登录",
    response_description="登录成功，返回访问令牌和用户信息"
)
async def login_with_phone_code(
    login_data: PhoneCodeLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    手机号验证码登录接口
    
    使用手机号和验证码进行登录，支持自动注册：
    - phone: 手机号码
    - verification_code: 6位数字验证码
    
    如果手机号未注册，将自动创建新用户。
    """
    try:
        auth_service = AuthService(db)
        ip_address = IPUtils.get_client_ip(request)
        
        login_response = auth_service.login_with_phone_code(login_data, ip_address)
        
        logger.info(f"手机号验证码登录成功 - phone: {login_data.phone}")
        return ResponseUtil.success(
            data=login_response,
            message="登录成功"
        )
        
    except ValueError as e:
        logger.warning(f"手机号验证码登录失败 - {str(e)}")
        return ResponseUtil.error(message=str(e))
    except Exception as e:
        logger.error(f"手机号验证码登录异常 - {str(e)}")
        return ResponseUtil.error(message="登录失败，请稍后重试")


@router.post(
    "/login/wechat",
    response_model=ApiResponse[LoginResponse],
    summary="微信登录",
    response_description="登录成功，返回访问令牌和用户信息"
)
async def login_with_wechat(
    login_data: WechatLoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    微信登录接口
    
    使用微信授权码进行登录：
    - code: 微信授权码，由微信客户端获取
    - user_info: 可选的用户补充信息
    
    首次登录会自动创建账户并绑定微信。
    """
    try:
        auth_service = AuthService(db)
        ip_address = IPUtils.get_client_ip(request)
        
        login_response = auth_service.login_with_wechat(login_data, ip_address)
        
        logger.info(f"微信登录成功 - code: {login_data.code}")
        return ResponseUtil.success(
            data=login_response,
            message="登录成功"
        )
        
    except ValueError as e:
        logger.warning(f"微信登录失败 - {str(e)}")
        return ResponseUtil.error(message=str(e))
    except Exception as e:
        logger.error(f"微信登录异常 - {str(e)}")
        return ResponseUtil.error(message="登录失败，请稍后重试")


# ==================== 验证码相关 ====================

@router.post(
    "/code/send",
    response_model=ApiResponse[Dict[str, str]],
    summary="发送验证码",
    response_description="发送成功，返回发送状态"
)
async def send_verification_code(
    send_data: SendCodeRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    发送验证码接口
    
    支持向手机号或邮箱发送验证码：
    - phone_or_email: 手机号或邮箱地址
    - code_type: 验证码类型（注册、登录、重置密码、绑定手机）
    
    限制：同一手机号/邮箱每分钟只能发送一次验证码。
    """
    try:
        auth_service = AuthService(db)
        ip_address = IPUtils.get_client_ip(request)
        
        success = auth_service.send_verification_code(send_data, ip_address)
        
        if success:
            logger.info(f"验证码发送成功 - {send_data.phone_or_email}")
            return ResponseUtil.success(
                data={"status": "sent"},
                message="验证码发送成功"
            )
        else:
            return ResponseUtil.error(message="验证码发送失败")
            
    except ValueError as e:
        logger.warning(f"验证码发送失败 - {str(e)}")
        return ResponseUtil.error(message=str(e))
    except Exception as e:
        logger.error(f"验证码发送异常 - {str(e)}")
        return ResponseUtil.error(message="发送失败，请稍后重试")


@router.post(
    "/code/verify",
    response_model=ApiResponse[Dict[str, bool]],
    summary="验证验证码",
    response_description="验证结果"
)
async def verify_verification_code(
    verify_data: VerifyCodeRequest,
    db: Session = Depends(get_db)
):
    """
    验证验证码接口
    
    验证手机号或邮箱的验证码是否正确：
    - phone_or_email: 手机号或邮箱地址
    - code: 验证码
    - code_type: 验证码类型
    
    验证成功后验证码将标记为已使用。
    """
    try:
        auth_service = AuthService(db)
        
        is_valid = auth_service.verify_code(
            verify_data.phone_or_email,
            verify_data.code,
            verify_data.code_type
        )
        
        if is_valid:
            return ResponseUtil.success(
                data={"valid": True},
                message="验证码正确"
            )
        else:
            return ResponseUtil.error(
                data={"valid": False},
                message="验证码无效或已过期"
            )
            
    except Exception as e:
        logger.error(f"验证码验证异常 - {str(e)}")
        return ResponseUtil.error(message="验证失败，请稍后重试")


# ==================== 用户信息管理 ====================

@router.get(
    "/profile",
    response_model=ApiResponse[UserProfile],
    summary="获取用户资料",
    response_description="返回当前用户的详细信息"
)
async def get_user_profile(
    current_user: UserProfile = Depends(get_current_user)
):
    """
    获取用户资料接口
    
    返回当前登录用户的详细信息，包括：
    - 基本信息：用户名、昵称、邮箱、手机号
    - 状态信息：注册时间、最后登录时间、登录次数
    - 认证信息：是否已验证、是否激活
    """
    return ResponseUtil.success(
        data=current_user,
        message="获取用户资料成功"
    )


@router.put(
    "/profile",
    response_model=ApiResponse[UserProfile],
    summary="更新用户资料",
    response_description="返回更新后的用户信息"
)
async def update_user_profile(
    update_data: UserUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户资料接口
    
    支持更新以下字段：
    - nickname: 昵称
    - avatar_url: 头像URL
    - gender: 性别
    - birthday: 生日
    - bio: 个人简介
    """
    try:
        auth_service = AuthService(db)
        
        updated_user = auth_service.update_user_profile(current_user.id, update_data)
        
        if updated_user:
            logger.info(f"用户资料更新成功 - user_id: {current_user.id}")
            return ResponseUtil.success(
                data=updated_user,
                message="资料更新成功"
            )
        else:
            return ResponseUtil.error(message="用户不存在")
            
    except Exception as e:
        logger.error(f"用户资料更新异常 - {str(e)}")
        return ResponseUtil.error(message="更新失败，请稍后重试")


@router.post(
    "/password/change",
    response_model=ApiResponse[Dict[str, str]],
    summary="修改密码",
    response_description="密码修改结果"
)
async def change_password(
    change_data: ChangePasswordRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码接口
    
    用户在已登录状态下修改密码：
    - old_password: 当前密码
    - new_password: 新密码
    
    修改成功后建议用户重新登录。
    """
    try:
        auth_service = AuthService(db)
        
        success = auth_service.change_password(current_user.id, change_data)
        
        if success:
            logger.info(f"密码修改成功 - user_id: {current_user.id}")
            return ResponseUtil.success(
                data={"status": "changed"},
                message="密码修改成功"
            )
        else:
            return ResponseUtil.error(message="用户不存在")
            
    except ValueError as e:
        logger.warning(f"密码修改失败 - {str(e)}")
        return ResponseUtil.error(message=str(e))
    except Exception as e:
        logger.error(f"密码修改异常 - {str(e)}")
        return ResponseUtil.error(message="修改失败，请稍后重试")


@router.post(
    "/password/reset",
    response_model=ApiResponse[Dict[str, str]],
    summary="重置密码",
    response_description="密码重置结果"
)
async def reset_password(
    reset_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    重置密码接口
    
    通过验证码重置密码，用于忘记密码场景：
    - phone_or_email: 手机号或邮箱
    - verification_code: 验证码
    - new_password: 新密码
    
    需要先调用发送验证码接口获取验证码。
    """
    try:
        auth_service = AuthService(db)
        
        success = auth_service.reset_password(reset_data)
        
        if success:
            logger.info(f"密码重置成功 - {reset_data.phone_or_email}")
            return ResponseUtil.success(
                data={"status": "reset"},
                message="密码重置成功"
            )
        else:
            return ResponseUtil.error(message="重置失败")
            
    except ValueError as e:
        logger.warning(f"密码重置失败 - {str(e)}")
        return ResponseUtil.error(message=str(e))
    except Exception as e:
        logger.error(f"密码重置异常 - {str(e)}")
        return ResponseUtil.error(message="重置失败，请稍后重试")


# ==================== 令牌管理 ====================

@router.post(
    "/token/refresh",
    response_model=ApiResponse[LoginResponse],
    summary="刷新访问令牌",
    response_description="返回新的访问令牌"
)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    刷新访问令牌接口
    
    使用刷新令牌获取新的访问令牌：
    - refresh_token: 刷新令牌
    
    当访问令牌即将过期时使用此接口获取新令牌。
    """
    try:
        # 验证刷新令牌
        payload = AuthUtils.verify_access_token(refresh_data.refresh_token)
        if not payload:
            return ResponseUtil.error(message="刷新令牌无效或已过期")
        
        user_id = payload.get("sub")
        username = payload.get("username")
        
        if not user_id or not username:
            return ResponseUtil.error(message="刷新令牌格式错误")
        
        # 生成新的访问令牌
        new_access_token = AuthUtils.create_access_token({
            "sub": user_id,
            "username": username
        })
        
        # 获取用户信息
        auth_service = AuthService(db)
        user = auth_service.get_user_profile(user_id)
        
        if not user:
            return ResponseUtil.error(message="用户不存在")
        
        login_response = LoginResponse(
            access_token=new_access_token,
            token_type="bearer",
            expires_in=AuthUtils.get_token_expires_in(),
            user=user
        )
        
        logger.info(f"令牌刷新成功 - user_id: {user_id}")
        return ResponseUtil.success(
            data=login_response,
            message="令牌刷新成功"
        )
        
    except Exception as e:
        logger.error(f"令牌刷新异常 - {str(e)}")
        return ResponseUtil.error(message="刷新失败，请重新登录")


@router.post(
    "/logout",
    response_model=ApiResponse[Dict[str, str]],
    summary="用户登出",
    response_description="登出结果"
)
async def logout(
    logout_data: LogoutRequest,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    用户登出接口
    
    用户主动登出，可选择：
    - all_devices: 是否登出所有设备
    
    登出后客户端应清除本地存储的令牌。
    """
    try:
        # TODO: 实现令牌黑名单机制（可选）
        # 如果需要立即失效令牌，可以将令牌加入黑名单
        
        logger.info(f"用户登出 - user_id: {current_user.id}")
        return ResponseUtil.success(
            data={"status": "logged_out"},
            message="登出成功"
        )
        
    except Exception as e:
        logger.error(f"用户登出异常 - {str(e)}")
        return ResponseUtil.error(message="登出失败，请稍后重试")


# ==================== 账户状态检查 ====================

@router.get(
    "/status",
    response_model=ApiResponse[Dict[str, Any]],
    summary="检查认证状态",
    response_description="返回当前认证状态信息"
)
async def check_auth_status(
    current_user: UserProfile = Depends(get_current_user)
):
    """
    检查认证状态接口
    
    返回当前用户的认证状态信息：
    - 是否已登录
    - 令牌剩余有效时间
    - 用户基本信息
    """
    try:
        status_info = {
            "authenticated": True,
            "user_id": str(current_user.id),
            "username": current_user.username,
            "is_verified": current_user.is_verified,
            "is_active": current_user.is_active
        }
        
        return ResponseUtil.success(
            data=status_info,
            message="认证状态正常"
        )
        
    except Exception as e:
        logger.error(f"认证状态检查异常 - {str(e)}")
        return ResponseUtil.error(message="状态检查失败") 