"""数据工厂模块

提供自动化测试数据生成功能
"""

from .base import DataFactory, FactoryRegistry
from .user_factory import UserFactory
from .card_factory import CardFactory
from .transaction_factory import TransactionFactory

__all__ = [
    'DataFactory',
    'FactoryRegistry', 
    'UserFactory',
    'CardFactory',
    'TransactionFactory'
] 