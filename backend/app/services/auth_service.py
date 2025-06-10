"""
用户认证服务层

包含用户注册、登录、验证码管理等业务逻辑。
新架构下的认证服务，支持完整的用户认证流程。
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any, Tuple, List
from uuid import UUID

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models.schemas.auth import (
    UserRegisterRequest,
    UsernamePasswordLogin,
    PhonePasswordLogin,
    PhoneCodeLogin,
    WechatLoginRequest,
    LoginResponse,
    SendCodeRequest,
    VerifyCodeRequest,
    ChangePasswordRequest,
    ResetPasswordRequest,
    CodeType,
    UserProfile
)
from app.models.schemas.user import (
    UserUpdateRequest,
    WechatBindingInfo
)
from app.models.database import User, VerificationCode, WechatBinding, LoginLog
from app.utils.auth import AuthUtils
from app.utils.verification import VerificationCodeUtils
from app.utils.security import SecurityUtils
from app.utils.wechat import WechatUtils
from app.utils.ip_location import IPUtils
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """用户认证服务"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 用户注册相关 ====================

    def register_user(self, register_data: UserRegisterRequest, ip_address: str) -> UserProfile:
        """
        用户注册
        
        创建新用户账户，包括数据验证、重复检查、密码哈希等。
        
        参数:
        - register_data: 注册数据
        - ip_address: 注册IP地址
        
        返回:
        - 用户资料信息
        
        异常:
        - ValueError: 用户名、邮箱或手机号已存在
        - ValueError: 验证码无效（如果需要）
        """
        logger.info(f"用户注册请求 - username: {register_data.username}, email: {register_data.email}")

        # 检查用户名、邮箱、手机号是否已存在
        self._check_user_exists(register_data.username, register_data.email, register_data.phone)

        # 如果提供了手机号，验证验证码
        if register_data.phone and register_data.verification_code:
            if not self.verify_code(register_data.phone, register_data.verification_code, CodeType.REGISTER):
                raise ValueError("验证码无效或已过期")

        # 创建用户
        user = User(
            username=register_data.username,
            email=register_data.email,
            password_hash=AuthUtils.hash_password(register_data.password),
            phone=register_data.phone,
            nickname=register_data.nickname or register_data.username,
            is_verified=bool(register_data.phone and register_data.verification_code),
            login_count=0
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # 记录登录日志
        self._create_login_log(user.id, "register", ip_address, True)

        logger.info(f"用户注册成功 - user_id: {user.id}, username: {user.username}")
        return UserProfile.model_validate(user)

    def _check_user_exists(self, username: str, email: str, phone: Optional[str] = None):
        """检查用户是否已存在"""
        # 检查用户名
        if self._get_user_by_username(username):
            raise ValueError(f"用户名 '{username}' 已存在")

        # 检查邮箱
        if self._get_user_by_email(email):
            raise ValueError(f"邮箱 '{email}' 已被注册")

        # 检查手机号
        if phone and self._get_user_by_phone(phone):
            raise ValueError(f"手机号 '{phone}' 已被注册")

    # ==================== 用户登录相关 ====================

    def login_with_username_password(
        self, 
        login_data: UsernamePasswordLogin, 
        ip_address: str
    ) -> LoginResponse:
        """
        用户名密码登录
        
        支持用户名或邮箱登录。
        
        参数:
        - login_data: 登录数据
        - ip_address: 登录IP地址
        
        返回:
        - 登录响应，包含令牌和用户信息
        
        异常:
        - ValueError: 用户不存在或密码错误
        """
        logger.info(f"用户名密码登录请求 - username: {login_data.username}")

        # 通过用户名或邮箱查找用户
        user = self._get_user_by_username_or_email(login_data.username)
        if not user:
            self._create_login_log(None, "username_password", ip_address, False, "用户不存在")
            raise ValueError("用户不存在")

        # 验证密码
        if not AuthUtils.verify_password(login_data.password, user.password_hash):
            self._create_login_log(user.id, "username_password", ip_address, False, "密码错误")
            raise ValueError("密码错误")

        # 检查用户状态
        if not user.is_active:
            self._create_login_log(user.id, "username_password", ip_address, False, "账户已被禁用")
            raise ValueError("账户已被禁用")

        # 更新登录信息
        self._update_login_info(user, ip_address, "username_password")

        # 生成令牌
        access_token = AuthUtils.create_access_token({"sub": str(user.id), "username": user.username})

        logger.info(f"用户名密码登录成功 - user_id: {user.id}")
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=AuthUtils.get_token_expires_in(),
            user=UserProfile.model_validate(user)
        )

    def login_with_phone_password(
        self, 
        login_data: PhonePasswordLogin, 
        ip_address: str
    ) -> LoginResponse:
        """
        手机号密码登录
        
        参数:
        - login_data: 登录数据
        - ip_address: 登录IP地址
        
        返回:
        - 登录响应
        
        异常:
        - ValueError: 手机号不存在或密码错误
        """
        logger.info(f"手机号密码登录请求 - phone: {login_data.phone}")

        user = self._get_user_by_phone(login_data.phone)
        if not user:
            self._create_login_log(None, "phone_password", ip_address, False, "手机号未注册")
            raise ValueError("手机号未注册")

        if not AuthUtils.verify_password(login_data.password, user.password_hash):
            self._create_login_log(user.id, "phone_password", ip_address, False, "密码错误")
            raise ValueError("密码错误")

        if not user.is_active:
            self._create_login_log(user.id, "phone_password", ip_address, False, "账户已被禁用")
            raise ValueError("账户已被禁用")

        self._update_login_info(user, ip_address, "phone_password")
        access_token = AuthUtils.create_access_token({"sub": str(user.id), "username": user.username})

        logger.info(f"手机号密码登录成功 - user_id: {user.id}")
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=AuthUtils.get_token_expires_in(),
            user=UserProfile.model_validate(user)
        )

    def login_with_phone_code(
        self, 
        login_data: PhoneCodeLogin, 
        ip_address: str
    ) -> LoginResponse:
        """
        手机号验证码登录
        
        参数:
        - login_data: 登录数据
        - ip_address: 登录IP地址
        
        返回:
        - 登录响应
        
        异常:
        - ValueError: 手机号未注册或验证码错误
        """
        logger.info(f"手机号验证码登录请求 - phone: {login_data.phone}")

        # 验证验证码
        if not self.verify_code(login_data.phone, login_data.verification_code, CodeType.LOGIN):
            self._create_login_log(None, "phone_code", ip_address, False, "验证码无效")
            raise ValueError("验证码无效或已过期")

        user = self._get_user_by_phone(login_data.phone)
        if not user:
            self._create_login_log(None, "phone_code", ip_address, False, "手机号未注册")
            raise ValueError("手机号未注册")

        if not user.is_active:
            self._create_login_log(user.id, "phone_code", ip_address, False, "账户已被禁用")
            raise ValueError("账户已被禁用")

        self._update_login_info(user, ip_address, "phone_code")
        access_token = AuthUtils.create_access_token({"sub": str(user.id), "username": user.username})

        logger.info(f"手机号验证码登录成功 - user_id: {user.id}")
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=AuthUtils.get_token_expires_in(),
            user=UserProfile.model_validate(user)
        )

    def login_with_wechat(
        self, 
        login_data: WechatLoginRequest, 
        ip_address: str
    ) -> LoginResponse:
        """
        微信登录
        
        参数:
        - login_data: 微信登录数据
        - ip_address: 登录IP地址
        
        返回:
        - 登录响应
        
        异常:
        - ValueError: 微信授权失败或用户创建失败
        """
        logger.info(f"微信登录请求 - code: {login_data.code[:10]}...")

        # 通过code获取微信用户信息
        wechat_info = WechatUtils.get_user_info_by_code(login_data.code)
        if not wechat_info:
            self._create_login_log(None, "wechat", ip_address, False, "微信授权失败")
            raise ValueError("微信授权失败")

        openid = wechat_info.get("openid")
        user = self._get_user_by_wechat_openid(openid)

        if user:
            # 已绑定用户，直接登录
            if not user.is_active:
                self._create_login_log(user.id, "wechat", ip_address, False, "账户已被禁用")
                raise ValueError("账户已被禁用")
            
            # 更新微信信息
            self._update_wechat_binding(user.id, wechat_info)
        else:
            # 新用户，创建账户
            user = self._create_user_from_wechat(wechat_info)

        self._update_login_info(user, ip_address, "wechat")
        access_token = AuthUtils.create_access_token({"sub": str(user.id), "username": user.username})

        logger.info(f"微信登录成功 - user_id: {user.id}")
        return LoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=AuthUtils.get_token_expires_in(),
            user=UserProfile.model_validate(user)
        )

    # ==================== 验证码相关 ====================

    def send_verification_code(
        self, 
        send_data: SendCodeRequest, 
        ip_address: str
    ) -> bool:
        """
        发送验证码
        
        参数:
        - send_data: 发送验证码数据
        - ip_address: 请求IP地址
        
        返回:
        - 是否发送成功
        
        异常:
        - ValueError: 发送频率过高或其他错误
        """
        logger.info(f"发送验证码请求 - phone_or_email: {send_data.phone_or_email}, type: {send_data.code_type}")

        # 检查发送频率
        if not self._check_code_send_frequency(send_data.phone_or_email, send_data.code_type):
            raise ValueError("发送验证码过于频繁，请稍后再试")

        # 生成验证码
        code = VerificationCodeUtils.generate_code()
        
        # 保存验证码
        verification_code = VerificationCode(
            phone_or_email=send_data.phone_or_email,
            code=code,
            code_type=send_data.code_type.value,
            ip_address=ip_address
        )
        
        self.db.add(verification_code)
        
        # 发送验证码
        if self._send_code_via_sms_or_email(send_data.phone_or_email, code, send_data.code_type):
            self.db.commit()
            logger.info(f"验证码发送成功 - phone_or_email: {send_data.phone_or_email}")
            return True
        else:
            self.db.rollback()
            logger.error(f"验证码发送失败 - phone_or_email: {send_data.phone_or_email}")
            raise ValueError("验证码发送失败")

    def verify_code(
        self, 
        phone_or_email: str, 
        code: str, 
        code_type: CodeType
    ) -> bool:
        """
        验证验证码
        
        参数:
        - phone_or_email: 手机号或邮箱
        - code: 验证码
        - code_type: 验证码类型
        
        返回:
        - 验证是否成功
        """
        # 查找有效的验证码
        verification_code = self.db.query(VerificationCode).filter(
            and_(
                VerificationCode.phone_or_email == phone_or_email,
                VerificationCode.code == code,
                VerificationCode.code_type == code_type.value,
                VerificationCode.is_used == False,
                VerificationCode.expires_at > datetime.now(UTC)
            )
        ).first()

        if verification_code:
            # 标记为已使用
            verification_code.is_used = True
            verification_code.used_at = datetime.now(UTC)
            self.db.commit()
            logger.info(f"验证码验证成功 - phone_or_email: {phone_or_email}")
            return True
        
        logger.warning(f"验证码验证失败 - phone_or_email: {phone_or_email}")
        return False

    def _check_code_send_frequency(self, phone_or_email: str, code_type: CodeType) -> bool:
        """检查验证码发送频率"""
        # 检查1分钟内是否已发送
        one_minute_ago = datetime.now(UTC) - timedelta(minutes=1)
        recent_code = self.db.query(VerificationCode).filter(
            and_(
                VerificationCode.phone_or_email == phone_or_email,
                VerificationCode.code_type == code_type.value,
                VerificationCode.created_at > one_minute_ago
            )
        ).first()
        
        return recent_code is None

    def _send_code_via_sms_or_email(self, phone_or_email: str, code: str, code_type: CodeType) -> bool:
        """通过短信或邮件发送验证码"""
        # 这里应该集成实际的短信/邮件服务
        # 目前返回True表示发送成功
        logger.info(f"模拟发送验证码 - phone_or_email: {phone_or_email}, code: {code}")
        return True

    # ==================== 用户资料相关 ====================

    def get_user_profile(self, user_id: UUID) -> Optional[UserProfile]:
        """获取用户资料"""
        user = self.db.query(User).filter(User.id == user_id).first()
        return UserProfile.model_validate(user) if user else None

    def update_user_profile(
        self, 
        user_id: UUID, 
        update_data: UserUpdateRequest
    ) -> Optional[UserProfile]:
        """
        更新用户资料
        
        参数:
        - user_id: 用户ID
        - update_data: 更新数据
        
        返回:
        - 更新后的用户资料
        
        异常:
        - ValueError: 用户不存在或数据冲突
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        # 检查邮箱是否被其他用户占用
        if update_data.email and update_data.email != user.email:
            existing_user = self._get_user_by_email(update_data.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError(f"邮箱 '{update_data.email}' 已被其他用户使用")

        # 检查手机号是否被其他用户占用
        if update_data.phone and update_data.phone != user.phone:
            existing_user = self._get_user_by_phone(update_data.phone)
            if existing_user and existing_user.id != user_id:
                raise ValueError(f"手机号 '{update_data.phone}' 已被其他用户使用")

        # 更新用户信息
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        
        user.updated_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(user)

        logger.info(f"用户资料更新成功 - user_id: {user_id}")
        return UserProfile.model_validate(user)

    def change_password(
        self, 
        user_id: UUID, 
        change_data: ChangePasswordRequest
    ) -> bool:
        """
        修改密码
        
        参数:
        - user_id: 用户ID
        - change_data: 修改密码数据
        
        返回:
        - 是否修改成功
        
        异常:
        - ValueError: 用户不存在或旧密码错误
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        # 验证旧密码
        if not AuthUtils.verify_password(change_data.old_password, user.password_hash):
            raise ValueError("原密码错误")

        # 更新密码
        user.password_hash = AuthUtils.hash_password(change_data.new_password)
        user.updated_at = datetime.now(UTC)
        self.db.commit()

        logger.info(f"密码修改成功 - user_id: {user_id}")
        return True

    def reset_password(self, reset_data: ResetPasswordRequest) -> bool:
        """
        重置密码
        
        参数:
        - reset_data: 重置密码数据
        
        返回:
        - 是否重置成功
        
        异常:
        - ValueError: 用户不存在或验证码错误
        """
        # 验证验证码
        if not self.verify_code(reset_data.phone_or_email, reset_data.verification_code, CodeType.RESET_PASSWORD):
            raise ValueError("验证码无效或已过期")

        # 查找用户
        user = self._get_user_by_phone_or_email(reset_data.phone_or_email)
        if not user:
            raise ValueError("用户不存在")

        # 重置密码
        user.password_hash = AuthUtils.hash_password(reset_data.new_password)
        user.updated_at = datetime.now(UTC)
        self.db.commit()

        logger.info(f"密码重置成功 - user_id: {user.id}")
        return True

    # ==================== 微信相关 ====================

    def get_wechat_binding(self, user_id: UUID) -> Optional[WechatBindingInfo]:
        """获取微信绑定信息"""
        binding = self.db.query(WechatBinding).filter(WechatBinding.user_id == user_id).first()
        return WechatBindingInfo.model_validate(binding) if binding else None

    # ==================== 内部辅助方法 ====================

    def _update_login_info(self, user: User, ip_address: str, login_type: str = "username_password"):
        """更新用户登录信息"""
        user.login_count += 1
        user.last_login_at = datetime.now(UTC)
        user.last_login_ip = ip_address
        
        # 创建登录日志
        self._create_login_log(user.id, login_type, ip_address, True)
        
        self.db.commit()

    def _create_login_log(self, user_id: Optional[UUID], login_type: str, ip_address: str, is_success: bool = True, failure_reason: Optional[str] = None):
        """创建登录日志"""
        location = self._get_location_by_ip(ip_address)
        
        login_log = LoginLog(
            user_id=user_id,
            login_type=login_type,
            ip_address=ip_address,
            location=location,
            is_success=is_success,
            failure_reason=failure_reason
        )
        
        self.db.add(login_log)
        # 注意：这里不立即提交，由调用方控制事务

    def _get_location_by_ip(self, ip_address: str) -> Optional[str]:
        """根据IP地址获取地理位置"""
        try:
            return IPUtils.get_location(ip_address)
        except Exception as e:
            logger.warning(f"获取IP地理位置失败 - ip: {ip_address}, error: {e}")
            return None

    def _get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名查找用户"""
        return self.db.query(User).filter(User.username == username).first()

    def _get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱查找用户"""
        return self.db.query(User).filter(User.email == email).first()

    def _get_user_by_phone(self, phone: str) -> Optional[User]:
        """根据手机号查找用户"""
        return self.db.query(User).filter(User.phone == phone).first()

    def _get_user_by_username_or_email(self, username_or_email: str) -> Optional[User]:
        """根据用户名或邮箱查找用户"""
        return self.db.query(User).filter(
            or_(User.username == username_or_email, User.email == username_or_email)
        ).first()

    def _get_user_by_phone_or_email(self, phone_or_email: str) -> Optional[User]:
        """根据手机号或邮箱查找用户"""
        return self.db.query(User).filter(
            or_(User.phone == phone_or_email, User.email == phone_or_email)
        ).first()

    def _get_user_by_wechat_openid(self, openid: str) -> Optional[User]:
        """根据微信openid查找用户"""
        binding = self.db.query(WechatBinding).filter(WechatBinding.openid == openid).first()
        if binding:
            return self.db.query(User).filter(User.id == binding.user_id).first()
        return None

    def _create_user_from_wechat(self, wechat_info: Dict[str, Any]) -> User:
        """从微信信息创建用户"""
        openid = wechat_info.get("openid")
        nickname = wechat_info.get("nickname", f"微信用户_{openid[:8]}")
        
        # 生成唯一用户名
        username = f"wx_{openid[:16]}"
        counter = 1
        while self._get_user_by_username(username):
            username = f"wx_{openid[:16]}_{counter}"
            counter += 1

        # 创建用户
        user = User(
            username=username,
            email=f"{openid}@wechat.local",  # 临时邮箱
            password_hash=AuthUtils.hash_password(SecurityUtils.generate_random_password()),
            nickname=nickname,
            avatar_url=wechat_info.get("headimgurl"),
            is_verified=True,
            login_count=0
        )
        
        self.db.add(user)
        self.db.flush()  # 获取用户ID
        
        # 创建微信绑定
        self._bind_wechat_to_user(user.id, wechat_info)
        
        return user

    def _bind_wechat_to_user(self, user_id: UUID, wechat_info: Dict[str, Any]):
        """绑定微信到用户"""
        binding = WechatBinding(
            user_id=user_id,
            openid=wechat_info.get("openid"),
            unionid=wechat_info.get("unionid"),
            nickname=wechat_info.get("nickname"),
            avatar_url=wechat_info.get("headimgurl"),
            gender=wechat_info.get("sex"),
            country=wechat_info.get("country"),
            province=wechat_info.get("province"),
            city=wechat_info.get("city"),
            raw_data=wechat_info
        )
        
        self.db.add(binding)

    def _update_wechat_binding(self, user_id: UUID, wechat_info: Dict[str, Any]):
        """更新微信绑定信息"""
        binding = self.db.query(WechatBinding).filter(WechatBinding.user_id == user_id).first()
        if binding:
            binding.nickname = wechat_info.get("nickname", binding.nickname)
            binding.avatar_url = wechat_info.get("headimgurl", binding.avatar_url)
            binding.gender = wechat_info.get("sex", binding.gender)
            binding.country = wechat_info.get("country", binding.country)
            binding.province = wechat_info.get("province", binding.province)
            binding.city = wechat_info.get("city", binding.city)
            binding.raw_data = wechat_info
            binding.updated_at = datetime.now(UTC)