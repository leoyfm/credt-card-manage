"""
还款提醒服务层

包含提醒设置、提醒记录、提醒触发等功能。
新架构下的提醒服务。
"""

import logging
from datetime import datetime, date, timedelta, UTC
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

from app.models.schemas.reminder import (
    ReminderSetting,
    ReminderSettingCreate,
    ReminderSettingUpdate,
    ReminderRecord,
    ReminderRecordCreate,
    ReminderQueryFilter,
    ReminderBatchOperation,
    ReminderStats,
    ReminderTemplate,
    ReminderType,
    NotificationChannel,
    ReminderStatus
)
from app.models.database.reminder import (
    ReminderSetting as DBReminderSetting,
    ReminderRecord as DBReminderRecord
)
from app.models.database.card import CreditCard as DBCard
from app.utils.response import ResponseUtil
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


class ReminderService:
    """还款提醒服务"""

    def __init__(self, db: Session):
        self.db = db

    # ==================== 提醒设置管理 ====================

    def create_reminder_setting(
        self, 
        setting_data: ReminderSettingCreate,
        user_id: UUID
    ) -> ReminderSetting:
        """创建提醒设置"""
        try:
            logger.info(f"创建提醒设置", extra={
                "user_id": str(user_id),
                "card_id": str(setting_data.card_id),
                "reminder_type": setting_data.reminder_type.value
            })
            
            # 验证信用卡是否属于该用户
            if setting_data.card_id:
                card = self.db.query(DBCard).filter(
                    and_(
                        DBCard.id == setting_data.card_id,
                        DBCard.user_id == user_id
                    )
                ).first()
                
                if not card:
                    raise ValueError("信用卡不存在或不属于该用户")
            
            # 创建提醒设置
            setting_dict = setting_data.model_dump(exclude_unset=True)
            setting_dict['user_id'] = user_id
            
            db_setting = DBReminderSetting(**setting_dict)
            self.db.add(db_setting)
            self.db.commit()
            self.db.refresh(db_setting)
            
            logger.info(f"提醒设置创建成功", extra={
                "setting_id": str(db_setting.id),
                "user_id": str(user_id)
            })
            
            return ReminderSetting.model_validate(db_setting)
            
        except Exception as e:
            logger.error(f"创建提醒设置失败: {str(e)}", extra={
                "user_id": str(user_id),
                "error": str(e)
            })
            self.db.rollback()
            raise

    def get_reminder_settings(
        self,
        user_id: UUID,
        card_id: Optional[UUID] = None,
        reminder_type: Optional[ReminderType] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[ReminderSetting], int]:
        """获取提醒设置列表"""
        try:
            query = self.db.query(DBReminderSetting).filter(
                DBReminderSetting.user_id == user_id
            )
            
            if card_id:
                query = query.filter(DBReminderSetting.card_id == card_id)
            
            if reminder_type:
                query = query.filter(DBReminderSetting.reminder_type == reminder_type)
            
            total = query.count()
            settings = query.order_by(
                desc(DBReminderSetting.created_at)
            ).offset(skip).limit(limit).all()
            
            return [ReminderSetting.model_validate(setting) for setting in settings], total
            
        except Exception as e:
            logger.error(f"获取提醒设置失败: {str(e)}")
            raise

    def get_reminder_setting_by_id(
        self, 
        setting_id: UUID, 
        user_id: UUID
    ) -> Optional[ReminderSetting]:
        """获取单个提醒设置"""
        try:
            setting = self.db.query(DBReminderSetting).filter(
                and_(
                    DBReminderSetting.id == setting_id,
                    DBReminderSetting.user_id == user_id
                )
            ).first()
            
            if not setting:
                return None
                
            return ReminderSetting.model_validate(setting)
            
        except Exception as e:
            logger.error(f"获取提醒设置失败: {str(e)}")
            raise

    def update_reminder_setting(
        self,
        setting_id: UUID,
        user_id: UUID,
        setting_data: ReminderSettingUpdate
    ) -> Optional[ReminderSetting]:
        """更新提醒设置"""
        try:
            setting = self.db.query(DBReminderSetting).filter(
                and_(
                    DBReminderSetting.id == setting_id,
                    DBReminderSetting.user_id == user_id
                )
            ).first()
            
            if not setting:
                return None
            
            # 更新字段
            update_data = setting_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(setting, field, value)
            
            setting.updated_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(setting)
            
            logger.info(f"提醒设置更新成功", extra={
                "setting_id": str(setting_id),
                "user_id": str(user_id)
            })
            
            return ReminderSetting.model_validate(setting)
            
        except Exception as e:
            logger.error(f"更新提醒设置失败: {str(e)}")
            self.db.rollback()
            raise

    def delete_reminder_setting(self, setting_id: UUID, user_id: UUID) -> bool:
        """删除提醒设置"""
        try:
            setting = self.db.query(DBReminderSetting).filter(
                and_(
                    DBReminderSetting.id == setting_id,
                    DBReminderSetting.user_id == user_id
                )
            ).first()
            
            if not setting:
                return False
            
            self.db.delete(setting)
            self.db.commit()
            
            logger.info(f"提醒设置删除成功", extra={
                "setting_id": str(setting_id),
                "user_id": str(user_id)
            })
            
            return True
            
        except Exception as e:
            logger.error(f"删除提醒设置失败: {str(e)}")
            self.db.rollback()
            raise

    # ==================== 提醒记录管理 ====================

    def create_reminder_record(
        self,
        record_data: ReminderRecordCreate,
        user_id: UUID
    ) -> ReminderRecord:
        """创建提醒记录"""
        try:
            # 验证提醒设置是否属于该用户
            setting = self.db.query(DBReminderSetting).filter(
                and_(
                    DBReminderSetting.id == record_data.setting_id,
                    DBReminderSetting.user_id == user_id
                )
            ).first()
            
            if not setting:
                raise ValueError("提醒设置不存在或不属于该用户")
            
            # 创建提醒记录
            record_dict = record_data.model_dump(exclude_unset=True)
            db_record = DBReminderRecord(**record_dict)
            self.db.add(db_record)
            self.db.commit()
            self.db.refresh(db_record)
            
            logger.info(f"提醒记录创建成功", extra={
                "record_id": str(db_record.id),
                "user_id": str(user_id)
            })
            
            return ReminderRecord.model_validate(db_record)
            
        except Exception as e:
            logger.error(f"创建提醒记录失败: {str(e)}")
            self.db.rollback()
            raise

    def get_reminder_records(
        self,
        user_id: UUID,
        filter_params: ReminderQueryFilter,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[ReminderRecord], int]:
        """获取提醒记录列表"""
        try:
            # 通过关联查询确保只获取用户自己的记录
            query = self.db.query(DBReminderRecord).join(DBReminderSetting).filter(
                DBReminderSetting.user_id == user_id
            )
            
            # 应用过滤条件
            if filter_params.card_id:
                query = query.filter(DBReminderSetting.card_id == filter_params.card_id)
            
            if filter_params.reminder_type:
                query = query.filter(DBReminderSetting.reminder_type == filter_params.reminder_type)
            
            if filter_params.status:
                query = query.filter(DBReminderRecord.status == filter_params.status)
            
            if filter_params.start_date:
                query = query.filter(DBReminderRecord.reminder_date >= filter_params.start_date)
            
            if filter_params.end_date:
                query = query.filter(DBReminderRecord.reminder_date <= filter_params.end_date)
            
            if filter_params.keyword:
                keyword_filter = f"%{filter_params.keyword}%"
                query = query.join(DBCard).filter(
                    or_(
                        DBCard.card_name.ilike(keyword_filter),
                        DBCard.bank_name.ilike(keyword_filter),
                        DBReminderRecord.message.ilike(keyword_filter)
                    )
                )
            
            total = query.count()
            records = query.order_by(
                desc(DBReminderRecord.reminder_date)
            ).offset(skip).limit(limit).all()
            
            return [ReminderRecord.model_validate(record) for record in records], total
            
        except Exception as e:
            logger.error(f"获取提醒记录失败: {str(e)}")
            raise

    def get_pending_reminders(self, user_id: UUID) -> List[ReminderRecord]:
        """获取待处理的提醒"""
        try:
            now = datetime.now(UTC)
            
            records = self.db.query(DBReminderRecord).join(DBReminderSetting).filter(
                and_(
                    DBReminderSetting.user_id == user_id,
                    DBReminderRecord.status == ReminderStatus.PENDING,
                    DBReminderRecord.reminder_date <= now
                )
            ).all()
            
            return [ReminderRecord.model_validate(record) for record in records]
            
        except Exception as e:
            logger.error(f"获取待处理提醒失败: {str(e)}")
            raise

    def mark_reminder_sent(self, record_id: UUID, user_id: UUID) -> bool:
        """标记提醒已发送"""
        try:
            record = self.db.query(DBReminderRecord).join(DBReminderSetting).filter(
                and_(
                    DBReminderRecord.id == record_id,
                    DBReminderSetting.user_id == user_id
                )
            ).first()
            
            if not record:
                return False
            
            record.status = ReminderStatus.SENT
            record.sent_at = datetime.now(UTC)
            record.updated_at = datetime.now(UTC)
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"标记提醒已发送失败: {str(e)}")
            self.db.rollback()
            raise

    def get_reminder_stats(
        self,
        user_id: UUID,
        days: int = 30
    ) -> ReminderStats:
        """获取提醒统计"""
        try:
            start_date = datetime.now(UTC) - timedelta(days=days)
            
            # 获取统计数据
            total_count = self.db.query(DBReminderRecord).join(DBReminderSetting).filter(
                and_(
                    DBReminderSetting.user_id == user_id,
                    DBReminderRecord.created_at >= start_date
                )
            ).count()
            
            sent_count = self.db.query(DBReminderRecord).join(DBReminderSetting).filter(
                and_(
                    DBReminderSetting.user_id == user_id,
                    DBReminderRecord.status == ReminderStatus.SENT,
                    DBReminderRecord.created_at >= start_date
                )
            ).count()
            
            pending_count = self.db.query(DBReminderRecord).join(DBReminderSetting).filter(
                and_(
                    DBReminderSetting.user_id == user_id,
                    DBReminderRecord.status == ReminderStatus.PENDING,
                    DBReminderRecord.created_at >= start_date
                )
            ).count()
            
            failed_count = self.db.query(DBReminderRecord).join(DBReminderSetting).filter(
                and_(
                    DBReminderSetting.user_id == user_id,
                    DBReminderRecord.status == ReminderStatus.FAILED,
                    DBReminderRecord.created_at >= start_date
                )
            ).count()
            
            return ReminderStats(
                total_reminders=total_count,
                sent_reminders=sent_count,
                pending_reminders=pending_count,
                failed_reminders=failed_count,
                success_rate=float(sent_count / total_count * 100) if total_count > 0 else 0,
                period_days=days
            )
            
        except Exception as e:
            logger.error(f"获取提醒统计失败: {str(e)}")
            raise

    def batch_operations(
        self,
        user_id: UUID,
        operation: ReminderBatchOperation
    ) -> Dict[str, Any]:
        """批量操作"""
        try:
            if operation.action == "mark_sent":
                updated_count = 0
                for record_id in operation.record_ids:
                    if self.mark_reminder_sent(record_id, user_id):
                        updated_count += 1
                
                return {"updated_count": updated_count, "total_requested": len(operation.record_ids)}
            
            elif operation.action == "delete":
                deleted_count = 0
                for record_id in operation.record_ids:
                    record = self.db.query(DBReminderRecord).join(DBReminderSetting).filter(
                        and_(
                            DBReminderRecord.id == record_id,
                            DBReminderSetting.user_id == user_id
                        )
                    ).first()
                    
                    if record:
                        self.db.delete(record)
                        deleted_count += 1
                
                self.db.commit()
                return {"deleted_count": deleted_count, "total_requested": len(operation.record_ids)}
            
            else:
                raise ValueError(f"不支持的批量操作: {operation.action}")
                
        except Exception as e:
            logger.error(f"批量操作失败: {str(e)}")
            self.db.rollback()
            raise

    # ==================== 智能提醒功能 ====================

    def generate_automatic_reminders(self, user_id: UUID) -> int:
        """生成自动提醒"""
        try:
            # 获取用户启用的提醒设置
            settings = self.db.query(DBReminderSetting).filter(
                and_(
                    DBReminderSetting.user_id == user_id,
                    DBReminderSetting.is_enabled == True
                )
            ).all()
            
            created_count = 0
            
            for setting in settings:
                # 检查是否需要创建新的提醒
                if self._should_create_reminder(setting):
                    reminder_date = self._calculate_reminder_date(setting)
                    message = self._generate_reminder_message(setting)
                    
                    record_data = ReminderRecordCreate(
                        setting_id=setting.id,
                        reminder_date=reminder_date,
                        message=message,
                        status=ReminderStatus.PENDING
                    )
                    
                    self.create_reminder_record(record_data, user_id)
                    created_count += 1
            
            logger.info(f"自动生成提醒完成", extra={
                "user_id": str(user_id),
                "created_count": created_count
            })
            
            return created_count
            
        except Exception as e:
            logger.error(f"生成自动提醒失败: {str(e)}")
            raise

    def _should_create_reminder(self, setting: DBReminderSetting) -> bool:
        """判断是否需要创建提醒"""
        # 检查最近是否已经创建过提醒
        recent_reminder = self.db.query(DBReminderRecord).filter(
            and_(
                DBReminderRecord.setting_id == setting.id,
                DBReminderRecord.created_at >= datetime.now(UTC) - timedelta(days=1)
            )
        ).first()
        
        return recent_reminder is None

    def _calculate_reminder_date(self, setting: DBReminderSetting) -> datetime:
        """计算提醒时间"""
        if setting.reminder_type == ReminderType.PAYMENT_DUE:
            # 还款日提醒，提前指定天数
            advance_days = setting.advance_days or 3
            
            # 获取信用卡的账单日
            card = self.db.query(DBCard).filter(DBCard.id == setting.card_id).first()
            if card and card.due_date:
                due_date = datetime.combine(card.due_date, datetime.min.time())
                return due_date - timedelta(days=advance_days)
        
        # 默认返回明天
        return datetime.now(UTC) + timedelta(days=1)

    def _generate_reminder_message(self, setting: DBReminderSetting) -> str:
        """生成提醒消息"""
        if setting.reminder_type == ReminderType.PAYMENT_DUE:
            card = self.db.query(DBCard).filter(DBCard.id == setting.card_id).first()
            if card:
                return f"【还款提醒】您的{card.bank_name}{card.card_name}即将到期，请及时还款"
        
        elif setting.reminder_type == ReminderType.BILL_STATEMENT:
            return "【账单提醒】您有新的账单已生成，请查看"
        
        elif setting.reminder_type == ReminderType.ANNUAL_FEE:
            return "【年费提醒】您的信用卡年费即将产生"
        
        return "【信用卡提醒】您有一个重要的信用卡事项需要关注"