"""认证相关接口"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.connection import get_db
from app.api.dependencies.auth import get_current_user, get_optional_user
from app.models.schemas.auth import (
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
from app.core.logging.logger import get_logger
from app.core.exceptions import ValidationError, BusinessLogicError
from app.utils.response import ResponseUtil

router = APIRouter()
logger = get_logger("auth")

@router.get("/health")
async def health_check():
    """健康检查接口"""
    logger.info("健康检查请求")
    return ResponseUtil.success(
        data={
            "status": "healthy",
            "version": "2.0.0"
        },
        message="系统运行正常"
    )

# ==================== 用户注册相关 ====================

@router.post("/register", summary="用户注册", response_description="注册成功，返回用户信息")
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
        logger.info("用户注册请求", username=register_data.username, email=register_data.email)
        
        # 临时实现 - 稍后连接真实的认证服务
        user_profile = UserProfile(
            user_id="new-user-" + register_data.username,
            username=register_data.username,
            email=register_data.email,
            nickname=register_data.nickname or register_data.username,
            phone=register_data.phone,
            is_active=True,
            is_admin=False,
            created_at="2024-12-10T21:30:00Z",
            last_login_at=None
        )
        
        logger.info("用户注册成功", username=register_data.username)
        return ResponseUtil.created(data=user_profile, message="注册成功")
        
    except Exception as e:
        logger.error("用户注册异常", error=str(e), username=register_data.username)
        raise BusinessLogicError("注册失败，请稍后重试")

# ==================== 用户登录相关 ====================

@router.post("/login/username", summary="用户名密码登录", response_description="登录成功，返回访问令牌和用户信息")
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
        logger.info("用户名密码登录请求", username=login_data.username)
        
        # 临时实现 - 稍后连接真实的认证服务
        user_profile = UserProfile(
            user_id="user-" + login_data.username,
            username=login_data.username,
            email=login_data.username + "@example.com",
            nickname="测试用户",
            phone=None,
            is_active=True,
            is_admin=False,
            created_at="2024-12-10T21:30:00Z",
            last_login_at="2024-12-10T21:30:00Z"
        )
        
        login_response = LoginResponse(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_token_" + login_data.username,
            token_type="bearer",
            expires_in=86400,
            user=user_profile
        )
        
        logger.info("用户名密码登录成功", username=login_data.username)
        return ResponseUtil.success(data=login_response, message="登录成功")
        
    except Exception as e:
        logger.error("用户名密码登录异常", error=str(e), username=login_data.username)
        raise BusinessLogicError("登录失败，请检查用户名和密码")

@router.post("/login/phone", summary="手机号密码登录", response_description="登录成功，返回访问令牌和用户信息")
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
        logger.info("手机号密码登录请求", phone=login_data.phone[-4:])  # 只记录后4位
        
        # 临时实现
        user_profile = UserProfile(
            user_id="user-phone-" + login_data.phone[-4:],
            username="phone_user_" + login_data.phone[-4:],
            email="phone" + login_data.phone[-4:] + "@example.com",
            nickname="手机用户",
            phone=login_data.phone,
            is_active=True,
            is_admin=False,
            created_at="2024-12-10T21:30:00Z",
            last_login_at="2024-12-10T21:30:00Z"
        )
        
        login_response = LoginResponse(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_token_phone_" + login_data.phone[-4:],
            token_type="bearer",
            expires_in=86400,
            user=user_profile
        )
        
        logger.info("手机号密码登录成功", phone=login_data.phone[-4:])
        return ResponseUtil.success(data=login_response, message="登录成功")
        
    except Exception as e:
        logger.error("手机号密码登录异常", error=str(e), phone=login_data.phone[-4:])
        raise BusinessLogicError("登录失败，请检查手机号和密码")

@router.post("/login/phone-code", summary="手机号验证码登录", response_description="登录成功，返回访问令牌和用户信息")
async def login_with_phone_code(
    login_data: PhoneCodeLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    手机号验证码登录接口
    
    使用手机号和验证码进行登录：
    - phone: 手机号码
    - code: 6位数字验证码
    - remember_me: 是否记住登录状态（可选）
    """
    try:
        logger.info("手机号验证码登录请求", phone=login_data.phone[-4:], code=login_data.code)
        
        # 临时验证码验证
        if login_data.code != "123456":
            raise ValidationError("验证码错误", field="code", invalid_value=login_data.code)
        
        # 临时实现
        user_profile = UserProfile(
            user_id="user-code-" + login_data.phone[-4:],
            username="code_user_" + login_data.phone[-4:],
            email="code" + login_data.phone[-4:] + "@example.com",
            nickname="验证码用户",
            phone=login_data.phone,
            is_active=True,
            is_admin=False,
            created_at="2024-12-10T21:30:00Z",
            last_login_at="2024-12-10T21:30:00Z"
        )
        
        login_response = LoginResponse(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_token_code_" + login_data.phone[-4:],
            token_type="bearer",
            expires_in=86400,
            user=user_profile
        )
        
        logger.info("手机号验证码登录成功", phone=login_data.phone[-4:])
        return ResponseUtil.success(data=login_response, message="登录成功")
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error("手机号验证码登录异常", error=str(e), phone=login_data.phone[-4:])
        raise BusinessLogicError("登录失败，请稍后重试")

# ==================== 验证码相关 ====================

@router.post("/code/send", summary="发送验证码", response_description="发送成功，返回发送状态")
async def send_verification_code(
    send_data: SendCodeRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    发送验证码接口
    
    支持多种验证码类型：
    - login: 登录验证码
    - register: 注册验证码
    - reset_password: 重置密码验证码
    """
    try:
        logger.info("发送验证码请求", phone=send_data.phone[-4:], code_type=send_data.code_type)
        
        # 临时实现 - 稍后连接真实的短信服务
        logger.info("验证码发送成功", phone=send_data.phone[-4:], code="123456")
        
        return ResponseUtil.success(
            data={
                "phone": send_data.phone,
                "code_type": send_data.code_type,
                "status": "sent",
                "expires_in": 300  # 5分钟
            },
            message="验证码发送成功"
        )
        
    except Exception as e:
        logger.error("发送验证码异常", error=str(e), phone=send_data.phone[-4:])
        raise BusinessLogicError("验证码发送失败，请稍后重试")

@router.post("/code/verify", summary="验证验证码", response_description="验证结果")
async def verify_verification_code(
    verify_data: VerifyCodeRequest,
    db: Session = Depends(get_db)
):
    """
    验证验证码接口
    
    验证用户输入的验证码是否正确。
    """
    try:
        logger.info("验证验证码请求", phone=verify_data.phone[-4:], code_type=verify_data.code_type)
        
        # 临时实现
        is_valid = verify_data.code == "123456"
        
        if is_valid:
            logger.info("验证码验证成功", phone=verify_data.phone[-4:])
        else:
            logger.warning("验证码验证失败", phone=verify_data.phone[-4:], code=verify_data.code)
            
        return ResponseUtil.success(
            data={"is_valid": is_valid},
            message="验证成功" if is_valid else "验证码错误"
        )
        
    except Exception as e:
        logger.error("验证验证码异常", error=str(e), phone=verify_data.phone[-4:])
        raise BusinessLogicError("验证失败，请稍后重试")

# ==================== 用户资料相关 ====================

@router.get("/profile", summary="获取用户资料", response_description="返回当前用户的详细信息")
async def get_user_profile(
    current_user = Depends(get_current_user)
):
    """
    获取用户资料接口
    
    返回当前登录用户的详细信息，需要有效的访问令牌。
    """
    logger.info("获取用户资料请求", user_id=current_user.user_id)
    
    # 临时实现
    user_profile = UserProfile(
        user_id=current_user.user_id,
        username=current_user.username,
        email=current_user.username + "@example.com",
        nickname="当前用户",
        phone=None,
        is_active=True,
        is_admin=False,
        created_at="2024-12-10T21:30:00Z",
        last_login_at="2024-12-10T21:30:00Z"
    )
    
    return ResponseUtil.success(data=user_profile, message="获取成功") 