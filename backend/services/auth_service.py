"""
用户认证服务层

包含用户注册、登录、验证码管理等业务逻辑。
"""

import logging
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any, Tuple, List
from uuid import UUID

from sqlalchemy import and_, or_
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
    CodeType,
    WechatBindingInfo
)
from utils.auth import (
    AuthUtils,
    VerificationCodeUtils,
    SecurityUtils,
    WechatUtils,
    IPUtils
)

logger = logging.getLogger(__name__)


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
        user_data = {
            "username": register_data.username,
            "email": register_data.email,
            "password_hash": AuthUtils.hash_password(register_data.password),
            "phone": register_data.phone,
            "nickname": register_data.nickname or register_data.username,
            "is_verified": bool(register_data.phone and register_data.verification_code),
            "login_count": "0"
        }

        user = self._create_user_db(user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

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
            raise ValueError("用户不存在")

        # 验证密码
        if not AuthUtils.verify_password(login_data.password, user.password_hash):
            raise ValueError("密码错误")

        # 检查用户状态
        if not user.is_active:
            raise ValueError("账户已被禁用")

        # 更新登录信息
        self._update_login_info(user, ip_address)

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
            raise ValueError("手机号未注册")

        if not AuthUtils.verify_password(login_data.password, user.password_hash):
            raise ValueError("密码错误")

        if not user.is_active:
            raise ValueError("账户已被禁用")

        self._update_login_info(user, ip_address)
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
        - ValueError: 验证码错误或手机号未注册
        """
        logger.info(f"手机号验证码登录请求 - phone: {login_data.phone}")

        # 验证验证码
        if not self.verify_code(login_data.phone, login_data.verification_code, CodeType.LOGIN):
            raise ValueError("验证码无效或已过期")

        # 查找用户，如果不存在则自动注册
        user = self._get_user_by_phone(login_data.phone)
        if not user:
            # 自动注册用户
            user_data = {
                "username": f"user_{login_data.phone}",
                "email": f"{login_data.phone}@temp.com",  # 临时邮箱，后续可以修改
                "password_hash": AuthUtils.hash_password(SecurityUtils.generate_random_string(16)),
                "phone": login_data.phone,
                "nickname": f"用户{login_data.phone[-4:]}",
                "is_verified": True,
                "login_count": "0"
            }
            user = self._create_user_db(user_data)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"自动注册新用户 - user_id: {user.id}, phone: {login_data.phone}")

        if not user.is_active:
            raise ValueError("账户已被禁用")

        self._update_login_info(user, ip_address)
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
        - ValueError: 微信授权失败
        """
        logger.info(f"微信登录请求 - code: {login_data.code[:10]}...")

        # 通过微信授权码获取用户信息
        wechat_info = WechatUtils.exchange_code_for_token(login_data.code)
        if not wechat_info:
            raise ValueError("微信授权失败")

        # 查找是否已绑定用户
        user = self._get_user_by_wechat_openid(wechat_info["openid"])
        
        if user:
            # 已绑定用户，直接登录
            if not user.is_active:
                raise ValueError("账户已被禁用")
                
            self._update_login_info(user, ip_address)
            # 更新微信绑定信息
            self._update_wechat_binding(user.id, wechat_info)
        else:
            # 未绑定用户，创建新用户
            user = self._create_user_from_wechat(wechat_info, login_data.user_info)
            self._update_login_info(user, ip_address)

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
        - 发送是否成功
        
        异常:
        - ValueError: 发送频率过高
        """
        logger.info(f"发送验证码请求 - {send_data.phone_or_email}, 类型: {send_data.code_type}")

        # 检查发送频率
        if self._check_code_send_frequency(send_data.phone_or_email, send_data.code_type):
            raise ValueError("验证码发送过于频繁，请稍后再试")

        # 生成验证码
        code = VerificationCodeUtils.generate_numeric_code()
        expires_at = VerificationCodeUtils.get_code_expires_at()

        # 保存验证码
        code_data = {
            "phone_or_email": send_data.phone_or_email,
            "code": code,
            "code_type": send_data.code_type.value,
            "expires_at": expires_at,
            "ip_address": ip_address
        }

        verification_code = self._create_verification_code_db(code_data)
        self.db.add(verification_code)
        self.db.commit()

        # 发送验证码
        success = self._send_code_via_sms_or_email(send_data.phone_or_email, code, send_data.code_type)
        
        if success:
            logger.info(f"验证码发送成功 - {send_data.phone_or_email}")
        else:
            logger.error(f"验证码发送失败 - {send_data.phone_or_email}")
            
        return success

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
        verification_code = self.db.query(self._get_verification_code_model()).filter(
            and_(
                self._get_verification_code_model().phone_or_email == phone_or_email,
                self._get_verification_code_model().code == code,
                self._get_verification_code_model().code_type == code_type.value,
                self._get_verification_code_model().is_used == False,
                self._get_verification_code_model().expires_at > datetime.now(UTC)
            )
        ).first()

        if verification_code:
            # 标记为已使用
            verification_code.is_used = True
            self.db.commit()
            return True
        
        return False

    def _check_code_send_frequency(self, phone_or_email: str, code_type: CodeType) -> bool:
        """检查验证码发送频率"""
        one_minute_ago = datetime.now(UTC) - timedelta(minutes=1)
        recent_code = self.db.query(self._get_verification_code_model()).filter(
            and_(
                self._get_verification_code_model().phone_or_email == phone_or_email,
                self._get_verification_code_model().code_type == code_type.value,
                self._get_verification_code_model().created_at > one_minute_ago
            )
        ).first()
        return bool(recent_code)

    def _send_code_via_sms_or_email(self, phone_or_email: str, code: str, code_type: CodeType) -> bool:
        """通过短信或邮件发送验证码"""
        # TODO: 集成实际的短信/邮件服务
        logger.info(f"模拟发送验证码 - {phone_or_email}: {code} (类型: {code_type.value})")
        return True

    # ==================== 用户信息管理 ====================

    def get_user_profile(self, user_id: UUID) -> Optional[UserProfile]:
        """获取用户资料"""
        user = self.db.query(self._get_user_model()).filter(
            self._get_user_model().id == user_id
        ).first()
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
        """
        user = self.db.query(self._get_user_model()).filter(
            self._get_user_model().id == user_id
        ).first()
        
        if not user:
            return None

        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

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
        - change_data: 密码修改数据
        
        返回:
        - 修改是否成功
        
        异常:
        - ValueError: 当前密码错误
        """
        user = self.db.query(self._get_user_model()).filter(
            self._get_user_model().id == user_id
        ).first()
        
        if not user:
            return False

        # 验证当前密码
        if not AuthUtils.verify_password(change_data.old_password, user.password_hash):
            raise ValueError("当前密码错误")

        # 更新密码
        user.password_hash = AuthUtils.hash_password(change_data.new_password)
        self.db.commit()
        
        logger.info(f"密码修改成功 - user_id: {user_id}")
        return True

    def reset_password(self, reset_data: ResetPasswordRequest) -> bool:
        """
        重置密码
        
        参数:
        - reset_data: 重置密码数据
        
        返回:
        - 重置是否成功
        
        异常:
        - ValueError: 验证码错误或用户不存在
        """
        # 验证验证码
        if not self.verify_code(
            reset_data.phone_or_email, 
            reset_data.verification_code, 
            CodeType.RESET_PASSWORD
        ):
            raise ValueError("验证码无效或已过期")

        # 查找用户
        user = self._get_user_by_phone_or_email(reset_data.phone_or_email)
        if not user:
            raise ValueError("用户不存在")

        # 更新密码
        user.password_hash = AuthUtils.hash_password(reset_data.new_password)
        self.db.commit()
        
        logger.info(f"密码重置成功 - user_id: {user.id}")
        return True

    # ==================== 微信相关 ====================

    def get_wechat_binding(self, user_id: UUID) -> Optional[WechatBindingInfo]:
        """获取用户微信绑定信息"""
        binding = self.db.query(self._get_wechat_binding_model()).filter(
            self._get_wechat_binding_model().user_id == user_id
        ).first()
        return WechatBindingInfo.model_validate(binding) if binding else None

    # ==================== 辅助方法 ====================

    def _update_login_info(self, user, ip_address: str):
        """更新登录信息"""
        user.last_login_at = datetime.now(UTC)
        user.last_login_ip = ip_address
        user.login_count = str(int(user.login_count or "0") + 1)
        self.db.commit()

    def _get_user_by_username(self, username: str):
        """通过用户名查找用户"""
        return self.db.query(self._get_user_model()).filter(
            self._get_user_model().username == username
        ).first()

    def _get_user_by_email(self, email: str):
        """通过邮箱查找用户"""
        return self.db.query(self._get_user_model()).filter(
            self._get_user_model().email == email
        ).first()

    def _get_user_by_phone(self, phone: str):
        """通过手机号查找用户"""
        return self.db.query(self._get_user_model()).filter(
            self._get_user_model().phone == phone
        ).first()

    def _get_user_by_username_or_email(self, username_or_email: str):
        """通过用户名或邮箱查找用户"""
        return self.db.query(self._get_user_model()).filter(
            or_(
                self._get_user_model().username == username_or_email,
                self._get_user_model().email == username_or_email
            )
        ).first()

    def _get_user_by_phone_or_email(self, phone_or_email: str):
        """通过手机号或邮箱查找用户"""
        return self.db.query(self._get_user_model()).filter(
            or_(
                self._get_user_model().phone == phone_or_email,
                self._get_user_model().email == phone_or_email
            )
        ).first()

    def _get_user_by_wechat_openid(self, openid: str):
        """通过微信OpenID查找用户"""
        binding = self.db.query(self._get_wechat_binding_model()).filter(
            self._get_wechat_binding_model().openid == openid
        ).first()
        
        if binding:
            return self.db.query(self._get_user_model()).filter(
                self._get_user_model().id == binding.user_id
            ).first()
        return None

    def _create_user_from_wechat(self, wechat_info: Dict[str, Any], user_info: Optional[Dict] = None):
        """从微信信息创建用户"""
        nickname = wechat_info.get("nickname", "微信用户")
        if user_info and "nickname" in user_info:
            nickname = user_info["nickname"]

        user_data = {
            "username": f"wx_{wechat_info['openid'][:16]}",
            "email": f"{wechat_info['openid'][:16]}@wechat.temp",
            "password_hash": AuthUtils.hash_password(SecurityUtils.generate_random_string(16)),
            "nickname": nickname,
            "avatar_url": wechat_info.get("headimgurl"),
            "is_verified": True,
            "login_count": "0"
        }
        
        user = self._create_user_db(user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def _bind_wechat_to_user(self, user_id: UUID, wechat_info: Dict[str, Any]):
        """绑定微信到用户"""
        binding_data = {
            "user_id": user_id,
            "openid": wechat_info["openid"],
            "unionid": wechat_info.get("unionid"),
            "nickname": wechat_info.get("nickname"),
            "avatar_url": wechat_info.get("headimgurl"),
            "sex": "male" if wechat_info.get("sex") == 1 else "female" if wechat_info.get("sex") == 2 else "unknown",
            "country": wechat_info.get("country"),
            "province": wechat_info.get("province"),
            "city": wechat_info.get("city")
        }
        
        binding = self._create_wechat_binding_db(binding_data)
        self.db.add(binding)
        self.db.commit()

    def _update_wechat_binding(self, user_id: UUID, wechat_info: Dict[str, Any]):
        """更新微信绑定信息"""
        binding = self.db.query(self._get_wechat_binding_model()).filter(
            self._get_wechat_binding_model().user_id == user_id
        ).first()
        
        if binding:
            binding.nickname = wechat_info.get("nickname", binding.nickname)
            binding.avatar_url = wechat_info.get("headimgurl", binding.avatar_url)
            self.db.commit()

    # 数据库模型相关方法的实际实现
    def _create_user_db(self, user_data: Dict[str, Any]):
        """创建用户数据库对象"""
        from db_models.users import User
        return User(**user_data)

    def _create_verification_code_db(self, code_data: Dict[str, Any]):
        """创建验证码数据库对象"""
        from db_models.users import VerificationCode
        return VerificationCode(**code_data)

    def _create_wechat_binding_db(self, binding_data: Dict[str, Any]):
        """创建微信绑定数据库对象"""
        from db_models.users import WechatBinding
        return WechatBinding(**binding_data)

    def _get_user_model(self):
        """获取用户数据库模型"""
        from db_models.users import User
        return User

    def _get_verification_code_model(self):
        """获取验证码数据库模型"""
        from db_models.users import VerificationCode
        return VerificationCode

    def _get_wechat_binding_model(self):
        """获取微信绑定数据库模型"""
        from db_models.users import WechatBinding
        return WechatBinding 