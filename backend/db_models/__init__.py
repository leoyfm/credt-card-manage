"""
数据库模型包

包含SQLAlchemy ORM模型定义，定义数据库表结构。
与Pydantic模型分离，避免循环依赖。
"""

from .base import Base, BaseModel
from .cards import CreditCard
from .annual_fee import AnnualFeeRule, AnnualFeeRecord
from .reminders import Reminder
from .recommendations import Recommendation
from .transactions import Transaction
from .users import User, VerificationCode, WechatBinding, UserSession, LoginLog

__all__ = [
    "Base",
    "BaseModel",
    "CreditCard", 
    "AnnualFeeRule",
    "AnnualFeeRecord",
    "Reminder",
    "Recommendation",
    "Transaction",
    "User",
    "VerificationCode", 
    "WechatBinding",
    "UserSession",
    "LoginLog"
] 