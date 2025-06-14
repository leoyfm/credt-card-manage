"""
测试数据工厂模块

提供统一的数据工厂导入接口，简化测试代码中的导入语句。

使用示例:
    from tests.factories import build_user, build_card, build_transaction
    
    # 或者导入整个模块
    from tests.factories import user_factory, card_factory
"""

# 用户相关工厂
from .user_factory import (
    build_user,
    build_simple_user,
    build_admin_user,
    build_verified_user,
    build_inactive_user,
    build_users_batch,
    build_template_user,
    USER_TEMPLATES
)

# 信用卡相关工厂
from .card_factory import (
    build_card,
    build_simple_card,
    build_premium_card,
    build_expired_card,
    build_cards_batch,
    build_template_card,
    CARD_TEMPLATES
)

# 交易相关工厂
from .transaction_factory import (
    build_transaction,
    build_simple_transaction,
    build_large_transaction,
    build_refund_transaction,
    build_pending_transaction,
    build_transactions_batch,
    build_monthly_transactions,
    build_template_transaction,
    TRANSACTION_TEMPLATES
)

# 年费相关工厂
from .fee_waiver_factory import (
    build_fee_waiver_rule,
    build_spending_rule,
    build_transaction_count_rule,
    build_points_redemption_rule,
    build_rigid_rule,
    build_annual_fee_record,
    build_paid_fee_record,
    build_waived_fee_record,
    build_overdue_fee_record,
    build_fee_records_batch,
    build_fee_rules_batch
)

# 导出所有工厂模块，便于需要时直接使用
from . import user_factory
from . import card_factory
from . import transaction_factory
from . import fee_waiver_factory

# 定义公共接口
__all__ = [
    # 用户工厂
    "build_user",
    "build_simple_user", 
    "build_admin_user",
    "build_verified_user",
    "build_inactive_user",
    "build_users_batch",
    "build_template_user",
    "USER_TEMPLATES",
    
    # 信用卡工厂
    "build_card",
    "build_simple_card",
    "build_premium_card", 
    "build_expired_card",
    "build_cards_batch",
    "build_template_card",
    "CARD_TEMPLATES",
    
    # 交易工厂
    "build_transaction",
    "build_simple_transaction",
    "build_large_transaction",
    "build_refund_transaction",
    "build_pending_transaction",
    "build_transactions_batch",
    "build_monthly_transactions",
    "build_template_transaction",
    "TRANSACTION_TEMPLATES",
    
    # 年费工厂
    "build_fee_waiver_rule",
    "build_spending_rule",
    "build_transaction_count_rule",
    "build_points_redemption_rule",
    "build_rigid_rule",
    "build_annual_fee_record",
    "build_paid_fee_record",
    "build_waived_fee_record",
    "build_overdue_fee_record",
    "build_fee_records_batch",
    "build_fee_rules_batch",
    
    # 工厂模块
    "user_factory",
    "card_factory", 
    "transaction_factory",
    "fee_waiver_factory"
]


def get_all_templates():
    """获取所有可用的数据模板
    
    Returns:
        dict: 包含所有模板的字典
    """
    return {
        "users": USER_TEMPLATES,
        "cards": CARD_TEMPLATES,
        "transactions": TRANSACTION_TEMPLATES
    }


def list_available_templates():
    """列出所有可用的模板名称
    
    Returns:
        dict: 按类型分组的模板名称列表
    """
    templates = get_all_templates()
    return {
        category: list(template_dict.keys())
        for category, template_dict in templates.items()
    } 