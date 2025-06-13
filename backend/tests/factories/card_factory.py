import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import random


def build_card(**kwargs) -> Dict[str, Any]:
    """构建信用卡测试数据
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 信用卡数据字典
    """
    # 生成随机卡号（测试用）
    card_number = kwargs.get("card_number") or f"4111111111{random.randint(100000, 999999)}"
    
    # 随机选择银行
    banks = ["招商银行", "建设银行", "工商银行", "农业银行", "中国银行", "交通银行", "浦发银行", "民生银行"]
    bank_name = kwargs.get("bank_name") or random.choice(banks)
    
    # 生成卡片名称
    card_types = ["经典白金卡", "钻石卡", "金卡", "普卡", "无限卡"]
    card_type = random.choice(card_types)
    card_name = kwargs.get("card_name") or f"{bank_name}{card_type}"
    
    # 生成有效期（未来1-5年）
    future_years = random.randint(1, 5)
    expiry_date = datetime.now() + timedelta(days=365 * future_years)
    expiry_month = kwargs.get("expiry_month") or expiry_date.month
    expiry_year = kwargs.get("expiry_year") or expiry_date.year
    
    # 生成账单日和还款日
    billing_date = kwargs.get("billing_date") or random.randint(1, 28)
    due_date = kwargs.get("due_date") or (billing_date + 20) % 28 + 1
    
    return {
        "card_number": card_number,
        "card_name": card_name,
        "bank_name": bank_name,
        "card_type": kwargs.get("card_type", "credit"),
        "card_network": kwargs.get("card_network") or random.choice(["VISA", "MasterCard", "银联"]),
        "card_level": kwargs.get("card_level") or random.choice(["普卡", "金卡", "白金卡", "钻石卡"]),
        "credit_limit": kwargs.get("credit_limit", Decimal("50000.00")),
        "available_limit": kwargs.get("available_limit", Decimal("45000.00")),
        "used_limit": kwargs.get("used_limit", Decimal("5000.00")),
        "expiry_month": expiry_month,
        "expiry_year": expiry_year,
        "billing_date": billing_date,
        "due_date": due_date,
        "annual_fee": kwargs.get("annual_fee", Decimal("200.00")),
        "fee_waivable": kwargs.get("fee_waivable", True),
        "fee_auto_deduct": kwargs.get("fee_auto_deduct", False),
        "fee_due_month": kwargs.get("fee_due_month", random.randint(1, 12)),
        "features": kwargs.get("features", ["积分返现", "机场贵宾厅", "免费洗车"]),
        "points_rate": kwargs.get("points_rate", Decimal("1.00")),
        "cashback_rate": kwargs.get("cashback_rate", Decimal("0.01")),
        "status": kwargs.get("status", "active"),
        "is_primary": kwargs.get("is_primary", False),
        "notes": kwargs.get("notes", "测试信用卡")
    }


def build_simple_card(**kwargs) -> Dict[str, Any]:
    """构建简单的信用卡数据（只包含必需字段）
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 简化的信用卡数据字典
    """
    card_number = kwargs.get("card_number") or f"4111111111{random.randint(100000, 999999)}"
    
    return {
        "card_number": card_number,
        "card_name": kwargs.get("card_name", f"测试卡_{uuid.uuid4().hex[:8]}"),
        "bank_name": kwargs.get("bank_name", "测试银行"),
        "credit_limit": kwargs.get("credit_limit", Decimal("10000.00")),
        "expiry_month": kwargs.get("expiry_month", 12),
        "expiry_year": kwargs.get("expiry_year", 2027)
    }


def build_premium_card(**kwargs) -> Dict[str, Any]:
    """构建高端信用卡数据
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 高端信用卡数据字典
    """
    base_card = build_card(**kwargs)
    
    # 高端卡特有属性
    premium_features = [
        "无限额度", "全球机场贵宾厅", "专属客服", "高端酒店权益", 
        "米其林餐厅优惠", "私人银行服务", "全球紧急救援"
    ]
    
    base_card.update({
        "card_level": kwargs.get("card_level", "无限卡"),
        "credit_limit": kwargs.get("credit_limit", Decimal("1000000.00")),
        "annual_fee": kwargs.get("annual_fee", Decimal("3600.00")),
        "points_rate": kwargs.get("points_rate", Decimal("2.00")),
        "cashback_rate": kwargs.get("cashback_rate", Decimal("0.02")),
        "features": kwargs.get("features", premium_features)
    })
    
    return base_card


def build_expired_card(**kwargs) -> Dict[str, Any]:
    """构建已过期的信用卡数据
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 已过期的信用卡数据字典
    """
    base_card = build_card(**kwargs)
    
    # 设置为已过期
    past_date = datetime.now() - timedelta(days=365)
    base_card.update({
        "expiry_month": kwargs.get("expiry_month", past_date.month),
        "expiry_year": kwargs.get("expiry_year", past_date.year),
        "status": kwargs.get("status", "closed")
    })
    
    return base_card


def build_cards_batch(count: int = 3, **kwargs) -> list[Dict[str, Any]]:
    """批量构建信用卡数据
    
    Args:
        count: 要生成的卡片数量
        **kwargs: 可选的覆盖参数
        
    Returns:
        list[Dict[str, Any]]: 信用卡数据列表
    """
    cards = []
    for i in range(count):
        card_kwargs = kwargs.copy()
        # 确保每张卡的卡号不同
        if "card_number" not in card_kwargs:
            card_kwargs["card_number"] = f"4111111111{random.randint(100000, 999999)}"
        # 第一张卡设为主卡
        if i == 0:
            card_kwargs["is_primary"] = True
        cards.append(build_card(**card_kwargs))
    
    return cards


# 预定义的测试卡片模板
CARD_TEMPLATES = {
    "招商经典白金": {
        "bank_name": "招商银行",
        "card_name": "招商银行经典白金卡",
        "card_level": "白金卡",
        "card_network": "VISA",
        "credit_limit": Decimal("100000.00"),
        "annual_fee": Decimal("580.00"),
        "points_rate": Decimal("1.00"),
        "features": ["积分永久有效", "机场贵宾厅", "道路救援"]
    },
    "建行龙卡": {
        "bank_name": "建设银行",
        "card_name": "建设银行龙卡信用卡",
        "card_level": "金卡",
        "card_network": "银联",
        "credit_limit": Decimal("50000.00"),
        "annual_fee": Decimal("200.00"),
        "points_rate": Decimal("1.00"),
        "features": ["积分兑换", "分期免息", "消费返现"]
    },
    "浦发AE白": {
        "bank_name": "浦发银行",
        "card_name": "浦发银行AE白金卡",
        "card_level": "白金卡",
        "card_network": "American Express",
        "credit_limit": Decimal("200000.00"),
        "annual_fee": Decimal("3600.00"),
        "points_rate": Decimal("1.50"),
        "features": ["全球机场贵宾厅", "酒店升房", "租车优惠", "高端餐厅优惠"]
    }
}


def build_template_card(template_name: str, **kwargs) -> Dict[str, Any]:
    """根据模板构建信用卡数据
    
    Args:
        template_name: 模板名称
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 信用卡数据字典
        
    Raises:
        ValueError: 当模板不存在时
    """
    if template_name not in CARD_TEMPLATES:
        raise ValueError(f"未知的卡片模板: {template_name}，可用模板: {list(CARD_TEMPLATES.keys())}")
    
    template = CARD_TEMPLATES[template_name].copy()
    template.update(kwargs)
    
    return build_card(**template) 