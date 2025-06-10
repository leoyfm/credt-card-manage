"""
认证工具模块

提供密码哈希、JWT令牌生成等认证相关的工具函数。
"""

import hashlib
import secrets
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, Optional
import jwt
from passlib.context import CryptContext

from app.core.config import settings

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthUtils:
    """认证工具类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        哈希密码
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        Args:
            plain_password: 明文密码
            hashed_password: 哈希密码
            
        Returns:
            密码是否匹配
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        创建访问令牌
        
        Args:
            data: 要编码的数据
            expires_delta: 过期时间增量
            
        Returns:
            JWT访问令牌
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """
        验证令牌
        
        Args:
            token: JWT令牌
            
        Returns:
            解码后的数据，验证失败返回None
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None
    
    @staticmethod
    def get_token_expires_in() -> int:
        """
        获取令牌过期时间（秒）
        
        Returns:
            过期时间秒数
        """
        return settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    @staticmethod
    def generate_random_string(length: int = 32) -> str:
        """
        生成随机字符串
        
        Args:
            length: 字符串长度
            
        Returns:
            随机字符串
        """
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """
        生成验证码
        
        Args:
            length: 验证码长度
            
        Returns:
            数字验证码
        """
        return ''.join([str(secrets.randbelow(10)) for _ in range(length)])
    
    @staticmethod
    def hash_string(text: str) -> str:
        """
        哈希字符串（用于生成唯一标识）
        
        Args:
            text: 要哈希的文本
            
        Returns:
            SHA256哈希值
        """
        return hashlib.sha256(text.encode()).hexdigest() 