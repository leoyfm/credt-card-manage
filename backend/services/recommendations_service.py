"""
智能推荐服务

实现智能推荐相关的业务逻辑。
"""

import logging
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.recommendations import Recommendation, RecommendationCreate, RecommendationUpdate

logger = logging.getLogger(__name__)


class RecommendationsService:
    """智能推荐服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_recommendations(
        self, 
        user_id: UUID,
        skip: int = 0, 
        limit: int = 100, 
        keyword: str = ""
    ) -> Tuple[List[Recommendation], int]:
        """获取推荐列表"""
        try:
            logger.info(f"获取推荐列表: user_id={user_id}, keyword='{keyword}'")
            
            query = self.db.query(self._get_recommendation_model()).filter(
                self._get_recommendation_model().user_id == user_id,
                self._get_recommendation_model().is_deleted == False
            )
            
            # 模糊搜索
            if keyword.strip():
                search_filter = or_(
                    self._get_recommendation_model().card_name.ilike(f"%{keyword}%"),
                    self._get_recommendation_model().reason.ilike(f"%{keyword}%")
                )
                query = query.filter(search_filter)
            
            total = query.count()
            recommendations = query.order_by(
                self._get_recommendation_model().score.desc(),
                self._get_recommendation_model().created_at.desc()
            ).offset(skip).limit(limit).all()
            
            return [Recommendation.model_validate(rec) for rec in recommendations], total
            
        except Exception as e:
            logger.error(f"获取推荐列表失败: {str(e)}")
            raise Exception(f"获取推荐列表失败: {str(e)}")

    def create_recommendation(self, rec_data: RecommendationCreate, user_id: UUID) -> Recommendation:
        """创建推荐"""
        try:
            rec_dict = rec_data.model_dump()
            rec_dict['user_id'] = user_id
            
            db_rec = self._create_recommendation_db(rec_dict)
            self.db.add(db_rec)
            self.db.commit()
            self.db.refresh(db_rec)
            
            return Recommendation.model_validate(db_rec)
            
        except Exception as e:
            logger.error(f"创建推荐失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"创建推荐失败: {str(e)}")

    def get_recommendation(self, rec_id: UUID, user_id: UUID) -> Optional[Recommendation]:
        """获取单个推荐"""
        try:
            recommendation = self.db.query(self._get_recommendation_model()).filter(
                self._get_recommendation_model().id == rec_id,
                self._get_recommendation_model().user_id == user_id,
                self._get_recommendation_model().is_deleted == False
            ).first()
            
            if not recommendation:
                return None
                
            return Recommendation.model_validate(recommendation)
            
        except Exception as e:
            logger.error(f"获取推荐失败: {str(e)}")
            raise Exception(f"获取推荐失败: {str(e)}")

    def update_recommendation(
        self, 
        rec_id: UUID, 
        user_id: UUID,
        rec_data: RecommendationUpdate
    ) -> Optional[Recommendation]:
        """更新推荐"""
        try:
            recommendation = self.db.query(self._get_recommendation_model()).filter(
                self._get_recommendation_model().id == rec_id,
                self._get_recommendation_model().user_id == user_id,
                self._get_recommendation_model().is_deleted == False
            ).first()
            
            if not recommendation:
                return None
            
            update_data = rec_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(recommendation, field):
                    setattr(recommendation, field, value)
            
            self.db.commit()
            self.db.refresh(recommendation)
            
            return Recommendation.model_validate(recommendation)
            
        except Exception as e:
            logger.error(f"更新推荐失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"更新推荐失败: {str(e)}")

    def delete_recommendation(self, recommendation_id: UUID, user_id: UUID) -> bool:
        """删除推荐"""
        try:
            recommendation = self.db.query(self._get_recommendation_model()).filter(
                self._get_recommendation_model().id == recommendation_id,
                self._get_recommendation_model().user_id == user_id,
                self._get_recommendation_model().is_deleted == False
            ).first()
            
            if not recommendation:
                return False
            
            recommendation.is_deleted = True
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"删除推荐失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"删除推荐失败: {str(e)}")

    def _create_recommendation_db(self, rec_data: dict):
        """创建推荐数据库记录"""
        from db_models.recommendations import Recommendation
        return Recommendation(**rec_data)

    def _get_recommendation_model(self):
        """获取推荐数据库模型"""
        from db_models.recommendations import Recommendation
        return Recommendation 