"""
年费减免规则和年费记录测试数据工厂

提供用于测试的年费相关数据构建函数
"""

import uuid
from decimal import Decimal
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional, List
import random


def build_fee_waiver_rule(**kwargs) -> Dict[str, Any]:
    """构建年费减免规则测试数据
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 年费减免规则数据字典
    """
    current_year = datetime.now().year
    
    return {
        "card_id": kwargs.get("card_id", str(uuid.uuid4())),
        "fee_year": kwargs.get("fee_year", current_year),
        "base_fee": str(kwargs.get("base_fee", Decimal("300.00"))),
        "waiver_type": kwargs.get("waiver_type", "spending_amount"),
        "waiver_condition_value": str(kwargs.get("waiver_condition_value", Decimal("50000.00"))),
        "waiver_condition_unit": kwargs.get("waiver_condition_unit", "元"),
        "points_per_yuan": str(kwargs.get("points_per_yuan", Decimal("1.00"))),
        "is_active": kwargs.get("is_active", True),
        "notes": kwargs.get("notes", "测试年费减免规则")
    }


def build_spending_rule(**kwargs) -> Dict[str, Any]:
    """构建消费金额减免规则"""
    base_rule = build_fee_waiver_rule(**kwargs)
    base_rule.update({
        "waiver_type": "spending_amount",
        "waiver_condition_value": str(kwargs.get("waiver_condition_value", Decimal("50000.00"))),
        "waiver_condition_unit": kwargs.get("waiver_condition_unit", "元"),
        "notes": kwargs.get("notes", "年消费满5万元免年费")
    })
    return base_rule


def build_transaction_count_rule(**kwargs) -> Dict[str, Any]:
    """构建交易次数减免规则"""
    base_rule = build_fee_waiver_rule(**kwargs)
    base_rule.update({
        "waiver_type": "transaction_count",
        "waiver_condition_value": str(kwargs.get("waiver_condition_value", Decimal("100"))),
        "waiver_condition_unit": kwargs.get("waiver_condition_unit", "笔"),
        "notes": kwargs.get("notes", "年交易满100笔免年费")
    })
    return base_rule


def build_points_redemption_rule(**kwargs) -> Dict[str, Any]:
    """构建积分兑换减免规则"""
    base_rule = build_fee_waiver_rule(**kwargs)
    base_rule.update({
        "waiver_type": "points_redemption",
        "waiver_condition_value": str(kwargs.get("waiver_condition_value", Decimal("20000"))),
        "waiver_condition_unit": kwargs.get("waiver_condition_unit", "积分"),
        "notes": kwargs.get("notes", "2万积分兑换年费")
    })
    return base_rule


def build_rigid_rule(**kwargs) -> Dict[str, Any]:
    """构建刚性减免规则（无条件减免）"""
    base_rule = build_fee_waiver_rule(**kwargs)
    base_rule.update({
        "waiver_type": "rigid",
        "waiver_condition_value": None,
        "waiver_condition_unit": None,
        "notes": kwargs.get("notes", "无条件免年费")
    })
    return base_rule


def build_annual_fee_record(**kwargs) -> Dict[str, Any]:
    """构建年费记录测试数据"""
    current_year = datetime.now().year
    fee_year = kwargs.get("fee_year", current_year)
    base_fee = kwargs.get("base_fee", Decimal("300.00"))
    waiver_amount = kwargs.get("waiver_amount", Decimal("0.00"))
    actual_fee = kwargs.get("actual_fee", base_fee - waiver_amount)
    
    return {
        "id": kwargs.get("id", str(uuid.uuid4())),
        "waiver_rule_id": kwargs.get("waiver_rule_id", str(uuid.uuid4())),
        "card_id": kwargs.get("card_id", str(uuid.uuid4())),
        "fee_year": fee_year,
        "base_fee": str(base_fee),
        "actual_fee": str(actual_fee),
        "waiver_amount": str(waiver_amount),
        "waiver_reason": kwargs.get("waiver_reason"),
        "status": kwargs.get("status", "pending"),
        "due_date": kwargs.get("due_date"),
        "paid_date": kwargs.get("paid_date"),
        "notes": kwargs.get("notes", "测试年费记录"),
        "created_at": kwargs.get("created_at", datetime.now()),
        "updated_at": kwargs.get("updated_at", datetime.now())
    }


def build_paid_fee_record(**kwargs) -> Dict[str, Any]:
    """构建已缴费的年费记录"""
    base_record = build_annual_fee_record(**kwargs)
    paid_date = kwargs.get("paid_date", date.today() - timedelta(days=random.randint(1, 30)))
    
    base_record.update({
        "status": kwargs.get("status", "paid"),
        "paid_date": paid_date.isoformat() if isinstance(paid_date, date) else paid_date,
        "notes": kwargs.get("notes", "已缴费")
    })
    return base_record


def build_waived_fee_record(**kwargs) -> Dict[str, Any]:
    """构建已减免的年费记录"""
    base_fee = kwargs.get("base_fee", Decimal("300.00"))
    waiver_amount = kwargs.get("waiver_amount", base_fee)
    
    base_record = build_annual_fee_record(**kwargs)
    base_record.update({
        "base_fee": str(base_fee),
        "actual_fee": str(Decimal("0.00")),
        "waiver_amount": str(waiver_amount),
        "waiver_reason": kwargs.get("waiver_reason", "满足减免条件"),
        "status": kwargs.get("status", "waived"),
        "notes": kwargs.get("notes", "已减免年费")
    })
    return base_record


def build_overdue_fee_record(**kwargs) -> Dict[str, Any]:
    """构建逾期的年费记录"""
    base_record = build_annual_fee_record(**kwargs)
    due_date = kwargs.get("due_date", date.today() - timedelta(days=random.randint(30, 90)))
    
    base_record.update({
        "status": kwargs.get("status", "overdue"),
        "due_date": due_date.isoformat() if isinstance(due_date, date) else due_date,
        "notes": kwargs.get("notes", "年费逾期未缴")
    })
    return base_record


def build_fee_records_batch(count: int = 3, **kwargs) -> List[Dict[str, Any]]:
    """批量构建年费记录"""
    records = []
    current_year = datetime.now().year
    
    for i in range(count):
        record_kwargs = kwargs.copy()
        record_kwargs.update({
            "fee_year": record_kwargs.get("fee_year", current_year - i),
            "waiver_rule_id": str(uuid.uuid4())
        })
        records.append(build_annual_fee_record(**record_kwargs))
    
    return records


def build_fee_rules_batch(count: int = 3, **kwargs) -> List[Dict[str, Any]]:
    """批量构建年费减免规则"""
    rules = []
    current_year = datetime.now().year
    waiver_types = ["spending_amount", "transaction_count", "points_redemption", "rigid"]
    
    for i in range(count):
        rule_kwargs = kwargs.copy()
        rule_kwargs.update({
            "fee_year": rule_kwargs.get("fee_year", current_year + i),
            "waiver_type": rule_kwargs.get("waiver_type", waiver_types[i % len(waiver_types)]),
            "card_id": str(uuid.uuid4())
        })
        rules.append(build_fee_waiver_rule(**rule_kwargs))
    
    return rules


def build_batch_annual_fee_records(count=3, **kwargs):
    """批量构建年费记录"""
    records = []
    for i in range(count):
        record_data = {
            "waiver_rule_id": str(uuid.uuid4()),
            "fee_year": 2024 + i,
            "base_fee": Decimal("300.00") + Decimal(str(i * 100)),
            "actual_fee": Decimal("0.00") if i % 2 == 0 else Decimal("300.00"),
            "status": "waived" if i % 2 == 0 else "paid"
        }
        record_data.update(kwargs)
        records.append(build_annual_fee_record(**record_data))
    return records 