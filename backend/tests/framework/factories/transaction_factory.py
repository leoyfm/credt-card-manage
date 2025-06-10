"""交易数据工厂

自动生成测试交易数据
"""

import random
from datetime import datetime, timedelta
from decimal import Decimal
from .base import DataFactory, random_amount


class TransactionFactory(DataFactory):
    """交易数据工厂"""
    
    def __init__(self):
        super().__init__()
        
        self.defaults = {
            "transaction_type": "expense",
            "amount": lambda: Decimal(str(random_amount(10.0, 1000.0))),
            "currency": "CNY",
            "description": lambda: random.choice([
                "超市购物", "餐厅用餐", "加油站", "网上购物", 
                "电影票", "咖啡厅", "药店", "书店",
                "健身房", "打车", "外卖", "便利店"
            ]),
            "merchant_name": lambda: random.choice([
                "沃尔玛", "家乐福", "星巴克", "麦当劳",
                "中石化", "滴滴出行", "美团", "淘宝",
                "京东", "苹果商店", "优衣库", "华为商城"
            ]),
            "merchant_category": lambda: random.choice([
                "超市", "餐饮", "加油", "网购",
                "娱乐", "交通", "服装", "数码",
                "医疗", "教育", "旅行", "其他"
            ]),
            "location": lambda: random.choice([
                "北京市朝阳区", "上海市浦东新区", "深圳市南山区",
                "广州市天河区", "杭州市西湖区", "成都市武侯区",
                "南京市鼓楼区", "武汉市洪山区", "西安市雁塔区"
            ]),
            "points_earned": lambda: random.randint(1, 50),
            "cashback_earned": lambda: Decimal(str(random.uniform(0.1, 10.0))),
            "status": "completed",
            "transaction_date": lambda: self._random_recent_date(),
            "tags": lambda: random.sample([
                "餐饮", "购物", "交通", "娱乐", "生活",
                "工作", "旅行", "健康", "教育", "投资"
            ], k=random.randint(0, 3))
        }
        
        self.traits = {
            "large_amount": {
                "amount": lambda: Decimal(str(random_amount(5000.0, 50000.0))),
                "description": "大额消费",
                "merchant_category": "购物",
                "points_earned": lambda: random.randint(100, 500)
            },
            "small_amount": {
                "amount": lambda: Decimal(str(random_amount(1.0, 50.0))),
                "description": "小额消费",
                "merchant_category": "便利店",
                "points_earned": lambda: random.randint(1, 5)
            },
            "dining": {
                "merchant_category": "餐饮",
                "description": lambda: random.choice(["中餐", "西餐", "快餐", "咖啡"]),
                "merchant_name": lambda: random.choice([
                    "麦当劳", "肯德基", "星巴克", "海底捞",
                    "西贝", "外婆家", "绿茶", "太二"
                ]),
                "tags": ["餐饮", "生活"]
            },
            "shopping": {
                "merchant_category": "购物",
                "description": "网上购物",
                "merchant_name": lambda: random.choice([
                    "淘宝", "京东", "天猫", "苏宁",
                    "唯品会", "拼多多", "小红书", "得物"
                ]),
                "tags": ["购物", "网购"]
            },
            "travel": {
                "merchant_category": "交通",
                "description": lambda: random.choice([
                    "机票", "高铁票", "酒店", "打车",
                    "地铁", "公交", "租车", "停车"
                ]),
                "amount": lambda: Decimal(str(random_amount(50.0, 2000.0))),
                "tags": ["交通", "旅行"]
            },
            "income": {
                "transaction_type": "income",
                "amount": lambda: Decimal(str(random_amount(100.0, 5000.0))),
                "description": lambda: random.choice([
                    "工资", "奖金", "返现", "退款",
                    "投资收益", "兼职收入", "礼金"
                ]),
                "merchant_category": "收入",
                "points_earned": 0,
                "cashback_earned": Decimal("0")
            },
            "recent": {
                "transaction_date": lambda: datetime.now() - timedelta(days=random.randint(0, 7))
            },
            "last_month": {
                "transaction_date": lambda: datetime.now() - timedelta(days=random.randint(30, 60))
            },
            "failed": {
                "status": "failed",
                "description": "交易失败",
                "points_earned": 0,
                "cashback_earned": Decimal("0")
            }
        }
    
    def _random_recent_date(self):
        """生成最近的随机日期"""
        days_ago = random.randint(1, 90)
        return datetime.now() - timedelta(days=days_ago)
    
    def large_amount(self):
        """大额交易"""
        return self.with_trait("large_amount")
    
    def small_amount(self):
        """小额交易"""
        return self.with_trait("small_amount")
    
    def dining(self):
        """餐饮交易"""
        return self.with_trait("dining")
    
    def shopping(self):
        """购物交易"""
        return self.with_trait("shopping")
    
    def travel(self):
        """旅行交易"""
        return self.with_trait("travel")
    
    def income(self):
        """收入记录"""
        return self.with_trait("income")
    
    def recent(self):
        """最近交易"""
        return self.with_trait("recent")
    
    def last_month(self):
        """上月交易"""
        return self.with_trait("last_month")
    
    def failed(self):
        """失败交易"""
        return self.with_trait("failed")
    
    def for_card(self, card_id: str):
        """为特定信用卡创建交易"""
        factory = self.__class__()
        factory.defaults = {**self.defaults, "card_id": card_id}
        factory.traits = self.traits
        return factory 