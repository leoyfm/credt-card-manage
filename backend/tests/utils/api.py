"""
API测试客户端
"""
import requests
from typing import Optional, Dict, Any
import json


class APIClient:
    """API测试客户端"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
    
    def set_auth(self, token: str):
        """设置认证令牌"""
        self.headers["Authorization"] = f"Bearer {token}"
    
    def get(self, url: str, params: Optional[Dict] = None):
        """GET请求"""
        return requests.get(
            f"{self.base_url}{url}",
            headers=self.headers,
            params=params
        )
    
    def post(self, url: str, data: Optional[Dict] = None):
        """POST请求"""
        return requests.post(
            f"{self.base_url}{url}",
            headers=self.headers,
            json=data
        )
    
    def put(self, url: str, data: Optional[Dict] = None):
        """PUT请求"""
        return requests.put(
            f"{self.base_url}{url}",
            headers=self.headers,
            json=data
        )
    
    def delete(self, url: str, data: Optional[Dict] = None):
        """DELETE请求"""
        return requests.delete(
            f"{self.base_url}{url}",
            headers=self.headers,
            json=data
        )
    
    def patch(self, url: str, data: Optional[Dict] = None):
        """PATCH请求"""
        return requests.patch(
            f"{self.base_url}{url}",
            headers=self.headers,
            json=data
        )

    def _parse(self, resp):
        try:
            return resp.json()
        except Exception:
            return None 