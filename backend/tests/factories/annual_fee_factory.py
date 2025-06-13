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
    rule_name = kwargs.get("rule_name") or "测试减免规则"
    condition_type = kwargs.get("condition_type") or random.choice([
        "spending_amount", "transaction_count", "points_redeem", "specific_category"
    ])
    
    # 根据条件类型设置默认值
    if condition_type == "spending_amount":
        condition_value = kwargs.get("condition_value", Decimal("50000.00"))
        condition_count = kwargs.get("condition_count")
    elif condition_type == "transaction_count":
        condition_value = kwargs.get("condition_value")
        condition_count = kwargs.get("condition_count", 100)
    elif condition_type == "points_redeem":
        condition_value = kwargs.get("condition_value", Decimal("10000.00"))
        condition_count = kwargs.get("condition_count")
    else:  # specific_category
        condition_value = kwargs.get("condition_value", Decimal("20000.00"))
        condition_count = kwargs.get("condition_count", 50)
    
    return {
        "rule_name": rule_name,
        "condition_type": condition_type,
        "condition_value": condition_value,
        "condition_count": condition_count,
        "condition_period": kwargs.get("condition_period", "yearly"),
        "logical_operator": kwargs.get("logical_operator"),
        "priority": kwargs.get("priority", 1),
        "is_enabled": kwargs.get("is_enabled", True),
        "effective_from": kwargs.get("effective_from"),
        "effective_to": kwargs.get("effective_to"),
        "description": kwargs.get("description", f"测试规则：{rule_name}")
    }


def build_simple_fee_rule(**kwargs) -> Dict[str, Any]:
    """构建简单的年费减免规则（只包含必需字段）
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 简化的年费减免规则数据字典
    """
    return {
        "rule_name": kwargs.get("rule_name", "简单测试规则"),
        "condition_type": kwargs.get("condition_type", "spending_amount"),
        "condition_value": kwargs.get("condition_value", Decimal("30000.00")),
        "condition_period": kwargs.get("condition_period", "yearly")
    }


def build_spending_rule(**kwargs) -> Dict[str, Any]:
    """构建消费金额减免规则
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 消费金额减免规则数据字典
    """
    base_rule = build_fee_waiver_rule(**kwargs)
    
    base_rule.update({
        "rule_name": kwargs.get("rule_name", "年消费满额减免"),
        "condition_type": "spending_amount",
        "condition_value": kwargs.get("condition_value", Decimal("50000.00")),
        "condition_period": kwargs.get("condition_period", "yearly"),
        "description": kwargs.get("description", "年消费满5万元免年费")
    })
    
    return base_rule


def build_transaction_count_rule(**kwargs) -> Dict[str, Any]:
    """构建交易次数减免规则
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 交易次数减免规则数据字典
    """
    base_rule = build_fee_waiver_rule(**kwargs)
    
    base_rule.update({
        "rule_name": kwargs.get("rule_name", "年交易次数减免"),
        "condition_type": "transaction_count",
        "condition_count": kwargs.get("condition_count", 100),
        "condition_period": kwargs.get("condition_period", "yearly"),
        "description": kwargs.get("description", "年交易满100笔免年费")
    })
    
    return base_rule


def build_points_redeem_rule(**kwargs) -> Dict[str, Any]:
    """构建积分兑换减免规则
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 积分兑换减免规则数据字典
    """
    base_rule = build_fee_waiver_rule(**kwargs)
    
    base_rule.update({
        "rule_name": kwargs.get("rule_name", "积分兑换年费"),
        "condition_type": "points_redeem",
        "condition_value": kwargs.get("condition_value", Decimal("20000.00")),
        "condition_period": kwargs.get("condition_period", "yearly"),
        "description": kwargs.get("description", "2万积分兑换年费")
    })
    
    return base_rule


def build_annual_fee_record(**kwargs) -> Dict[str, Any]:
    """构建年费记录测试数据
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 年费记录数据字典
    """
    current_year = datetime.now().year
    fee_year = kwargs.get("fee_year", current_year)
    base_fee = kwargs.get("base_fee", Decimal("580.00"))
    waiver_amount = kwargs.get("waiver_amount", Decimal("0.00"))
    actual_fee = kwargs.get("actual_fee", base_fee - waiver_amount)
    
    return {
        "fee_year": fee_year,
        "base_fee": base_fee,
        "actual_fee": actual_fee,
        "waiver_amount": waiver_amount,
        "waiver_rules_applied": kwargs.get("waiver_rules_applied", []),
        "rule_evaluation_result": kwargs.get("rule_evaluation_result"),
        "waiver_reason": kwargs.get("waiver_reason"),
        "calculation_details": kwargs.get("calculation_details"),
        "status": kwargs.get("status", "pending"),
        "due_date": kwargs.get("due_date"),
        "paid_date": kwargs.get("paid_date"),
        "payment_method": kwargs.get("payment_method"),
        "notes": kwargs.get("notes", "测试年费记录")
    }


def build_paid_fee_record(**kwargs) -> Dict[str, Any]:
    """构建已缴费的年费记录
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 已缴费年费记录数据字典
    """
    base_record = build_annual_fee_record(**kwargs)
    
    paid_date = kwargs.get("paid_date", date.today() - timedelta(days=random.randint(1, 30)))
    
    base_record.update({
        "status": kwargs.get("status", "paid"),
        "paid_date": paid_date,
        "payment_method": kwargs.get("payment_method", "auto_deduct"),
        "notes": kwargs.get("notes", "已自动扣费")
    })
    
    return base_record


def build_waived_fee_record(**kwargs) -> Dict[str, Any]:
    """构建已减免的年费记录
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 已减免年费记录数据字典
    """
    base_fee = kwargs.get("base_fee", Decimal("580.00"))
    waiver_amount = kwargs.get("waiver_amount", base_fee)
    
    base_record = build_annual_fee_record(**kwargs)
    
    base_record.update({
        "actual_fee": Decimal("0.00"),
        "waiver_amount": waiver_amount,
        "waiver_reason": kwargs.get("waiver_reason", "满足消费条件"),
        "waiver_rules_applied": kwargs.get("waiver_rules_applied", ["年消费满额减免"]),
        "status": kwargs.get("status", "waived"),
        "payment_method": kwargs.get("payment_method", "waived"),
        "notes": kwargs.get("notes", "年费已减免")
    })
    
    return base_record


def build_overdue_fee_record(**kwargs) -> Dict[str, Any]:
    """构建逾期年费记录
    
    Args:
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 逾期年费记录数据字典
    """
    base_record = build_annual_fee_record(**kwargs)
    
    due_date = kwargs.get("due_date", date.today() - timedelta(days=random.randint(30, 90)))
    
    base_record.update({
        "status": kwargs.get("status", "overdue"),
        "due_date": due_date,
        "notes": kwargs.get("notes", "年费逾期未缴")
    })
    
    return base_record


def build_fee_records_batch(count: int = 3, **kwargs) -> List[Dict[str, Any]]:
    """批量构建年费记录数据
    
    Args:
        count: 要生成的记录数量
        **kwargs: 可选的覆盖参数
        
    Returns:
        List[Dict[str, Any]]: 年费记录数据列表
    """
    records = []
    current_year = datetime.now().year
    
    for i in range(count):
        record_kwargs = kwargs.copy()
        # 生成不同年份的记录
        if "fee_year" not in record_kwargs:
            record_kwargs["fee_year"] = current_year - i
        records.append(build_annual_fee_record(**record_kwargs))
    
    return records


def build_fee_rules_batch(count: int = 3, **kwargs) -> List[Dict[str, Any]]:
    """批量构建年费减免规则数据
    
    Args:
        count: 要生成的规则数量
        **kwargs: 可选的覆盖参数
        
    Returns:
        List[Dict[str, Any]]: 年费减免规则数据列表
    """
    rules = []
    rule_types = ["spending_amount", "transaction_count", "points_redeem"]
    
    for i in range(count):
        rule_kwargs = kwargs.copy()
        # 生成不同类型的规则
        if "condition_type" not in rule_kwargs:
            rule_kwargs["condition_type"] = rule_types[i % len(rule_types)]
        if "rule_name" not in rule_kwargs:
            rule_kwargs["rule_name"] = f"测试规则{i+1}"
        if "priority" not in rule_kwargs:
            rule_kwargs["priority"] = i + 1
        rules.append(build_fee_waiver_rule(**rule_kwargs))
    
    return rules


# 预定义的年费模板
FEE_TEMPLATES = {
    "普通年费": {
        "base_fee": Decimal("200.00"),
        "actual_fee": Decimal("200.00"),
        "waiver_amount": Decimal("0.00"),
        "status": "pending"
    },
    "白金卡年费": {
        "base_fee": Decimal("580.00"),
        "actual_fee": Decimal("580.00"),
        "waiver_amount": Decimal("0.00"),
        "status": "pending"
    },
    "钻石卡年费": {
        "base_fee": Decimal("3600.00"),
        "actual_fee": Decimal("3600.00"),
        "waiver_amount": Decimal("0.00"),
        "status": "pending"
    },
    "已减免年费": {
        "base_fee": Decimal("580.00"),
        "actual_fee": Decimal("0.00"),
        "waiver_amount": Decimal("580.00"),
        "status": "waived",
        "waiver_reason": "满足消费条件"
    }
}

RULE_TEMPLATES = {
    "消费减免": {
        "rule_name": "年消费满额减免",
        "condition_type": "spending_amount",
        "condition_value": Decimal("50000.00"),
        "condition_period": "yearly",
        "description": "年消费满5万元免年费"
    },
    "交易次数减免": {
        "rule_name": "年交易次数减免",
        "condition_type": "transaction_count",
        "condition_count": 100,
        "condition_period": "yearly",
        "description": "年交易满100笔免年费"
    },
    "积分兑换": {
        "rule_name": "积分兑换年费",
        "condition_type": "points_redeem",
        "condition_value": Decimal("20000.00"),
        "condition_period": "yearly",
        "description": "2万积分兑换年费"
    }
}


def build_template_fee_record(template_name: str, **kwargs) -> Dict[str, Any]:
    """根据模板构建年费记录数据
    
    Args:
        template_name: 模板名称
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 年费记录数据字典
        
    Raises:
        ValueError: 当模板不存在时
    """
    if template_name not in FEE_TEMPLATES:
        raise ValueError(f"未知的年费模板: {template_name}，可用模板: {list(FEE_TEMPLATES.keys())}")
    
    template = FEE_TEMPLATES[template_name].copy()
    template.update(kwargs)
    
    return build_annual_fee_record(**template)


def build_template_fee_rule(template_name: str, **kwargs) -> Dict[str, Any]:
    """根据模板构建年费减免规则数据
    
    Args:
        template_name: 模板名称
        **kwargs: 可选的覆盖参数
        
    Returns:
        Dict[str, Any]: 年费减免规则数据字典
        
    Raises:
        ValueError: 当模板不存在时
    """
    if template_name not in RULE_TEMPLATES:
        raise ValueError(f"未知的规则模板: {template_name}，可用模板: {list(RULE_TEMPLATES.keys())}")
    
    template = RULE_TEMPLATES[template_name].copy()
    template.update(kwargs)
    
    return build_fee_waiver_rule(**template) 