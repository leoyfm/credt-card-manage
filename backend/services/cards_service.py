"""
信用卡服务

实现信用卡相关的业务逻辑，包括增删改查、额度管理等功能。
"""

import logging
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.cards import Card, CardCreate, CardUpdate
from utils.response import ResponseUtil

logger = logging.getLogger(__name__)


class CardsService:
    """
    信用卡服务类
    
    提供信用卡相关的业务逻辑处理，包括CRUD操作、额度管理等功能。
    """

    def __init__(self, db: Session):
        """
        初始化信用卡服务
        
        Args:
            db: 数据库会话
        """
        self.db = db

    def create_card(self, card_data: CardCreate, user_id: UUID) -> Card:
        """
        创建信用卡
        
        Args:
            card_data: 信用卡创建数据
            user_id: 用户ID
            
        Returns:
            Card: 创建的信用卡信息
            
        Raises:
            ValueError: 参数验证失败
            Exception: 创建失败
        """
        try:
            logger.info(f"创建信用卡: {card_data.bank_name} - {card_data.card_name}")
            
            # 检查卡号是否已存在
            existing_card = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().card_number == card_data.card_number,
                self._get_credit_card_model().is_deleted == False
            ).first()
            
            if existing_card:
                raise ValueError("信用卡号已存在")
            
            # 创建信用卡记录
            card_dict = card_data.dict()
            card_dict['user_id'] = user_id
            
            # 移除available_amount字段，因为它是计算属性
            if 'available_amount' in card_dict:
                card_dict.pop('available_amount')
            
            db_card = self._create_card_db(card_dict)
            self.db.add(db_card)
            self.db.commit()
            self.db.refresh(db_card)
            
            logger.info(f"信用卡创建成功: {db_card.id}")
            return Card.from_orm(db_card)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"创建信用卡失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"创建信用卡失败: {str(e)}")

    def get_cards(
        self, 
        user_id: UUID,
        skip: int = 0, 
        limit: int = 100, 
        keyword: str = ""
    ) -> Tuple[List[Card], int]:
        """
        获取信用卡列表
        
        Args:
            user_id: 用户ID
            skip: 跳过记录数
            limit: 限制记录数
            keyword: 搜索关键词
            
        Returns:
            Tuple[List[Card], int]: 信用卡列表和总数
        """
        try:
            logger.info(f"获取信用卡列表: user_id={user_id}, keyword='{keyword}'")
            
            query = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().user_id == user_id,
                self._get_credit_card_model().is_deleted == False
            )
            
            # 模糊搜索
            if keyword.strip():
                search_filter = or_(
                    self._get_credit_card_model().bank_name.ilike(f"%{keyword}%"),
                    self._get_credit_card_model().card_name.ilike(f"%{keyword}%"),
                    self._get_credit_card_model().notes.ilike(f"%{keyword}%")
                )
                query = query.filter(search_filter)
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            cards = query.order_by(
                self._get_credit_card_model().created_at.desc()
            ).offset(skip).limit(limit).all()
            
            logger.info(f"找到 {len(cards)} 张信用卡，总计 {total} 张")
            return [Card.from_orm(card) for card in cards], total
            
        except Exception as e:
            logger.error(f"获取信用卡列表失败: {str(e)}")
            raise Exception(f"获取信用卡列表失败: {str(e)}")

    def get_card(self, card_id: UUID, user_id: UUID) -> Optional[Card]:
        """
        获取单张信用卡详情
        
        Args:
            card_id: 信用卡ID
            user_id: 用户ID
            
        Returns:
            Optional[Card]: 信用卡信息
        """
        try:
            logger.info(f"获取信用卡详情: {card_id}")
            
            card = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().id == card_id,
                self._get_credit_card_model().user_id == user_id,
                self._get_credit_card_model().is_deleted == False
            ).first()
            
            if not card:
                logger.warning(f"信用卡不存在: {card_id}")
                return None
                
            return Card.from_orm(card)
            
        except Exception as e:
            logger.error(f"获取信用卡详情失败: {str(e)}")
            raise Exception(f"获取信用卡详情失败: {str(e)}")

    def update_card(
        self, 
        card_id: UUID, 
        user_id: UUID,
        card_data: CardUpdate
    ) -> Optional[Card]:
        """
        更新信用卡信息
        
        Args:
            card_id: 信用卡ID
            user_id: 用户ID
            card_data: 更新数据
            
        Returns:
            Optional[Card]: 更新后的信用卡信息
        """
        try:
            logger.info(f"更新信用卡: {card_id}")
            
            card = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().id == card_id,
                self._get_credit_card_model().user_id == user_id,
                self._get_credit_card_model().is_deleted == False
            ).first()
            
            if not card:
                logger.warning(f"信用卡不存在: {card_id}")
                return None
            
            # 更新字段
            update_data = card_data.dict(exclude_unset=True)
            # 移除available_amount字段，因为它是计算属性
            if 'available_amount' in update_data:
                update_data.pop('available_amount')
                
            for field, value in update_data.items():
                if hasattr(card, field):
                    setattr(card, field, value)
            
            self.db.commit()
            self.db.refresh(card)
            
            logger.info(f"信用卡更新成功: {card_id}")
            return Card.from_orm(card)
            
        except Exception as e:
            logger.error(f"更新信用卡失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"更新信用卡失败: {str(e)}")

    def delete_card(self, card_id: UUID, user_id: UUID) -> bool:
        """
        删除信用卡（软删除）
        
        Args:
            card_id: 信用卡ID
            user_id: 用户ID
            
        Returns:
            bool: 删除是否成功
        """
        try:
            logger.info(f"删除信用卡: {card_id}")
            
            card = self.db.query(self._get_credit_card_model()).filter(
                self._get_credit_card_model().id == card_id,
                self._get_credit_card_model().user_id == user_id,
                self._get_credit_card_model().is_deleted == False
            ).first()
            
            if not card:
                logger.warning(f"信用卡不存在: {card_id}")
                return False
            
            # 软删除
            card.is_deleted = True
            self.db.commit()
            
            logger.info(f"信用卡删除成功: {card_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除信用卡失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"删除信用卡失败: {str(e)}")

    def _create_card_db(self, card_data: dict):
        """创建信用卡数据库记录"""
        # 这里应该导入实际的CreditCard模型
        # 为了避免循环导入，使用动态导入
        from db_models.cards import CreditCard
        return CreditCard(**card_data)

    def _get_credit_card_model(self):
        """获取信用卡数据库模型"""
        from db_models.cards import CreditCard
        return CreditCard 