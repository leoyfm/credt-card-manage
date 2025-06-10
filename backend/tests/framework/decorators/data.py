"""
数据装饰器

提供自动数据准备和清理功能，让测试专注于业务逻辑验证。

Usage:
    @with_user
    @with_cards(count=3, bank="招商银行")
    def test_user_cards(self, api, user, cards):
        # 数据会自动创建和清理
        pass
"""

import functools
import logging
from typing import Dict, Any, Callable, Optional, List, Union
from uuid import uuid4
import random

logger = logging.getLogger(__name__)


class DataCleaner:
    """数据清理器"""
    
    cleanup_stack = []
    
    @classmethod
    def add_cleanup(cls, cleanup_func: Callable):
        """添加清理函数"""
        cls.cleanup_stack.append(cleanup_func)
    
    @classmethod
    def cleanup_all(cls):
        """执行所有清理"""
        while cls.cleanup_stack:
            cleanup_func = cls.cleanup_stack.pop()
            try:
                cleanup_func()
            except Exception as e:
                logger.warning(f"数据清理失败: {e}")
    
    @classmethod
    def cleanup_user(cls, user_id: str):
        """清理用户相关数据"""
        # 这里应该调用实际的清理API
        logger.info(f"清理用户数据: {user_id}")


class TestUser:
    """测试用户对象"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id")
        self.username = data.get("username")
        self.email = data.get("email")
        self.password = data.get("password")
        self.nickname = data.get("nickname")
        self.token = data.get("token")
        self.raw_data = data
    
    def __repr__(self):
        return f"TestUser(id={self.id}, username={self.username})"


class TestCard:
    """测试信用卡对象"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id")
        self.card_name = data.get("card_name")
        self.bank_name = data.get("bank_name")
        self.card_number = data.get("card_number")
        self.credit_limit = data.get("credit_limit")
        self.raw_data = data
    
    def __repr__(self):
        return f"TestCard(id={self.id}, name={self.card_name})"


class TestTransaction:
    """测试交易对象"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id")
        self.card_id = data.get("card_id")
        self.amount = data.get("amount")
        self.transaction_type = data.get("transaction_type")
        self.merchant_name = data.get("merchant_name")
        self.raw_data = data
    
    def __repr__(self):
        return f"TestTransaction(id={self.id}, amount={self.amount})"


def with_user(username: str = None, **user_kwargs):
    """
    自动创建用户装饰器
    
    自动注册用户、登录并设置认证信息。
    
    Args:
        username: 指定用户名（可选）
        **user_kwargs: 其他用户属性
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            api = kwargs.get('api')
            if not api:
                raise ValueError("with_user装饰器需要api客户端，请先使用@api_test装饰器")
            
            # 生成唯一用户数据
            unique_id = uuid4().hex[:8]
            user_data = {
                "username": username or f"testuser_{unique_id}",
                "email": f"test_{unique_id}@example.com",
                "password": "TestPass123456",
                "nickname": f"测试用户_{unique_id}",
                **user_kwargs
            }
            
            try:
                # 注册用户
                register_response = api.post("/api/v1/public/auth/register", data=user_data)
                register_response.should.succeed()
                
                # 登录获取token
                login_response = api.post("/api/v1/public/auth/login/username", data={
                    "username": user_data["username"],
                    "password": user_data["password"]
                })
                login_response.should.succeed()
                
                # 设置认证信息
                token_data = login_response.data
                api.set_auth(token_data["access_token"])
                
                # 创建用户对象
                user_info = token_data.get("user", {})
                user = TestUser({
                    **user_data,
                    **user_info,
                    "token": token_data["access_token"]
                })
                
                # 注入用户对象
                kwargs['user'] = user
                
                logger.info(f"✅ 创建测试用户: {user.username}")
                
                # 添加清理函数
                DataCleaner.add_cleanup(lambda: DataCleaner.cleanup_user(user.id))
                
                return func(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"创建用户失败: {e}")
                raise
        
        wrapper._creates_user = True
        return wrapper
    
    return decorator


def with_cards(count: int = 1, **card_kwargs):
    """
    自动创建信用卡装饰器
    
    Args:
        count: 创建卡片数量
        **card_kwargs: 卡片属性
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            api = kwargs.get('api')
            user = kwargs.get('user')
            
            if not api or not user:
                raise ValueError("with_cards装饰器需要api和user，请先使用@api_test和@with_user装饰器")
            
            cards = []
            banks = ["招商银行", "工商银行", "建设银行", "农业银行", "中国银行"]
            
            for i in range(count):
                card_data = {
                    "card_name": f"测试信用卡{i+1}",
                    "bank_name": card_kwargs.get("bank", random.choice(banks)),
                    "card_number": f"6225{random.randint(100000000000, 999999999999)}",
                    "card_type": "visa",
                    "credit_limit": 50000.00,
                    "expiry_month": 12,
                    "expiry_year": 2027,
                    "billing_day": random.randint(1, 28),
                    "due_day": random.randint(1, 28),
                    "used_amount": 0.0,
                    "annual_fee_enabled": False,
                    **{k: v for k, v in card_kwargs.items() if k != "bank"}
                }
                
                # 创建信用卡
                response = api.post("/api/v1/user/cards/create", data=card_data)
                response.should.succeed()
                
                card = TestCard(response.data)
                cards.append(card)
                
                logger.info(f"✅ 创建测试信用卡: {card.card_name}")
            
            # 注入卡片对象
            if count == 1:
                kwargs['card'] = cards[0]
            else:
                kwargs['cards'] = cards
            
            return func(*args, **kwargs)
        
        wrapper._creates_cards = True
        wrapper._card_count = count
        return wrapper
    
    return decorator


def with_transactions(count: int = 10, card_index: int = 0, **transaction_kwargs):
    """
    自动创建交易记录装饰器
    
    Args:
        count: 交易记录数量
        card_index: 使用的卡片索引
        **transaction_kwargs: 交易属性
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            api = kwargs.get('api')
            cards = kwargs.get('cards') or [kwargs.get('card')]
            
            if not api or not cards or not cards[0]:
                raise ValueError("with_transactions装饰器需要api和cards，请先使用相关装饰器")
            
            # 选择卡片
            if card_index >= len(cards):
                card_index_to_use = 0
            else:
                card_index_to_use = card_index
            
            target_card = cards[card_index_to_use]
            transactions = []
            
            merchants = ["超市", "餐厅", "加油站", "商场", "网购", "咖啡店"]
            categories = ["dining", "shopping", "gas", "grocery", "entertainment"]
            
            for i in range(count):
                transaction_data = {
                    "card_id": target_card.id,
                    "transaction_type": "expense",
                    "amount": round(random.uniform(10, 1000), 2),
                    "transaction_date": "2024-06-08T14:30:00",
                    "merchant_name": random.choice(merchants),
                    "description": f"测试交易{i+1}",
                    "category": random.choice(categories),
                    "status": "completed",
                    "points_earned": 10.0,
                    "points_rate": 1.0,
                    "reference_number": f"TEST{uuid4().hex[:8]}",
                    "location": "测试地点",
                    "is_installment": False,
                    **transaction_kwargs
                }
                
                # 创建交易记录
                response = api.post("/api/v1/user/transactions/create", data=transaction_data)
                response.should.succeed()
                
                transaction = TestTransaction(response.data)
                transactions.append(transaction)
            
            # 注入交易对象
            kwargs['transactions'] = transactions
            
            logger.info(f"✅ 创建{count}条测试交易记录")
            
            return func(*args, **kwargs)
        
        wrapper._creates_transactions = True
        wrapper._transaction_count = count
        return wrapper
    
    return decorator


def with_data(data_spec: Dict[str, Any]):
    """
    复杂数据创建装饰器
    
    支持创建复杂的数据关系。
    
    Args:
        data_spec: 数据规格定义
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            api = kwargs.get('api')
            if not api:
                raise ValueError("with_data装饰器需要api客户端")
            
            # 解析数据规格并创建数据
            created_data = {}
            
            for key, spec in data_spec.items():
                if key == "user":
                    # 创建用户
                    user_data = _create_user_data(spec)
                    user = _register_and_login_user(api, user_data)
                    created_data[key] = user
                    kwargs['user'] = user
                
                elif key == "cards":
                    # 创建信用卡
                    user = created_data.get("user") or kwargs.get("user")
                    if not user:
                        raise ValueError("创建信用卡需要先创建用户")
                    
                    cards = _create_cards(api, spec)
                    created_data[key] = cards
                    kwargs['cards'] = cards
                
                elif key == "transactions":
                    # 创建交易记录
                    cards = created_data.get("cards") or kwargs.get("cards")
                    if not cards:
                        raise ValueError("创建交易记录需要先创建信用卡")
                    
                    transactions = _create_transactions(api, cards[0], spec)
                    created_data[key] = transactions
                    kwargs['transactions'] = transactions
            
            # 注入数据对象
            kwargs['data'] = type('Data', (), created_data)
            
            return func(*args, **kwargs)
        
        wrapper._creates_data = True
        wrapper._data_spec = data_spec
        return wrapper
    
    return decorator


def with_admin_user(func):
    """
    创建管理员用户装饰器
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        api = kwargs.get('api')
        if not api:
            raise ValueError("with_admin_user装饰器需要api客户端")
        
        # 创建管理员用户
        admin_data = {
            "username": f"admin_{uuid4().hex[:8]}",
            "email": f"admin_{uuid4().hex[:8]}@example.com",
            "password": "AdminPass123456",
            "nickname": "管理员",
            "is_admin": True
        }
        
        # 注册和登录流程
        register_response = api.post("/api/v1/public/auth/register", data=admin_data)
        register_response.should.succeed()
        
        login_response = api.post("/api/v1/public/auth/login/username", data={
            "username": admin_data["username"],
            "password": admin_data["password"]
        })
        login_response.should.succeed()
        
        # 设置认证
        token_data = login_response.data
        api.set_auth(token_data["access_token"])
        
        admin = TestUser({
            **admin_data,
            **token_data.get("user", {}),
            "token": token_data["access_token"]
        })
        
        kwargs['admin'] = admin
        
        logger.info(f"✅ 创建管理员用户: {admin.username}")
        
        return func(*args, **kwargs)
    
    wrapper._creates_admin = True
    return wrapper


def cleanup_after(func):
    """
    自动清理装饰器
    
    测试完成后自动清理所有创建的数据。
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            DataCleaner.cleanup_all()
    
    return wrapper


# 辅助函数

def _create_user_data(spec):
    """创建用户数据"""
    if isinstance(spec, dict):
        return {
            "username": spec.get("username", f"user_{uuid4().hex[:8]}"),
            "email": spec.get("email", f"test_{uuid4().hex[:8]}@example.com"),
            "password": spec.get("password", "TestPass123456"),
            "nickname": spec.get("nickname", "测试用户"),
            **{k: v for k, v in spec.items() if k not in ["username", "email", "password", "nickname"]}
        }
    else:
        return {
            "username": f"user_{uuid4().hex[:8]}",
            "email": f"test_{uuid4().hex[:8]}@example.com",
            "password": "TestPass123456",
            "nickname": "测试用户"
        }


def _register_and_login_user(api, user_data):
    """注册并登录用户"""
    # 注册
    register_response = api.post("/api/v1/public/auth/register", data=user_data)
    register_response.should.succeed()
    
    # 登录
    login_response = api.post("/api/v1/public/auth/login/username", data={
        "username": user_data["username"],
        "password": user_data["password"]
    })
    login_response.should.succeed()
    
    # 设置认证
    token_data = login_response.data
    api.set_auth(token_data["access_token"])
    
    return TestUser({
        **user_data,
        **token_data.get("user", {}),
        "token": token_data["access_token"]
    })


def _create_cards(api, spec):
    """创建信用卡"""
    if isinstance(spec, dict):
        count = spec.get("count", 1)
        card_data = {k: v for k, v in spec.items() if k != "count"}
    else:
        count = spec if isinstance(spec, int) else 1
        card_data = {}
    
    cards = []
    for i in range(count):
        card_info = {
            "card_name": f"测试信用卡{i+1}",
            "bank_name": "测试银行",
            "card_number": f"6225{random.randint(100000000000, 999999999999)}",
            "card_type": "visa",
            "credit_limit": 50000.00,
            "expiry_month": 12,
            "expiry_year": 2027,
            **card_data
        }
        
        response = api.post("/api/v1/user/cards/create", data=card_info)
        response.should.succeed()
        
        cards.append(TestCard(response.data))
    
    return cards


def _create_transactions(api, card, spec):
    """创建交易记录"""
    if isinstance(spec, dict):
        count = spec.get("count", 10)
        transaction_data = {k: v for k, v in spec.items() if k != "count"}
    else:
        count = spec if isinstance(spec, int) else 10
        transaction_data = {}
    
    transactions = []
    for i in range(count):
        transaction_info = {
            "card_id": card.id,
            "transaction_type": "expense",
            "amount": round(random.uniform(10, 1000), 2),
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "测试商户",
            "description": f"测试交易{i+1}",
            "category": "dining",
            **transaction_data
        }
        
        response = api.post("/api/v1/user/transactions/create", data=transaction_info)
        response.should.succeed()
        
        transactions.append(TestTransaction(response.data))
    
    return transactions 