"""信用卡数据工厂

自动生成测试信用卡数据
"""

import random
from decimal import Decimal
from .base import DataFactory, random_string, random_card_number


class CardFactory(DataFactory):
    """信用卡数据工厂"""
    
    def __init__(self):
        super().__init__()
        
        self.defaults = {
            "card_name": lambda: f"测试信用卡{random_string(4)}",
            "bank_name": "测试银行",
            "card_number": random_card_number,
            "card_type": "credit",
            "card_network": lambda: random.choice(["VISA", "MasterCard", "银联"]),
            "card_level": lambda: random.choice(["普卡", "金卡", "白金卡"]),
            "credit_limit": lambda: Decimal(str(random.choice([10000, 30000, 50000, 100000]))),
            "available_limit": lambda: self._calculate_available_limit(),
            "used_limit": Decimal("0"),
            "expiry_month": lambda: random.randint(1, 12),
            "expiry_year": lambda: random.randint(2025, 2030),
            "billing_date": lambda: random.randint(1, 28),
            "due_date": lambda: random.randint(1, 28),
            "annual_fee": Decimal("0"),
            "fee_waivable": True,
            "fee_auto_deduct": False,
            "points_rate": Decimal("1.00"),
            "cashback_rate": Decimal("0.01"),
            "status": "active",
            "is_primary": False
        }
        
        self.traits = {
            "high_limit": {
                "credit_limit": Decimal("200000"),
                "card_level": "钻石卡",
                "annual_fee": Decimal("2000"),
                "points_rate": Decimal("2.00")
            },
            "cmb": {
                "bank_name": "招商银行",
                "card_name": "招商银行信用卡",
                "card_network": "VISA"
            },
            "icbc": {
                "bank_name": "工商银行", 
                "card_name": "工商银行信用卡",
                "card_network": "银联"
            },
            "primary": {
                "is_primary": True,
                "card_name": "主信用卡"
            },
            "expired": {
                "expiry_month": 12,
                "expiry_year": 2023,
                "status": "frozen"
            },
            "with_fee": {
                "annual_fee": Decimal("680"),
                "fee_waivable": True,
                "fee_auto_deduct": True
            },
            "cashback": {
                "cashback_rate": Decimal("0.05"),
                "points_rate": Decimal("0.50"),
                "card_name": "返现信用卡"
            }
        }
    
    def _calculate_available_limit(self):
        """计算可用额度"""
        # 这里简化处理，实际创建时会重新计算
        return Decimal("0")
    
    def high_limit(self):
        """高额度信用卡"""
        return self.with_trait("high_limit")
    
    def cmb(self):
        """招商银行信用卡"""
        return self.with_trait("cmb")
    
    def icbc(self):
        """工商银行信用卡"""
        return self.with_trait("icbc")
    
    def primary(self):
        """主信用卡"""
        return self.with_trait("primary")
    
    def expired(self):
        """过期信用卡"""
        return self.with_trait("expired")
    
    def with_fee(self):
        """有年费信用卡"""
        return self.with_trait("with_fee")
    
    def cashback(self):
        """返现信用卡"""
        return self.with_trait("cashback")
    
    def for_user(self, user_id: str):
        """为特定用户创建信用卡"""
        factory = self.__class__()
        factory.defaults = {**self.defaults, "user_id": user_id}
        factory.traits = self.traits
        return factory 