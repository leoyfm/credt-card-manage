"""
服务层依赖注入模块

提供所有业务服务的依赖注入函数，支持新架构下的服务层。
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.services import (
    AuthService,
    UsersService,
    CardsService,
    TransactionsService,
    AnnualFeeService,
    ReminderService,
    RecommendationService,
    StatisticsService
)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """获取认证服务实例"""
    return AuthService(db)


def get_users_service(db: Session = Depends(get_db)) -> UsersService:
    """获取用户管理服务实例"""
    return UsersService(db)


def get_cards_service(db: Session = Depends(get_db)) -> CardsService:
    """获取信用卡服务实例"""
    return CardsService(db)


def get_transactions_service(db: Session = Depends(get_db)) -> TransactionsService:
    """获取交易服务实例"""
    return TransactionsService(db)


def get_annual_fee_service(db: Session = Depends(get_db)) -> AnnualFeeService:
    """获取年费服务实例"""
    return AnnualFeeService(db)


def get_reminder_service(db: Session = Depends(get_db)) -> ReminderService:
    """获取提醒服务实例"""
    return ReminderService(db)


def get_recommendation_service(db: Session = Depends(get_db)) -> RecommendationService:
    """获取推荐服务实例"""
    return RecommendationService(db)


def get_statistics_service(db: Session = Depends(get_db)) -> StatisticsService:
    """获取统计服务实例"""
    return StatisticsService(db)