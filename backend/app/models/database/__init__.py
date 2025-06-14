"""
数据库模型包

导入所有数据库模型以确保SQLAlchemy能够正确识别和创建表
"""

from .user import User, VerificationCode, LoginLog, WechatBinding
from .card import Bank, CreditCard
from .transaction import TransactionCategory, Transaction
from .fee_waiver import FeeWaiverRule, AnnualFeeRecord
from .reminder import ReminderSetting, ReminderRecord
from .recommendation import RecommendationRule, RecommendationRecord

__all__ = [
    "User",
    "VerificationCode", 
    "LoginLog",
    "WechatBinding",
    "Bank",
    "CreditCard",
    "TransactionCategory",
    "Transaction",
    "FeeWaiverRule",
    "AnnualFeeRecord",
    "ReminderSetting",
    "ReminderRecord",
    "RecommendationRule",
    "RecommendationRecord"
] 