import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import random


def build_transaction(**kwargs) -> Dict[str, Any]:
    """构建交易记录测试数据
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 交易记录数据字典
    """
    # 随机交易金额
    amount = kwargs.get("amount") or str(Decimal(str(random.uniform(10.0, 5000.0))))
    
    # 随机商户
    merchants = [
        "星巴克咖啡", "麦当劳", "沃尔玛超市", "中石化加油站", "苹果专卖店",
        "京东商城", "淘宝网", "美团外卖", "滴滴出行", "携程旅行",
        "华为商城", "小米之家", "海底捞火锅", "必胜客", "肯德基"
    ]
    merchant_name = kwargs.get("merchant_name") or random.choice(merchants)
    
    # 随机交易分类
    categories = [
        "餐饮美食", "购物消费", "交通出行", "生活服务", "娱乐休闲",
        "医疗健康", "教育培训", "旅游住宿", "数码电器", "服装鞋帽"
    ]
    merchant_category = kwargs.get("merchant_category") or random.choice(categories)
    
    # 随机交易时间（最近30天内）
    days_ago = random.randint(0, 30)
    transaction_date = (datetime.now() - timedelta(days=days_ago)).isoformat()
    if "transaction_date" in kwargs:
        transaction_date = kwargs["transaction_date"]
    
    # 计算积分和返现
    points_earned = kwargs.get("points_earned") or int(float(amount))
    cashback_earned = kwargs.get("cashback_earned") or str(Decimal(amount) * Decimal("0.01"))
    
    return {
        "transaction_type": kwargs.get("transaction_type", "expense"),
        "amount": amount,
        "currency": kwargs.get("currency", "CNY"),
        "description": kwargs.get("description", f"在{merchant_name}消费"),
        "merchant_name": merchant_name,
        "merchant_category": merchant_category,
        "location": kwargs.get("location", "北京市朝阳区"),
        "points_earned": points_earned,
        "cashback_earned": cashback_earned,
        "status": kwargs.get("status", "completed"),
        "transaction_date": transaction_date,
        "notes": kwargs.get("notes", "测试交易记录"),
        "tags": kwargs.get("tags", [merchant_category])
    }


def build_simple_transaction(**kwargs) -> Dict[str, Any]:
    """构建简单的交易记录数据（只包含必需字段）
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 简化的交易记录数据字典
    """
    return {
        "transaction_type": kwargs.get("transaction_type", "expense"),
        "amount": str(kwargs.get("amount", Decimal("100.00"))),
        "description": kwargs.get("description", "测试交易"),
        "merchant_name": kwargs.get("merchant_name", "测试商户")
    }


def build_large_transaction(**kwargs) -> Dict[str, Any]:
    """构建大额交易数据
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 大额交易数据字典
    """
    base_transaction = build_transaction(**kwargs)
    
    # 大额交易特有属性
    large_merchants = [
        "苹果专卖店", "特斯拉汽车", "路易威登", "香奈儿", "劳力士专柜",
        "奔驰4S店", "宝马专卖店", "华为旗舰店", "戴森专卖店", "戴森专卖店"
    ]
    
    base_transaction.update({
        "amount": str(kwargs.get("amount", Decimal(str(random.uniform(5000.0, 50000.0))))),
        "merchant_name": kwargs.get("merchant_name") or random.choice(large_merchants),
        "merchant_category": kwargs.get("merchant_category", "奢侈品消费"),
        "points_earned": kwargs.get("points_earned") or int(float(base_transaction["amount"]) * 2),
        "cashback_earned": kwargs.get("cashback_earned") or str(Decimal(base_transaction["amount"]) * Decimal("0.02"))
    })
    
    return base_transaction


def build_refund_transaction(**kwargs) -> Dict[str, Any]:
    """构建退款交易数据
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 退款交易数据字典
    """
    base_transaction = build_transaction(**kwargs)
    
    base_transaction.update({
        "transaction_type": kwargs.get("transaction_type", "income"),
        "amount": str(kwargs.get("amount", Decimal("500.00"))),
        "description": kwargs.get("description", "退款"),
        "status": kwargs.get("status", "completed"),
        "points_earned": kwargs.get("points_earned", 0),
        "cashback_earned": str(kwargs.get("cashback_earned", Decimal("0.00")))
    })
    
    return base_transaction


def build_pending_transaction(**kwargs) -> Dict[str, Any]:
    """构建待处理交易数据
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 待处理交易数据字典
    """
    base_transaction = build_transaction(**kwargs)
    
    base_transaction.update({
        "status": kwargs.get("status", "pending"),
        "transaction_date": kwargs.get("transaction_date", datetime.now().isoformat()),
        "points_earned": kwargs.get("points_earned", 0),
        "cashback_earned": str(kwargs.get("cashback_earned", Decimal("0.00")))
    })
    
    return base_transaction


def build_transactions_batch(count: int = 5, **kwargs) -> list[Dict[str, Any]]:
    """批量构建交易记录数据
    
    Args:
        count: 要生成的交易数量
        **kwargs: 可选的覆盖参数
        
    Returns:
        list[Dict[str, Any]]: 交易记录数据列表
    """
    transactions = []
    for i in range(count):
        transaction_kwargs = kwargs.copy()
        # 确保交易时间有差异
        if "transaction_date" not in transaction_kwargs:
            days_ago = random.randint(0, 30)
            transaction_kwargs["transaction_date"] = (datetime.now() - timedelta(days=days_ago)).isoformat()
        transactions.append(build_transaction(**transaction_kwargs))
    
    return transactions


def build_monthly_transactions(year: int = None, month: int = None, count: int = 10, **kwargs) -> list[Dict[str, Any]]:
    """构建指定月份的交易记录
    
    Args:
        year: 年份，默认当前年
        month: 月份，默认当前月
        count: 交易数量
        **kwargs: 可选的覆盖参数
        
    Returns:
        list[Dict[str, Any]]: 指定月份的交易记录列表
    """
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    transactions = []
    for i in range(count):
        # 在指定月份内随机选择日期
        day = random.randint(1, 28)  # 使用28避免月份天数问题
        hour = random.randint(8, 22)
        minute = random.randint(0, 59)
        
        transaction_date = datetime(year, month, day, hour, minute).isoformat()
        
        transaction_kwargs = kwargs.copy()
        transaction_kwargs["transaction_date"] = transaction_date
        
        transactions.append(build_transaction(**transaction_kwargs))
    
    return transactions


# 预定义的交易模板
TRANSACTION_TEMPLATES = {
    "餐饮": {
        "merchant_category": "餐饮美食",
        "amount": "88.00",
        "merchant_name": "海底捞火锅",
        "description": "晚餐消费",
        "points_earned": 88,
        "cashback_earned": "0.88"
    },
    "加油": {
        "merchant_category": "交通出行",
        "amount": "300.00",
        "merchant_name": "中石化加油站",
        "description": "汽油费",
        "points_earned": 600,  # 加油双倍积分
        "cashback_earned": "3.00"
    },
    "购物": {
        "merchant_category": "购物消费",
        "amount": "1288.00",
        "merchant_name": "苹果专卖店",
        "description": "购买iPhone配件",
        "points_earned": 1288,
        "cashback_earned": "12.88"
    },
    "旅行": {
        "merchant_category": "旅游住宿",
        "amount": "2580.00",
        "merchant_name": "携程旅行",
        "description": "机票预订",
        "points_earned": 5160,  # 旅行双倍积分
        "cashback_earned": "25.80"
    }
}


def build_template_transaction(template_name: str, **kwargs) -> Dict[str, Any]:
    """根据模板构建交易数据
    
    Args:
        template_name: 模板名称
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 交易数据字典
        
    Raises:
        ValueError: 当模板不存在时
    """
    if template_name not in TRANSACTION_TEMPLATES:
        raise ValueError(f"未知的交易模板: {template_name}，可用模板: {list(TRANSACTION_TEMPLATES.keys())}")
    
    template = TRANSACTION_TEMPLATES[template_name].copy()
    template.update(kwargs)
    
    return build_transaction(**template) 