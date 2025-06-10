"""
信用卡管理服务层

包含信用卡相关的业务逻辑，包括增删改查、额度管理、状态管理等功能。
新架构下的信用卡服务。
"""

import logging
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import date, datetime, UTC
from decimal import Decimal

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc

from app.models.schemas.card import (
    Card,
    CardCreate,
    CardUpdate,
    CardQueryFilter,
    CardBatchOperation,
    CardStats,
    CardSummary,
    CardStatus,
    CardType
)
from app.models.database.card import CreditCard as DBCard
from app.utils.response import ResponseUtil
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


class CardsService:
    """信用卡管理服务"""

    def __init__(self, db: Session):
        self.db = db

    def create_card(self, card_data: CardCreate, user_id: UUID) -> Card:
        """
        创建信用卡
        
        参数:
        - card_data: 信用卡创建数据
        - user_id: 用户ID
        
        返回:
        - Card: 创建的信用卡信息
        
        异常:
        - ValueError: 参数验证失败或信用卡号已存在
        - Exception: 创建失败
        """
        logger.info(f"创建信用卡 - user_id: {user_id}, bank: {card_data.bank_name}")
        
        # 检查卡号是否已存在
        existing_card = self.db.query(DBCard).filter(
            and_(
                DBCard.card_number == card_data.card_number,
                DBCard.is_deleted == False
            )
        ).first()
        
        if existing_card:
            raise ValueError("信用卡号已存在")
        
        try:
            # 创建信用卡记录
            db_card = DBCard(
                user_id=user_id,
                **card_data.model_dump()
            )
            
            self.db.add(db_card)
            self.db.commit()
            self.db.refresh(db_card)
            
            logger.info(f"信用卡创建成功 - card_id: {db_card.id}")
            return Card.model_validate(db_card)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建信用卡失败 - error: {e}")
            raise Exception(f"创建信用卡失败: {str(e)}")

    def get_cards_list(
        self,
        user_id: UUID,
        filters: CardQueryFilter,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Card], int]:
        """
        获取信用卡列表
        
        参数:
        - user_id: 用户ID
        - filters: 查询过滤条件
        - page: 页码
        - page_size: 每页数量
        
        返回:
        - (信用卡列表, 总数量)
        """
        logger.info(f"获取信用卡列表 - user_id: {user_id}, page: {page}")
        
        # 基础查询
        query = self.db.query(DBCard).filter(
            and_(
                DBCard.user_id == user_id,
                DBCard.is_deleted == False
            )
        )
        
        # 应用筛选条件
        if filters.keyword:
            search_filter = or_(
                DBCard.card_name.ilike(f"%{filters.keyword}%"),
                DBCard.bank_name.ilike(f"%{filters.keyword}%"),
                DBCard.card_number.ilike(f"%{filters.keyword}%")
            )
            query = query.filter(search_filter)
        
        if filters.status:
            query = query.filter(DBCard.status == filters.status.value)
        
        if filters.card_type:
            query = query.filter(DBCard.card_type == filters.card_type.value)
        
        if filters.bank_name:
            query = query.filter(DBCard.bank_name.ilike(f"%{filters.bank_name}%"))
        
        if filters.is_primary is not None:
            query = query.filter(DBCard.is_primary == filters.is_primary)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        skip = ResponseUtil.calculate_skip(page, page_size)
        cards = query.order_by(desc(DBCard.created_at)).offset(skip).limit(page_size).all()
        
        # 转换为Pydantic模型
        card_list = [Card.model_validate(card) for card in cards]
        
        logger.info(f"获取信用卡列表成功 - 返回 {len(card_list)} 条记录")
        return card_list, total

    def get_card_by_id(self, card_id: UUID, user_id: UUID) -> Optional[Card]:
        """
        根据ID获取信用卡详情
        
        参数:
        - card_id: 信用卡ID
        - user_id: 用户ID
        
        返回:
        - 信用卡信息，不存在返回None
        """
        logger.info(f"获取信用卡详情 - card_id: {card_id}, user_id: {user_id}")
        
        card = self.db.query(DBCard).filter(
            and_(
                DBCard.id == card_id,
                DBCard.user_id == user_id,
                DBCard.is_deleted == False
            )
        ).first()
        
        if card:
            logger.info(f"信用卡详情获取成功 - card_name: {card.card_name}")
            return Card.model_validate(card)
        
        logger.warning(f"信用卡不存在 - card_id: {card_id}")
        return None

    def update_card(
        self,
        card_id: UUID,
        user_id: UUID,
        card_data: CardUpdate
    ) -> Optional[Card]:
        """
        更新信用卡信息
        
        参数:
        - card_id: 信用卡ID
        - user_id: 用户ID
        - card_data: 更新数据
        
        返回:
        - 更新后的信用卡信息，不存在返回None
        
        异常:
        - ValueError: 信用卡号已存在（当更新卡号时）
        """
        logger.info(f"更新信用卡 - card_id: {card_id}, user_id: {user_id}")
        
        card = self.db.query(DBCard).filter(
            and_(
                DBCard.id == card_id,
                DBCard.user_id == user_id,
                DBCard.is_deleted == False
            )
        ).first()
        
        if not card:
            logger.warning(f"信用卡不存在 - card_id: {card_id}")
            return None
        
        # 检查卡号是否被其他卡片占用
        update_data = card_data.model_dump(exclude_unset=True)
        if 'card_number' in update_data and update_data['card_number'] != card.card_number:
            existing_card = self.db.query(DBCard).filter(
                and_(
                    DBCard.card_number == update_data['card_number'],
                    DBCard.id != card_id,
                    DBCard.is_deleted == False
                )
            ).first()
            
            if existing_card:
                raise ValueError("信用卡号已存在")
        
        try:
            # 更新信用卡信息
            for field, value in update_data.items():
                setattr(card, field, value)
            
            card.updated_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(card)
            
            logger.info(f"信用卡更新成功 - card_id: {card_id}")
            return Card.model_validate(card)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新信用卡失败 - card_id: {card_id}, error: {e}")
            raise Exception(f"更新信用卡失败: {str(e)}")

    def update_card_status(
        self,
        card_id: UUID,
        user_id: UUID,
        status: CardStatus
    ) -> Optional[Card]:
        """
        更新信用卡状态
        
        参数:
        - card_id: 信用卡ID
        - user_id: 用户ID
        - status: 新状态
        
        返回:
        - 更新后的信用卡信息，不存在返回None
        """
        logger.info(f"更新信用卡状态 - card_id: {card_id}, status: {status}")
        
        card = self.db.query(DBCard).filter(
            and_(
                DBCard.id == card_id,
                DBCard.user_id == user_id,
                DBCard.is_deleted == False
            )
        ).first()
        
        if not card:
            logger.warning(f"信用卡不存在 - card_id: {card_id}")
            return None
        
        try:
            card.status = status.value
            card.updated_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(card)
            
            logger.info(f"信用卡状态更新成功 - card_id: {card_id}")
            return Card.model_validate(card)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新信用卡状态失败 - card_id: {card_id}, error: {e}")
            raise Exception(f"更新信用卡状态失败: {str(e)}")

    def delete_card(self, card_id: UUID, user_id: UUID) -> bool:
        """
        删除信用卡（软删除）
        
        参数:
        - card_id: 信用卡ID
        - user_id: 用户ID
        
        返回:
        - 是否删除成功
        """
        logger.info(f"删除信用卡 - card_id: {card_id}, user_id: {user_id}")
        
        card = self.db.query(DBCard).filter(
            and_(
                DBCard.id == card_id,
                DBCard.user_id == user_id,
                DBCard.is_deleted == False
            )
        ).first()
        
        if not card:
            logger.warning(f"信用卡不存在 - card_id: {card_id}")
            return False
        
        try:
            card.is_deleted = True
            card.deleted_at = datetime.now(UTC)
            self.db.commit()
            
            logger.info(f"信用卡删除成功 - card_id: {card_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除信用卡失败 - card_id: {card_id}, error: {e}")
            return False

    def batch_update_cards(
        self,
        user_id: UUID,
        operation: CardBatchOperation
    ) -> Dict[str, Any]:
        """
        批量操作信用卡
        
        参数:
        - user_id: 用户ID
        - operation: 批量操作信息
        
        返回:
        - 操作结果统计
        """
        logger.info(f"批量操作信用卡 - user_id: {user_id}, operation: {operation.operation_type}")
        
        # 查询目标信用卡
        cards = self.db.query(DBCard).filter(
            and_(
                DBCard.id.in_(operation.card_ids),
                DBCard.user_id == user_id,
                DBCard.is_deleted == False
            )
        ).all()
        
        if not cards:
            return {"success": 0, "failed": 0, "message": "未找到有效的信用卡"}
        
        success_count = 0
        failed_count = 0
        
        try:
            for card in cards:
                try:
                    if operation.operation_type == "activate":
                        card.status = CardStatus.ACTIVE.value
                    elif operation.operation_type == "deactivate":
                        card.status = CardStatus.INACTIVE.value
                    elif operation.operation_type == "delete":
                        card.is_deleted = True
                        card.deleted_at = datetime.now(UTC)
                    elif operation.operation_type == "set_primary":
                        # 首先取消其他卡片的主卡状态
                        self.db.query(DBCard).filter(
                            and_(
                                DBCard.user_id == user_id,
                                DBCard.is_deleted == False
                            )
                        ).update({"is_primary": False})
                        card.is_primary = True
                    
                    card.updated_at = datetime.now(UTC)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"批量操作单个信用卡失败 - card_id: {card.id}, error: {e}")
                    failed_count += 1
            
            self.db.commit()
            
            logger.info(f"批量操作完成 - 成功: {success_count}, 失败: {failed_count}")
            return {
                "success": success_count,
                "failed": failed_count,
                "message": f"成功操作 {success_count} 张信用卡，失败 {failed_count} 张"
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"批量操作失败 - error: {e}")
            raise Exception(f"批量操作失败: {str(e)}")

    def get_cards_statistics(self, user_id: UUID) -> CardStats:
        """
        获取信用卡统计信息
        
        参数:
        - user_id: 用户ID
        
        返回:
        - 信用卡统计信息
        """
        logger.info(f"获取信用卡统计 - user_id: {user_id}")
        
        # 基础查询
        base_query = self.db.query(DBCard).filter(
            and_(
                DBCard.user_id == user_id,
                DBCard.is_deleted == False
            )
        )
        
        # 统计各项数据
        total_cards = base_query.count()
        active_cards = base_query.filter(DBCard.status == CardStatus.ACTIVE.value).count()
        inactive_cards = base_query.filter(DBCard.status == CardStatus.INACTIVE.value).count()
        
        # 额度统计
        total_limit = base_query.with_entities(func.sum(DBCard.credit_limit)).scalar() or Decimal('0')
        used_amount = base_query.with_entities(func.sum(DBCard.used_amount)).scalar() or Decimal('0')
        available_amount = total_limit - used_amount
        
        # 使用率统计
        usage_rate = float(used_amount / total_limit * 100) if total_limit > 0 else 0.0
        
        # 银行分布统计
        bank_stats = self.db.query(
            DBCard.bank_name,
            func.count(DBCard.id).label('count')
        ).filter(
            and_(
                DBCard.user_id == user_id,
                DBCard.is_deleted == False
            )
        ).group_by(DBCard.bank_name).all()
        
        bank_distribution = [
            {"bank_name": stat.bank_name, "count": stat.count}
            for stat in bank_stats
        ]
        
        # 类型分布统计
        type_stats = self.db.query(
            DBCard.card_type,
            func.count(DBCard.id).label('count')
        ).filter(
            and_(
                DBCard.user_id == user_id,
                DBCard.is_deleted == False
            )
        ).group_by(DBCard.card_type).all()
        
        type_distribution = [
            {"card_type": stat.card_type, "count": stat.count}
            for stat in type_stats
        ]
        
        stats = CardStats(
            total_cards=total_cards,
            active_cards=active_cards,
            inactive_cards=inactive_cards,
            total_limit=total_limit,
            used_amount=used_amount,
            available_amount=available_amount,
            usage_rate=usage_rate,
            bank_distribution=bank_distribution,
            type_distribution=type_distribution
        )
        
        logger.info(f"信用卡统计获取成功 - 总计: {total_cards} 张")
        return stats

    def get_cards_summary(self, user_id: UUID) -> List[CardSummary]:
        """
        获取信用卡摘要列表（用于下拉选择等场景）
        
        参数:
        - user_id: 用户ID
        
        返回:
        - 信用卡摘要列表
        """
        logger.info(f"获取信用卡摘要 - user_id: {user_id}")
        
        cards = self.db.query(DBCard).filter(
            and_(
                DBCard.user_id == user_id,
                DBCard.is_deleted == False,
                DBCard.status == CardStatus.ACTIVE.value
            )
        ).order_by(desc(DBCard.is_primary), DBCard.bank_name, DBCard.card_name).all()
        
        summary_list = [CardSummary.model_validate(card) for card in cards]
        
        logger.info(f"信用卡摘要获取成功 - 返回 {len(summary_list)} 张")
        return summary_list