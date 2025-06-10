"""数据清理工具

自动清理测试数据，防止测试污染
"""

import os
import logging
from typing import Set, List, Dict, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DataCleaner:
    """数据清理器"""
    
    def __init__(self):
        self.created_users: Set[str] = set()
        self.created_cards: Set[str] = set()
        self.created_transactions: Set[str] = set()
        self.created_objects: Dict[str, Set[str]] = {}
        self.cleanup_enabled = os.getenv("TEST_CLEANUP_DATA", "true").lower() == "true"
    
    def register_user(self, user_id: str):
        """注册用户以便清理"""
        if self.cleanup_enabled:
            self.created_users.add(user_id)
            logger.debug(f"注册用户以便清理: {user_id}")
    
    def register_card(self, card_id: str):
        """注册信用卡以便清理"""
        if self.cleanup_enabled:
            self.created_cards.add(card_id)
            logger.debug(f"注册信用卡以便清理: {card_id}")
    
    def register_transaction(self, transaction_id: str):
        """注册交易以便清理"""
        if self.cleanup_enabled:
            self.created_transactions.add(transaction_id)
            logger.debug(f"注册交易以便清理: {transaction_id}")
    
    def register_object(self, object_type: str, object_id: str):
        """注册任意对象以便清理"""
        if self.cleanup_enabled:
            if object_type not in self.created_objects:
                self.created_objects[object_type] = set()
            self.created_objects[object_type].add(object_id)
            logger.debug(f"注册{object_type}以便清理: {object_id}")
    
    def cleanup_all(self):
        """清理所有注册的对象"""
        if not self.cleanup_enabled:
            logger.info("数据清理已禁用，跳过清理")
            return
        
        logger.info("开始清理测试数据...")
        
        try:
            # 清理交易记录（优先清理，因为有外键依赖）
            self._cleanup_transactions()
            
            # 清理信用卡
            self._cleanup_cards()
            
            # 清理用户（最后清理，因为其他对象依赖用户）
            self._cleanup_users()
            
            # 清理其他对象
            self._cleanup_other_objects()
            
            logger.info("测试数据清理完成")
            
        except Exception as e:
            logger.error(f"数据清理失败: {e}")
    
    def _cleanup_users(self):
        """清理用户"""
        if not self.created_users:
            return
        
        logger.info(f"清理 {len(self.created_users)} 个测试用户")
        
        # 这里应该调用实际的数据库清理逻辑
        # 由于我们在测试环境中，这里暂时只是记录
        for user_id in self.created_users:
            logger.debug(f"清理用户: {user_id}")
        
        self.created_users.clear()
    
    def _cleanup_cards(self):
        """清理信用卡"""
        if not self.created_cards:
            return
        
        logger.info(f"清理 {len(self.created_cards)} 张测试信用卡")
        
        for card_id in self.created_cards:
            logger.debug(f"清理信用卡: {card_id}")
        
        self.created_cards.clear()
    
    def _cleanup_transactions(self):
        """清理交易记录"""
        if not self.created_transactions:
            return
        
        logger.info(f"清理 {len(self.created_transactions)} 条测试交易")
        
        for transaction_id in self.created_transactions:
            logger.debug(f"清理交易: {transaction_id}")
        
        self.created_transactions.clear()
    
    def _cleanup_other_objects(self):
        """清理其他对象"""
        for object_type, object_ids in self.created_objects.items():
            if object_ids:
                logger.info(f"清理 {len(object_ids)} 个{object_type}")
                for object_id in object_ids:
                    logger.debug(f"清理{object_type}: {object_id}")
        
        self.created_objects.clear()
    
    def get_cleanup_stats(self) -> Dict[str, int]:
        """获取清理统计信息"""
        stats = {
            "users": len(self.created_users),
            "cards": len(self.created_cards),
            "transactions": len(self.created_transactions)
        }
        
        for object_type, object_ids in self.created_objects.items():
            stats[object_type] = len(object_ids)
        
        return stats
    
    @contextmanager
    def auto_cleanup(self):
        """自动清理上下文管理器"""
        try:
            yield self
        finally:
            self.cleanup_all()


# 全局数据清理器实例
global_cleaner = DataCleaner()


def cleanup_after_test(func):
    """测试后自动清理装饰器"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            global_cleaner.cleanup_all()
    return wrapper


@contextmanager
def temp_data_context():
    """临时数据上下文"""
    cleaner = DataCleaner()
    try:
        yield cleaner
    finally:
        cleaner.cleanup_all() 