"""
还款提醒服务

实现还款提醒相关的业务逻辑。
"""

import logging
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.reminders import Reminder, ReminderCreate, ReminderUpdate

logger = logging.getLogger(__name__)


class RemindersService:
    """还款提醒服务类"""

    def __init__(self, db: Session):
        self.db = db

    def get_reminders(
        self, 
        user_id: UUID,
        skip: int = 0, 
        limit: int = 100, 
        keyword: str = ""
    ) -> Tuple[List[Reminder], int]:
        """获取还款提醒列表"""
        try:
            logger.info(f"获取还款提醒列表: user_id={user_id}, keyword='{keyword}'")
            
            query = self.db.query(self._get_reminder_model()).filter(
                self._get_reminder_model().user_id == user_id,
                self._get_reminder_model().is_deleted == False
            )
            
            # 模糊搜索
            if keyword.strip():
                search_filter = or_(
                    self._get_reminder_model().title.ilike(f"%{keyword}%"),
                    self._get_reminder_model().message.ilike(f"%{keyword}%")
                )
                query = query.filter(search_filter)
            
            total = query.count()
            reminders = query.order_by(
                self._get_reminder_model().reminder_date.desc()
            ).offset(skip).limit(limit).all()
            
            return [Reminder.from_orm(reminder) for reminder in reminders], total
            
        except Exception as e:
            logger.error(f"获取还款提醒列表失败: {str(e)}")
            raise Exception(f"获取还款提醒列表失败: {str(e)}")

    def create_reminder(self, reminder_data: ReminderCreate, user_id: UUID) -> Reminder:
        """创建还款提醒"""
        try:
            reminder_dict = reminder_data.dict()
            reminder_dict['user_id'] = user_id
            
            db_reminder = self._create_reminder_db(reminder_dict)
            self.db.add(db_reminder)
            self.db.commit()
            self.db.refresh(db_reminder)
            
            return Reminder.from_orm(db_reminder)
            
        except Exception as e:
            logger.error(f"创建还款提醒失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"创建还款提醒失败: {str(e)}")

    def get_reminder(self, reminder_id: UUID, user_id: UUID) -> Optional[Reminder]:
        """获取单个还款提醒"""
        try:
            reminder = self.db.query(self._get_reminder_model()).filter(
                self._get_reminder_model().id == reminder_id,
                self._get_reminder_model().user_id == user_id,
                self._get_reminder_model().is_deleted == False
            ).first()
            
            if not reminder:
                return None
                
            return Reminder.from_orm(reminder)
            
        except Exception as e:
            logger.error(f"获取还款提醒失败: {str(e)}")
            raise Exception(f"获取还款提醒失败: {str(e)}")

    def update_reminder(
        self, 
        reminder_id: UUID, 
        user_id: UUID,
        reminder_data: ReminderUpdate
    ) -> Optional[Reminder]:
        """更新还款提醒"""
        try:
            reminder = self.db.query(self._get_reminder_model()).filter(
                self._get_reminder_model().id == reminder_id,
                self._get_reminder_model().user_id == user_id,
                self._get_reminder_model().is_deleted == False
            ).first()
            
            if not reminder:
                return None
            
            update_data = reminder_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(reminder, field):
                    setattr(reminder, field, value)
            
            self.db.commit()
            self.db.refresh(reminder)
            
            return Reminder.from_orm(reminder)
            
        except Exception as e:
            logger.error(f"更新还款提醒失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"更新还款提醒失败: {str(e)}")

    def delete_reminder(self, reminder_id: UUID, user_id: UUID) -> bool:
        """删除还款提醒"""
        try:
            reminder = self.db.query(self._get_reminder_model()).filter(
                self._get_reminder_model().id == reminder_id,
                self._get_reminder_model().user_id == user_id,
                self._get_reminder_model().is_deleted == False
            ).first()
            
            if not reminder:
                return False
            
            reminder.is_deleted = True
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"删除还款提醒失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"删除还款提醒失败: {str(e)}")

    def mark_reminder_read(self, reminder_id: UUID, user_id: UUID) -> bool:
        """标记提醒已读"""
        try:
            reminder = self.db.query(self._get_reminder_model()).filter(
                self._get_reminder_model().id == reminder_id,
                self._get_reminder_model().user_id == user_id,
                self._get_reminder_model().is_deleted == False
            ).first()
            
            if not reminder:
                return False
            
            from models.reminders import ReminderStatus
            reminder.status = ReminderStatus.READ
            from datetime import datetime
            reminder.read_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"标记提醒已读失败: {str(e)}")
            self.db.rollback()
            raise Exception(f"标记提醒已读失败: {str(e)}")

    def _create_reminder_db(self, reminder_data: dict):
        """创建还款提醒数据库记录"""
        from db_models.reminders import Reminder
        return Reminder(**reminder_data)

    def _get_reminder_model(self):
        """获取还款提醒数据库模型"""
        from db_models.reminders import Reminder
        return Reminder 