"""
认证相关工具类

包含JWT处理、密码哈希、验证码生成等认证相关的工具函数。
"""

import hashlib
import secrets
import random
import string
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any

import bcrypt
from jose import JWTError, jwt
from passlib.context import CryptContext

# JWT配置
import os
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")  # 生产环境必须从环境变量读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 默认24小时

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthUtils:
    """认证工具类"""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        生成密码哈希值
        
        使用bcrypt算法对密码进行哈希处理，确保密码安全存储。
        
        参数:
        - password: 明文密码
        
        返回:
        - 密码哈希值
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        对比明文密码和哈希密码是否匹配。
        
        参数:
        - plain_password: 明文密码
        - hashed_password: 哈希密码
        
        返回:
        - 密码是否匹配
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建JWT访问令牌
        
        生成包含用户信息的JWT令牌，用于API访问认证。
        
        参数:
        - data: 要编码的数据字典，通常包含用户ID等信息
        - expires_delta: 令牌过期时间，可选
        
        返回:
        - JWT令牌字符串
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
        """
        验证JWT访问令牌
        
        解码并验证JWT令牌的有效性。
        
        参数:
        - token: JWT令牌字符串
        
        返回:
        - 解码后的数据字典，验证失败返回None
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None

    @staticmethod
    def get_token_expires_in() -> int:
        """获取令牌过期时间（秒）"""
        return ACCESS_TOKEN_EXPIRE_MINUTES * 60


class VerificationCodeUtils:
    """验证码工具类"""

    @staticmethod
    def generate_numeric_code(length: int = 6) -> str:
        """
        生成数字验证码
        
        生成指定长度的随机数字验证码。
        
        参数:
        - length: 验证码长度，默认6位
        
        返回:
        - 数字验证码字符串
        """
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def generate_mixed_code(length: int = 8) -> str:
        """
        生成字母数字混合验证码
        
        生成包含大小写字母和数字的混合验证码。
        
        参数:
        - length: 验证码长度，默认8位
        
        返回:
        - 混合验证码字符串
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=length))

    @staticmethod
    def get_code_expires_at(minutes: int = 5) -> datetime:
        """
        获取验证码过期时间
        
        计算验证码的过期时间点。
        
        参数:
        - minutes: 有效时间（分钟），默认5分钟
        
        返回:
        - 过期时间
        """
        return datetime.now(UTC) + timedelta(minutes=minutes)


class SecurityUtils:
    """安全相关工具类"""

    @staticmethod
    def generate_random_string(length: int = 32) -> str:
        """
        生成随机字符串
        
        用于生成安全的随机字符串，如session ID等。
        
        参数:
        - length: 字符串长度，默认32位
        
        返回:
        - 随机字符串
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_string(text: str, salt: str = "") -> str:
        """
        计算字符串哈希值
        
        使用SHA256算法计算字符串的哈希值。
        
        参数:
        - text: 要哈希的文本
        - salt: 盐值，可选
        
        返回:
        - 哈希值
        """
        return hashlib.sha256((text + salt).encode()).hexdigest()

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        验证邮箱格式
        
        简单的邮箱格式验证。
        
        参数:
        - email: 邮箱地址
        
        返回:
        - 是否为有效邮箱格式
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """
        验证手机号格式
        
        验证中国大陆手机号格式。
        
        参数:
        - phone: 手机号码
        
        返回:
        - 是否为有效手机号格式
        """
        import re
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))


class WechatUtils:
    """微信相关工具类"""

    # 微信配置（生产环境应该从环境变量读取）
    WECHAT_APP_ID = "your_wechat_app_id"
    WECHAT_APP_SECRET = "your_wechat_app_secret"

    @staticmethod
    def exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
        """
        通过授权码获取微信访问令牌
        
        调用微信API，通过授权码换取访问令牌。
        
        参数:
        - code: 微信授权码
        
        返回:
        - 包含访问令牌和OpenID的字典，失败返回None
        """
        # TODO: 实现微信API调用
        # 这里需要实际调用微信的oauth2/access_token接口
        # 示例返回格式：
        return {
            "access_token": "mock_access_token",
            "expires_in": 7200,
            "refresh_token": "mock_refresh_token",
            "openid": "mock_openid",
            "scope": "snsapi_userinfo"
        }

    @staticmethod
    def get_user_info(access_token: str, openid: str) -> Optional[Dict[str, Any]]:
        """
        获取微信用户信息
        
        使用访问令牌获取微信用户的详细信息。
        
        参数:
        - access_token: 微信访问令牌
        - openid: 微信OpenID
        
        返回:
        - 用户信息字典，失败返回None
        """
        # TODO: 实现微信API调用
        # 这里需要实际调用微信的userinfo接口
        # 示例返回格式：
        return {
            "openid": openid,
            "nickname": "微信用户",
            "sex": 1,
            "province": "广东",
            "city": "深圳",
            "country": "中国",
            "headimgurl": "https://wx.qlogo.cn/mmopen/xxx",
            "unionid": "mock_unionid"
        }


class IPUtils:
    """IP地址相关工具类"""

    @staticmethod
    def get_client_ip(request) -> str:
        """
        获取客户端真实IP地址
        
        从HTTP请求中提取客户端的真实IP地址，考虑代理服务器的情况。
        
        参数:
        - request: FastAPI请求对象
        
        返回:
        - 客户端IP地址
        """
        # 优先从X-Forwarded-For头获取
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # 取第一个IP（客户端真实IP）
            return forwarded_for.split(",")[0].strip()
        
        # 从X-Real-IP头获取
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # 直接从连接信息获取
        return request.client.host if request.client else "127.0.0.1"

    @staticmethod
    def is_valid_ip(ip: str) -> bool:
        """
        验证IP地址格式
        
        验证IPv4地址格式是否正确。
        
        参数:
        - ip: IP地址字符串
        
        返回:
        - 是否为有效IP地址
        """
        import ipaddress
        try:
            ipaddress.IPv4Address(ip)
            return True
        except ipaddress.AddressValueError:
            return False 