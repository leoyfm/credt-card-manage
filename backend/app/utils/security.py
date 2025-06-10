"""
安全工具模块

提供安全相关的工具函数，如数据脱敏、输入验证等。
"""

import re
import hashlib
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, UTC

from app.core.logging import get_logger

logger = get_logger(__name__)


class SecurityUtils:
    """安全工具类"""
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """
        清理用户输入
        
        Args:
            text: 输入文本
            max_length: 最大长度
            
        Returns:
            清理后的文本
        """
        if not text:
            return ""
        
        # 移除危险字符
        text = re.sub(r'[<>"\']', '', text)
        
        # 限制长度
        if len(text) > max_length:
            text = text[:max_length]
        
        return text.strip()
    
    @staticmethod
    def mask_sensitive_data(data: str, mask_char: str = "*", show_first: int = 2, show_last: int = 2) -> str:
        """
        脱敏敏感数据
        
        Args:
            data: 原始数据
            mask_char: 脱敏字符
            show_first: 显示前几位
            show_last: 显示后几位
            
        Returns:
            脱敏后的数据
        """
        if not data or len(data) <= show_first + show_last:
            return data
        
        mask_length = len(data) - show_first - show_last
        return f"{data[:show_first]}{mask_char * mask_length}{data[-show_last:]}"
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """
        验证密码强度
        
        Args:
            password: 密码
            
        Returns:
            验证结果字典
        """
        result = {
            "is_valid": True,
            "score": 0,
            "issues": []
        }
        
        if len(password) < 8:
            result["issues"].append("密码长度至少8位")
            result["is_valid"] = False
        else:
            result["score"] += 1
        
        if not re.search(r'[a-z]', password):
            result["issues"].append("密码需包含小写字母")
            result["is_valid"] = False
        else:
            result["score"] += 1
        
        if not re.search(r'[A-Z]', password):
            result["issues"].append("密码需包含大写字母")
            result["is_valid"] = False
        else:
            result["score"] += 1
        
        if not re.search(r'\d', password):
            result["issues"].append("密码需包含数字")
            result["is_valid"] = False
        else:
            result["score"] += 1
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result["issues"].append("密码需包含特殊字符")
        else:
            result["score"] += 1
        
        return result
    
    @staticmethod
    def generate_csrf_token() -> str:
        """
        生成CSRF令牌
        
        Returns:
            CSRF令牌
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_session_id() -> str:
        """
        生成会话ID
        
        Returns:
            会话ID
        """
        return secrets.token_urlsafe(64)
    
    @staticmethod
    def hash_ip_address(ip: str) -> str:
        """
        哈希IP地址（用于隐私保护）
        
        Args:
            ip: IP地址
            
        Returns:
            哈希后的IP
        """
        return hashlib.sha256(ip.encode()).hexdigest()[:16]
    
    @staticmethod
    def is_safe_redirect_url(url: str, allowed_hosts: list = None) -> bool:
        """
        检查重定向URL是否安全
        
        Args:
            url: 重定向URL
            allowed_hosts: 允许的主机列表
            
        Returns:
            是否安全
        """
        if not url:
            return False
        
        # 检查是否为相对URL
        if url.startswith('/') and not url.startswith('//'):
            return True
        
        # 检查是否在允许的主机列表中
        if allowed_hosts:
            for host in allowed_hosts:
                if url.startswith(f"https://{host}") or url.startswith(f"http://{host}"):
                    return True
        
        return False
    
    @staticmethod
    def log_security_event(event_type: str, details: Dict[str, Any], ip_address: Optional[str] = None):
        """
        记录安全事件
        
        Args:
            event_type: 事件类型
            details: 事件详情
            ip_address: IP地址
        """
        log_data = {
            "event_type": event_type,
            "timestamp": datetime.now(UTC).isoformat(),
            "details": details
        }
        
        if ip_address:
            log_data["ip_hash"] = SecurityUtils.hash_ip_address(ip_address)
        
        logger.warning(f"安全事件: {event_type}", **log_data) 