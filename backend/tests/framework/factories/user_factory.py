"""用户数据工厂

自动生成测试用户数据
"""

import uuid
from .base import DataFactory, random_string, random_email, random_phone


class UserFactory(DataFactory):
    """用户数据工厂"""
    
    def __init__(self):
        super().__init__()
        
        self.defaults = {
            "username": lambda: f"user_{random_string(8)}",
            "email": random_email,
            "password": "TestPass123456",
            "nickname": lambda: f"测试用户{random_string(4)}",
            "phone": random_phone,
            "is_active": True,
            "is_verified": False,
            "is_admin": False,
            "timezone": "Asia/Shanghai",
            "language": "zh-CN",
            "currency": "CNY"
        }
        
        self.traits = {
            "admin": {
                "is_admin": True,
                "nickname": "管理员用户"
            },
            "verified": {
                "is_verified": True
            },
            "inactive": {
                "is_active": False
            },
            "vip": {
                "nickname": "VIP用户",
                "is_verified": True
            }
        }
    
    def admin(self):
        """创建管理员用户"""
        return self.with_trait("admin")
    
    def verified(self):
        """创建已验证用户"""
        return self.with_trait("verified")
    
    def inactive(self):
        """创建未激活用户"""
        return self.with_trait("inactive")
    
    def vip(self):
        """创建VIP用户"""
        return self.with_trait("vip")


class TestUserPool:
    """测试用户池"""
    
    def __init__(self, size: int = 10):
        self.size = size
        self.users = []
        self.factory = UserFactory()
    
    def create_pool(self):
        """创建用户池"""
        self.users = self.factory.create_batch(self.size)
        return self.users
    
    def get_random_user(self):
        """获取随机用户"""
        if not self.users:
            self.create_pool()
        import random
        return random.choice(self.users)
    
    def get_admin_user(self):
        """获取管理员用户"""
        admin_users = [u for u in self.users if u.get("is_admin")]
        if not admin_users:
            admin_user = self.factory.admin().create()
            self.users.append(admin_user)
            return admin_user
        return admin_users[0]
    
    def cleanup(self):
        """清理用户池"""
        self.users.clear()
        self.factory.cleanup() 