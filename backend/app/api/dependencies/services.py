"""
服务层依赖注入
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.services.admin_service import AdminUserService
from app.services.card_service import CardService
from app.services.transaction_service import TransactionService
from app.db.database import get_db
from app.services.admin_card_service import AdminCardService


def get_admin_service(db: Session = Depends(get_db)) -> AdminUserService:
    """管理员服务依赖注入"""
    return AdminUserService(db)


def get_card_service(db: Session = Depends(get_db)) -> CardService:
    """信用卡服务依赖注入"""
    return CardService(db) 


def get_transaction_service(db: Session = Depends(get_db)) -> TransactionService:
    """交易服务依赖注入"""
    return TransactionService(db)


def get_admin_card_service(db: Session = Depends(get_db)) -> AdminCardService:
    """获取管理员信用卡服务实例"""
    return AdminCardService(db) 