"""
数据装饰器系统

提供自动化的测试数据创建、管理和清理功能。
"""

import uuid
import random
import string
from functools import wraps
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json

from ..clients.api import FluentAPIClient


@dataclass
class UserData:
    """用户数据"""
    id: Optional[str] = None
    username: str = ""
    email: str = ""
    password: str = "TestPass123456"
    nickname: str = "测试用户"
    phone: Optional[str] = None
    is_admin: bool = False
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "nickname": self.nickname,
            "phone": self.phone
        }


@dataclass
class CardData:
    """信用卡数据"""
    id: Optional[str] = None
    user_id: Optional[str] = None
    card_name: str = "测试信用卡"
    bank_name: str = "测试银行"
    card_number: str = ""
    credit_limit: float = 50000.00
    expiry_month: int = 12
    expiry_year: int = 2027
    billing_date: Optional[int] = 5
    due_date: Optional[int] = 25
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "card_name": self.card_name,
            "bank_name": self.bank_name,
            "card_number": self.card_number,
            "credit_limit": self.credit_limit,
            "expiry_month": self.expiry_month,
            "expiry_year": self.expiry_year,
            "billing_date": self.billing_date,
            "due_date": self.due_date
        }


@dataclass
class TransactionData:
    """交易数据"""
    id: Optional[str] = None
    card_id: Optional[str] = None
    transaction_type: str = "expense"
    amount: float = 100.00
    description: str = "测试交易"
    merchant_name: Optional[str] = "测试商户"
    transaction_date: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "card_id": self.card_id,
            "transaction_type": self.transaction_type,
            "amount": self.amount,
            "description": self.description,
            "merchant_name": self.merchant_name,
            "transaction_date": self.transaction_date or datetime.now().isoformat()
        }


class DataFactory:
    """数据工厂基类"""
    
    @staticmethod
    def random_string(length: int = 8) -> str:
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    @staticmethod
    def random_email(domain: str = "example.com") -> str:
        """生成随机邮箱"""
        return f"test_{DataFactory.random_string()}@{domain}"
    
    @staticmethod
    def random_phone() -> str:
        """生成随机手机号"""
        return f"138{random.randint(10000000, 99999999)}"
    
    @staticmethod
    def random_card_number() -> str:
        """生成随机卡号"""
        return f"6225{random.randint(100000000000, 999999999999)}"


class UserFactory(DataFactory):
    """用户数据工厂"""
    
    @classmethod
    def create(cls, **kwargs) -> UserData:
        """创建用户数据"""
        username = kwargs.get("username", f"testuser_{cls.random_string()}")
        email = kwargs.get("email", cls.random_email())
        
        user_data = UserData(
            username=username,
            email=email,
            password=kwargs.get("password", "TestPass123456"),
            nickname=kwargs.get("nickname", f"测试用户_{cls.random_string(4)}"),
            phone=kwargs.get("phone", cls.random_phone()),
            is_admin=kwargs.get("is_admin", False)
        )
        
        return user_data
    
    @classmethod
    def create_admin(cls, **kwargs) -> UserData:
        """创建管理员用户"""
        kwargs["is_admin"] = True
        kwargs["nickname"] = kwargs.get("nickname", "管理员")
        return cls.create(**kwargs)
    
    @classmethod
    def create_batch(cls, count: int, **kwargs) -> List[UserData]:
        """批量创建用户"""
        return [cls.create(**kwargs) for _ in range(count)]


class CardFactory(DataFactory):
    """信用卡数据工厂"""
    
    BANKS = [
        "招商银行", "工商银行", "建设银行", "农业银行", "中国银行", 
        "交通银行", "民生银行", "浦发银行", "兴业银行", "光大银行"
    ]
    
    CARD_NAMES = [
        "经典白金卡", "钻石卡", "金卡", "白金卡", "无限卡",
        "全币种卡", "联名卡", "商旅卡", "购物卡", "现金卡"
    ]
    
    @classmethod
    def create(cls, user_id: str = None, **kwargs) -> CardData:
        """创建信用卡数据"""
        bank_name = kwargs.get("bank_name", random.choice(cls.BANKS))
        card_name = kwargs.get("card_name", f"{bank_name}{random.choice(cls.CARD_NAMES)}")
        
        card_data = CardData(
            user_id=user_id,
            card_name=card_name,
            bank_name=bank_name,
            card_number=kwargs.get("card_number", cls.random_card_number()),
            credit_limit=kwargs.get("credit_limit", random.choice([10000, 20000, 50000, 100000, 200000])),
            expiry_month=kwargs.get("expiry_month", random.randint(1, 12)),
            expiry_year=kwargs.get("expiry_year", random.randint(2025, 2030)),
            billing_date=kwargs.get("billing_date", random.randint(1, 28)),
            due_date=kwargs.get("due_date", random.randint(1, 28))
        )
        
        return card_data
    
    @classmethod
    def create_batch(cls, count: int, user_id: str = None, **kwargs) -> List[CardData]:
        """批量创建信用卡"""
        return [cls.create(user_id=user_id, **kwargs) for _ in range(count)]
    
    @classmethod
    def create_high_limit_card(cls, user_id: str = None, **kwargs) -> CardData:
        """创建高额度信用卡"""
        kwargs["credit_limit"] = kwargs.get("credit_limit", 500000)
        kwargs["card_name"] = kwargs.get("card_name", "钻石无限卡")
        return cls.create(user_id=user_id, **kwargs)


class TransactionFactory(DataFactory):
    """交易数据工厂"""
    
    MERCHANTS = [
        "星巴克", "麦当劳", "肯德基", "必胜客", "海底捞",
        "超市发", "华联超市", "永辉超市", "家乐福", "沃尔玛",
        "中石油", "中石化", "招商银行", "工商银行", "支付宝",
        "京东", "淘宝", "天猫", "拼多多", "美团"
    ]
    
    DESCRIPTIONS = [
        "餐饮消费", "购物消费", "加油消费", "交通出行", "娱乐消费",
        "教育培训", "医疗保健", "生活服务", "旅游住宿", "网络购物"
    ]
    
    @classmethod
    def create(cls, card_id: str = None, **kwargs) -> TransactionData:
        """创建交易数据"""
        transaction_data = TransactionData(
            card_id=card_id,
            transaction_type=kwargs.get("transaction_type", "expense"),
            amount=kwargs.get("amount", round(random.uniform(10, 5000), 2)),
            description=kwargs.get("description", random.choice(cls.DESCRIPTIONS)),
            merchant_name=kwargs.get("merchant_name", random.choice(cls.MERCHANTS)),
            transaction_date=kwargs.get("transaction_date", 
                (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
            )
        )
        
        return transaction_data
    
    @classmethod
    def create_batch(cls, count: int, card_id: str = None, **kwargs) -> List[TransactionData]:
        """批量创建交易"""
        return [cls.create(card_id=card_id, **kwargs) for _ in range(count)]
    
    @classmethod
    def create_large_transaction(cls, card_id: str = None, **kwargs) -> TransactionData:
        """创建大额交易"""
        kwargs["amount"] = kwargs.get("amount", random.uniform(10000, 50000))
        kwargs["description"] = kwargs.get("description", "大额消费")
        return cls.create(card_id=card_id, **kwargs)


class DataManager:
    """数据管理器"""
    
    def __init__(self, api_client: FluentAPIClient):
        self.api_client = api_client
        self.created_users: List[UserData] = []
        self.created_cards: List[CardData] = []
        self.created_transactions: List[TransactionData] = []
        self.cleanup_hooks: List[Callable] = []
    
    def create_user(self, user_data: UserData = None, auto_login: bool = True) -> UserData:
        """创建并注册用户"""
        if user_data is None:
            user_data = UserFactory.create()
        
        # 注册用户
        response = self.api_client.register_user(user_data.to_dict())
        response.succeed()
        
        # 获取用户ID
        if response.data and "data" in response.data:
            user_data.id = response.data["data"].get("id")
        
        # 自动登录
        if auto_login:
            login_response = self.api_client.login_user(user_data.username, user_data.password)
            login_response.succeed()
            
            if login_response.data and "data" in login_response.data:
                user_data.access_token = login_response.data["data"].get("access_token")
                user_data.refresh_token = login_response.data["data"].get("refresh_token")
        
        self.created_users.append(user_data)
        print(f"✅ 创建用户: {user_data.username}")
        
        return user_data
    
    def create_card(self, card_data: CardData = None, user: UserData = None) -> CardData:
        """创建信用卡"""
        if card_data is None:
            card_data = CardFactory.create()
        
        if user:
            card_data.user_id = user.id
            # 设置用户认证
            if user.access_token:
                self.api_client.set_auth(user.access_token)
        
        # 创建信用卡
        response = self.api_client.create_card(card_data.to_dict())
        response.succeed()
        
        # 获取卡片ID
        if response.data and "data" in response.data:
            card_data.id = response.data["data"].get("id")
        
        self.created_cards.append(card_data)
        print(f"✅ 创建信用卡: {card_data.card_name}")
        
        return card_data
    
    def create_transaction(self, transaction_data: TransactionData = None, card: CardData = None) -> TransactionData:
        """创建交易记录"""
        if transaction_data is None:
            transaction_data = TransactionFactory.create()
        
        if card:
            transaction_data.card_id = card.id
        
        # 创建交易
        response = self.api_client.create_transaction(transaction_data.to_dict())
        response.succeed()
        
        # 获取交易ID
        if response.data and "data" in response.data:
            transaction_data.id = response.data["data"].get("id")
        
        self.created_transactions.append(transaction_data)
        print(f"✅ 创建交易: {transaction_data.description} (¥{transaction_data.amount})")
        
        return transaction_data
    
    def cleanup_all(self):
        """清理所有创建的数据"""
        print("🧹 开始清理测试数据...")
        
        # 执行自定义清理钩子
        for hook in self.cleanup_hooks:
            try:
                hook()
            except Exception as e:
                print(f"⚠️ 清理钩子执行失败: {e}")
        
        # 清理事务记录
        for transaction in self.created_transactions:
            if transaction.id:
                try:
                    self.api_client.delete(f"/api/v1/user/transactions/{transaction.id}/delete")
                    print(f"🗑️ 删除交易: {transaction.id}")
                except:
                    pass
        
        # 清理信用卡
        for card in self.created_cards:
            if card.id:
                try:
                    self.api_client.delete(f"/api/v1/user/cards/{card.id}/delete")
                    print(f"🗑️ 删除信用卡: {card.id}")
                except:
                    pass
        
        # 清理用户
        for user in self.created_users:
            if user.id:
                try:
                    # 设置用户认证后删除账户
                    if user.access_token:
                        self.api_client.set_auth(user.access_token)
                    self.api_client.delete("/api/v1/user/profile/account")
                    print(f"🗑️ 删除用户: {user.username}")
                except:
                    pass
        
        # 清空记录
        self.created_users.clear()
        self.created_cards.clear()
        self.created_transactions.clear()
        self.cleanup_hooks.clear()
        
        print("✅ 测试数据清理完成")
    
    def add_cleanup_hook(self, hook: Callable):
        """添加清理钩子"""
        self.cleanup_hooks.append(hook)


# 装饰器实现
def with_user(username: str = None, auto_login: bool = True, **user_kwargs):
    """用户数据装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取或创建API客户端
            api_client = kwargs.get("api") or FluentAPIClient()
            data_manager = DataManager(api_client)
            
            # 创建用户数据
            user_data = UserFactory.create(username=username, **user_kwargs)
            user = data_manager.create_user(user_data, auto_login=auto_login)
            
            # 注入参数
            kwargs["api"] = api_client
            kwargs["user"] = user
            kwargs["data_manager"] = data_manager
            
            try:
                return func(*args, **kwargs)
            finally:
                # 自动清理
                data_manager.cleanup_all()
        
        return wrapper
    return decorator


def with_cards(count: int = 1, **card_kwargs):
    """信用卡数据装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = kwargs.get("user")
            data_manager = kwargs.get("data_manager")
            
            if not user or not data_manager:
                raise ValueError("with_cards 装饰器需要 with_user 装饰器配合使用")
            
            # 创建信用卡
            cards = []
            for _ in range(count):
                card_data = CardFactory.create(**card_kwargs)
                card = data_manager.create_card(card_data, user)
                cards.append(card)
            
            # 注入参数
            if count == 1:
                kwargs["card"] = cards[0]
            else:
                kwargs["cards"] = cards
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def with_transactions(count: int = 1, **transaction_kwargs):
    """交易数据装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            card = kwargs.get("card")
            cards = kwargs.get("cards")
            data_manager = kwargs.get("data_manager")
            
            if not data_manager:
                raise ValueError("with_transactions 装饰器需要 with_user 装饰器配合使用")
            
            if not card and not cards:
                raise ValueError("with_transactions 装饰器需要 with_cards 装饰器配合使用")
            
            # 选择信用卡
            target_card = card or (cards[0] if cards else None)
            
            # 创建交易记录
            transactions = []
            for _ in range(count):
                transaction_data = TransactionFactory.create(**transaction_kwargs)
                transaction = data_manager.create_transaction(transaction_data, target_card)
                transactions.append(transaction)
            
            # 注入参数
            if count == 1:
                kwargs["transaction"] = transactions[0]
            else:
                kwargs["transactions"] = transactions
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def with_user_and_cards(card_count: int = 1, username: str = None, **kwargs):
    """用户和信用卡组合装饰器"""
    def decorator(func):
        # 分离用户和卡片参数
        user_kwargs = {k: v for k, v in kwargs.items() if k in ["password", "nickname", "phone", "is_admin"]}
        card_kwargs = {k: v for k, v in kwargs.items() if k not in user_kwargs}
        
        # 应用装饰器链
        decorated = with_transactions(0)(func) if "transactions" in func.__code__.co_varnames else func
        decorated = with_cards(card_count, **card_kwargs)(decorated)
        decorated = with_user(username, **user_kwargs)(decorated)
        
        return decorated
    return decorator


def with_test_data(users: int = 1, cards_per_user: int = 1, transactions_per_card: int = 0):
    """完整测试数据装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            api_client = kwargs.get("api") or FluentAPIClient()
            data_manager = DataManager(api_client)
            
            # 创建用户、信用卡和交易的完整数据集
            all_users = []
            all_cards = []
            all_transactions = []
            
            for i in range(users):
                # 创建用户
                user_data = UserFactory.create()
                user = data_manager.create_user(user_data)
                all_users.append(user)
                
                # 为用户创建信用卡
                user_cards = []
                for j in range(cards_per_user):
                    card_data = CardFactory.create()
                    card = data_manager.create_card(card_data, user)
                    user_cards.append(card)
                    all_cards.append(card)
                    
                    # 为信用卡创建交易
                    for k in range(transactions_per_card):
                        transaction_data = TransactionFactory.create()
                        transaction = data_manager.create_transaction(transaction_data, card)
                        all_transactions.append(transaction)
            
            # 注入参数
            kwargs["api"] = api_client
            kwargs["data_manager"] = data_manager
            kwargs["users"] = all_users
            kwargs["cards"] = all_cards
            kwargs["transactions"] = all_transactions
            
            if users == 1:
                kwargs["user"] = all_users[0]
            if cards_per_user == 1 and users == 1:
                kwargs["card"] = all_cards[0]
            
            try:
                return func(*args, **kwargs)
            finally:
                # 自动清理
                data_manager.cleanup_all()
        
        return wrapper
    return decorator 