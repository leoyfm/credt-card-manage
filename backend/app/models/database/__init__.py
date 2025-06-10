"""
数据库模型包

导出所有数据库模型类，方便统一导入使用。
"""

from .base import Base, BaseModel

# 用户模块
from .user import User, VerificationCode, LoginLog, WechatBinding

# 银行和信用卡模块  
from .card import Bank, CreditCard

# 年费管理模块
from .annual_fee import FeeWaiverRule, AnnualFeeRecord

# 交易管理模块
from .transaction import TransactionCategory, Transaction

# 还款提醒模块
from .reminder import ReminderSetting, ReminderLog

# 统计分析模块
from .statistics import UserStatistics

# 系统配置模块
from .system import SystemConfig, NotificationTemplate

# 智能推荐模块
from .recommendation import RecommendationRule, RecommendationRecord

__all__ = [
    # 基础
    "Base", "BaseModel",
    
    # 用户模块
    "User", "VerificationCode", "LoginLog", "WechatBinding",
    
    # 银行和信用卡模块
    "Bank", "CreditCard",
    
    # 年费管理模块  
    "FeeWaiverRule", "AnnualFeeRecord",
    
    # 交易管理模块
    "TransactionCategory", "Transaction",
    
    # 还款提醒模块
    "ReminderSetting", "ReminderLog", 
    
    # 统计分析模块
    "UserStatistics",
    
    # 系统配置模块
    "SystemConfig", "NotificationTemplate",
    
    # 智能推荐模块
    "RecommendationRule", "RecommendationRecord"
] 