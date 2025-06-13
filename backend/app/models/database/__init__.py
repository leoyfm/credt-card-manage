"""
数据库模型包

导入所有数据库模型以确保SQLAlchemy能够正确识别和创建表
"""

from .user import User, VerificationCode, LoginLog, WechatBinding
from .card import Bank, CreditCard
from .transaction import TransactionCategory, Transaction
from .annual_fee import FeeWaiverRule, AnnualFeeRecord, AnnualFeeRule
from .reminder import ReminderSetting, ReminderRecord

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
    "AnnualFeeRule",
    "ReminderSetting",
    "ReminderRecord"
] 