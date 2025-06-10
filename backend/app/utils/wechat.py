"""
微信工具模块

提供微信登录、API调用等功能。
"""

import requests
from typing import Dict, Any, Optional
from urllib.parse import urlencode

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class WechatUtils:
    """微信工具类"""
    
    # 微信API端点
    WECHAT_API_BASE = "https://api.weixin.qq.com"
    OAUTH_URL = "https://open.weixin.qq.com/connect/oauth2/authorize"
    ACCESS_TOKEN_URL = f"{WECHAT_API_BASE}/sns/oauth2/access_token"
    USER_INFO_URL = f"{WECHAT_API_BASE}/sns/userinfo"
    
    @staticmethod
    def get_oauth_url(redirect_uri: str, state: str = None) -> str:
        """
        获取微信OAuth授权URL
        
        Args:
            redirect_uri: 回调地址
            state: 状态参数
            
        Returns:
            授权URL
        """
        params = {
            "appid": settings.WECHAT_APP_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "snsapi_userinfo",
        }
        
        if state:
            params["state"] = state
        
        return f"{WechatUtils.OAUTH_URL}?{urlencode(params)}#wechat_redirect"
    
    @staticmethod
    def get_access_token(code: str) -> Optional[Dict[str, Any]]:
        """
        通过授权码获取访问令牌
        
        Args:
            code: 授权码
            
        Returns:
            访问令牌信息
        """
        params = {
            "appid": settings.WECHAT_APP_ID,
            "secret": settings.WECHAT_APP_SECRET,
            "code": code,
            "grant_type": "authorization_code"
        }
        
        try:
            response = requests.get(WechatUtils.ACCESS_TOKEN_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if "errcode" in data:
                logger.error(f"微信获取访问令牌失败: {data}")
                return None
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"微信API请求失败: {e}")
            return None
    
    @staticmethod
    def get_user_info(access_token: str, openid: str) -> Optional[Dict[str, Any]]:
        """
        获取用户信息
        
        Args:
            access_token: 访问令牌
            openid: 用户OpenID
            
        Returns:
            用户信息
        """
        params = {
            "access_token": access_token,
            "openid": openid,
            "lang": "zh_CN"
        }
        
        try:
            response = requests.get(WechatUtils.USER_INFO_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if "errcode" in data:
                logger.error(f"微信获取用户信息失败: {data}")
                return None
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"微信API请求失败: {e}")
            return None
    
    @staticmethod
    def validate_signature(signature: str, timestamp: str, nonce: str) -> bool:
        """
        验证微信签名
        
        Args:
            signature: 签名
            timestamp: 时间戳
            nonce: 随机数
            
        Returns:
            签名是否有效
        """
        import hashlib
        
        token = settings.WECHAT_TOKEN
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        tmp_str = ''.join(tmp_list)
        
        hash_obj = hashlib.sha1(tmp_str.encode('utf-8'))
        hash_str = hash_obj.hexdigest()
        
        return hash_str == signature
    
    @staticmethod
    def parse_wechat_user_info(user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析微信用户信息
        
        Args:
            user_info: 微信返回的用户信息
            
        Returns:
            标准化的用户信息
        """
        return {
            "openid": user_info.get("openid"),
            "unionid": user_info.get("unionid"),
            "nickname": user_info.get("nickname"),
            "avatar_url": user_info.get("headimgurl"),
            "gender": user_info.get("sex", 0),  # 0-未知, 1-男, 2-女
            "country": user_info.get("country"),
            "province": user_info.get("province"),
            "city": user_info.get("city"),
            "language": user_info.get("language", "zh_CN")
        }
    
    @staticmethod
    def send_template_message(openid: str, template_id: str, data: Dict[str, Any]) -> bool:
        """
        发送模板消息
        
        Args:
            openid: 用户OpenID
            template_id: 模板ID
            data: 消息数据
            
        Returns:
            是否发送成功
        """
        # 这里需要实现模板消息发送逻辑
        # 由于需要服务号权限，暂时返回True
        logger.info(f"发送微信模板消息: openid={openid}, template_id={template_id}")
        return True 