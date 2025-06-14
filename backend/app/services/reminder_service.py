"""
提醒服务
提供还款提醒、年费提醒、账单提醒等功能
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, extract, case
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta, date
from decimal import Decimal
from uuid import UUID
import calendar

from app.models.database.reminder import ReminderSetting, ReminderRecord
from app.models.database.card import CreditCard
from app.models.database.fee_waiver import AnnualFeeRecord
from app.models.schemas.reminder import (
    ReminderSettingCreate, ReminderSettingUpdate, ReminderSettingResponse,
    ReminderRecordCreate, ReminderRecordUpdate, ReminderRecordResponse,
    ReminderStatisticsResponse, UpcomingRemindersResponse
)
from app.core.exceptions.custom import (
    ResourceNotFoundError, ValidationError, BusinessRuleError
)
from app.core.logging.logger import app_logger as logger


class ReminderService:
    """提醒服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========== 提醒设置管理 ==========
    
    def create_reminder_setting(self, user_id: UUID, setting_data: dict) -> dict:
        """创建提醒设置"""
        try:
            # 验证信用卡是否属于用户（如果指定了卡片）
            if setting_data.get('card_id'):
                card = self.db.query(CreditCard).filter(
                    and_(
                        CreditCard.id == setting_data['card_id'],
                        CreditCard.user_id == user_id
                    )
                ).first()
                
                if not card:
                    raise ResourceNotFoundError("信用卡不存在或不属于当前用户")
            
            # 检查是否已存在相同类型的提醒设置
            existing_setting = self.db.query(ReminderSetting).filter(
                and_(
                    ReminderSetting.user_id == user_id,
                    ReminderSetting.card_id == setting_data.get('card_id'),
                    ReminderSetting.reminder_type == setting_data['reminder_type']
                )
            ).first()
            
            if existing_setting:
                raise BusinessRuleError(f"该信用卡的{setting_data['reminder_type']}提醒设置已存在")
            
            # 创建提醒设置
            setting = ReminderSetting(
                user_id=user_id,
                card_id=setting_data.get('card_id'),
                reminder_type=setting_data['reminder_type'],
                reminder_name=setting_data['reminder_name'],
                advance_days=setting_data.get('advance_days', 3),
                reminder_time=setting_data.get('reminder_time'),
                is_enabled=setting_data.get('is_enabled', True),
                notification_methods=setting_data.get('notification_methods', ['app']),
                custom_message=setting_data.get('custom_message'),
                repeat_interval=setting_data.get('repeat_interval'),
                notes=setting_data.get('notes')
            )
            
            self.db.add(setting)
            self.db.commit()
            self.db.refresh(setting)
            
            logger.info(f"创建提醒设置成功: {setting.id}, 用户: {user_id}")
            return self._to_setting_response(setting)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建提醒设置失败: 用户: {user_id}, 错误: {str(e)}")
            raise
    
    def get_reminder_setting(self, user_id: UUID, setting_id: UUID) -> dict:
        """获取提醒设置详情"""
        setting = self.db.query(ReminderSetting).filter(
            and_(
                ReminderSetting.id == setting_id,
                ReminderSetting.user_id == user_id
            )
        ).first()
        
        if not setting:
            raise ResourceNotFoundError("提醒设置不存在")
        
        return self._to_setting_response(setting)
    
    def update_reminder_setting(self, user_id: UUID, setting_id: UUID, 
                               setting_data: dict) -> dict:
        """更新提醒设置"""
        try:
            setting = self.db.query(ReminderSetting).filter(
                and_(
                    ReminderSetting.id == setting_id,
                    ReminderSetting.user_id == user_id
                )
            ).first()
            
            if not setting:
                raise ResourceNotFoundError("提醒设置不存在")
            
            # 验证信用卡（如果更新）
            if setting_data.get('card_id') and setting_data['card_id'] != setting.card_id:
                card = self.db.query(CreditCard).filter(
                    and_(
                        CreditCard.id == setting_data['card_id'],
                        CreditCard.user_id == user_id
                    )
                ).first()
                if not card:
                    raise ResourceNotFoundError("信用卡不存在或不属于当前用户")
            
            # 更新字段
            for field, value in setting_data.items():
                if hasattr(setting, field):
                    setattr(setting, field, value)
            
            self.db.commit()
            self.db.refresh(setting)
            
            logger.info(f"更新提醒设置成功: {setting_id}, 用户: {user_id}")
            return self._to_setting_response(setting)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新提醒设置失败: {setting_id}, 用户: {user_id}, 错误: {str(e)}")
            raise
    
    def delete_reminder_setting(self, user_id: UUID, setting_id: UUID) -> bool:
        """删除提醒设置"""
        try:
            setting = self.db.query(ReminderSetting).filter(
                and_(
                    ReminderSetting.id == setting_id,
                    ReminderSetting.user_id == user_id
                )
            ).first()
            
            if not setting:
                raise ResourceNotFoundError("提醒设置不存在")
            
            # 删除关联的提醒记录
            self.db.query(ReminderRecord).filter(
                ReminderRecord.setting_id == setting_id
            ).delete()
            
            self.db.delete(setting)
            self.db.commit()
            
            logger.info(f"删除提醒设置成功: {setting_id}, 用户: {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除提醒设置失败: {setting_id}, 用户: {user_id}, 错误: {str(e)}")
            raise
    
    def get_user_reminder_settings(self, user_id: UUID, page: int = 1, page_size: int = 20,
                                  card_id: Optional[UUID] = None, reminder_type: Optional[str] = None,
                                  is_enabled: Optional[bool] = None) -> Tuple[List[dict], int]:
        """获取用户提醒设置列表（支持筛选和分页）"""
        
        query = self.db.query(ReminderSetting).filter(ReminderSetting.user_id == user_id)
        
        # 应用筛选条件
        if card_id:
            query = query.filter(ReminderSetting.card_id == card_id)
        
        if reminder_type:
            query = query.filter(ReminderSetting.reminder_type == reminder_type)
        
        if is_enabled is not None:
            query = query.filter(ReminderSetting.is_enabled == is_enabled)
        
        # 获取总数
        total = query.count()
        
        # 分页和排序
        settings = query.order_by(desc(ReminderSetting.created_at))\
                        .offset((page - 1) * page_size)\
                        .limit(page_size)\
                        .all()
        
        setting_responses = [self._to_setting_response(setting) for setting in settings]
        
        logger.info(f"获取用户提醒设置列表成功: 用户: {user_id}, 总数: {total}")
        return setting_responses, total
    
    # ========== 提醒记录管理 ==========
    
    def create_reminder_record(self, user_id: UUID, record_data: dict) -> dict:
        """创建提醒记录"""
        try:
            # 验证提醒设置是否属于用户
            setting = self.db.query(ReminderSetting).filter(
                and_(
                    ReminderSetting.id == record_data['setting_id'],
                    ReminderSetting.user_id == user_id
                )
            ).first()
            
            if not setting:
                raise ResourceNotFoundError("提醒设置不存在或不属于当前用户")
            
            # 创建提醒记录
            record = ReminderRecord(
                setting_id=record_data['setting_id'],
                reminder_date=record_data['reminder_date'],
                reminder_time=record_data.get('reminder_time') or setting.reminder_time,
                message=record_data.get('message') or setting.custom_message,
                status=record_data.get('status', 'pending'),
                sent_at=record_data.get('sent_at'),
                read_at=record_data.get('read_at'),
                notes=record_data.get('notes')
            )
            
            self.db.add(record)
            self.db.commit()
            self.db.refresh(record)
            
            logger.info(f"创建提醒记录成功: {record.id}, 用户: {user_id}")
            return self._to_record_response(record)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建提醒记录失败: 用户: {user_id}, 错误: {str(e)}")
            raise
    
    def get_reminder_record(self, user_id: UUID, record_id: UUID) -> dict:
        """获取提醒记录详情"""
        record = self.db.query(ReminderRecord).join(ReminderSetting).filter(
            and_(
                ReminderRecord.id == record_id,
                ReminderSetting.user_id == user_id
            )
        ).first()
        
        if not record:
            raise ResourceNotFoundError("提醒记录不存在")
        
        return self._to_record_response(record)
    
    def mark_reminder_as_read(self, user_id: UUID, record_id: UUID) -> dict:
        """标记提醒为已读"""
        try:
            record = self.db.query(ReminderRecord).join(ReminderSetting).filter(
                and_(
                    ReminderRecord.id == record_id,
                    ReminderSetting.user_id == user_id
                )
            ).first()
            
            if not record:
                raise ResourceNotFoundError("提醒记录不存在")
            
            record.status = 'read'
            record.read_at = datetime.now()
            
            self.db.commit()
            self.db.refresh(record)
            
            logger.info(f"标记提醒为已读成功: {record_id}, 用户: {user_id}")
            return self._to_record_response(record)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"标记提醒为已读失败: {record_id}, 用户: {user_id}, 错误: {str(e)}")
            raise
    
    def get_user_reminder_records(self, user_id: UUID, page: int = 1, page_size: int = 20,
                                 setting_id: Optional[UUID] = None, status: Optional[str] = None,
                                 start_date: Optional[date] = None, end_date: Optional[date] = None) -> Tuple[List[dict], int]:
        """获取用户提醒记录列表（支持筛选和分页）"""
        
        query = self.db.query(ReminderRecord).join(ReminderSetting).filter(
            ReminderSetting.user_id == user_id
        )
        
        # 应用筛选条件
        if setting_id:
            query = query.filter(ReminderRecord.setting_id == setting_id)
        
        if status:
            query = query.filter(ReminderRecord.status == status)
        
        if start_date:
            query = query.filter(ReminderRecord.reminder_date >= start_date)
        
        if end_date:
            query = query.filter(ReminderRecord.reminder_date <= end_date)
        
        # 获取总数
        total = query.count()
        
        # 分页和排序
        records = query.order_by(desc(ReminderRecord.reminder_date), desc(ReminderRecord.reminder_time))\
                       .offset((page - 1) * page_size)\
                       .limit(page_size)\
                       .all()
        
        record_responses = [self._to_record_response(record) for record in records]
        
        logger.info(f"获取用户提醒记录列表成功: 用户: {user_id}, 总数: {total}")
        return record_responses, total
    
    # ========== 自动提醒生成 ==========
    
    def generate_upcoming_reminders(self, user_id: UUID, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """生成即将到来的提醒"""
        
        # 获取用户启用的提醒设置
        settings = self.db.query(ReminderSetting).filter(
            and_(
                ReminderSetting.user_id == user_id,
                ReminderSetting.is_enabled == True
            )
        ).all()
        
        upcoming_reminders = []
        current_date = date.today()
        end_date = current_date + timedelta(days=days_ahead)
        
        for setting in settings:
            if setting.reminder_type == 'payment_due':
                # 还款提醒
                if setting.card and setting.card.billing_date:
                    # 计算下一个账单日
                    next_billing_date = self._calculate_next_billing_date(setting.card.billing_date)
                    reminder_date = next_billing_date - timedelta(days=setting.advance_days)
                    
                    if current_date <= reminder_date <= end_date:
                        upcoming_reminders.append({
                            'setting_id': str(setting.id),
                            'reminder_type': setting.reminder_type,
                            'reminder_name': setting.reminder_name,
                            'reminder_date': reminder_date,
                            'reminder_time': setting.reminder_time,
                            'card_name': setting.card.card_name,
                            'message': f"信用卡 {setting.card.card_name} 将在 {next_billing_date} 到期还款",
                            'priority': 'high'
                        })
            
            elif setting.reminder_type == 'annual_fee':
                # 年费提醒
                if setting.card:
                    # 查询年费记录
                    current_year = datetime.now().year
                    fee_records = self.db.query(AnnualFeeRecord).join(AnnualFeeRecord.rule).filter(
                        and_(
                            AnnualFeeRecord.rule.has(card_id=setting.card_id),
                            AnnualFeeRecord.fee_year == current_year,
                            AnnualFeeRecord.status == 'pending'
                        )
                    ).all()
                    
                    for record in fee_records:
                        if record.due_date:
                            reminder_date = record.due_date - timedelta(days=setting.advance_days)
                            
                            if current_date <= reminder_date <= end_date:
                                upcoming_reminders.append({
                                    'setting_id': str(setting.id),
                                    'reminder_type': setting.reminder_type,
                                    'reminder_name': setting.reminder_name,
                                    'reminder_date': reminder_date,
                                    'reminder_time': setting.reminder_time,
                                    'card_name': setting.card.card_name,
                                    'message': f"信用卡 {setting.card.card_name} 年费 ¥{record.actual_fee} 将在 {record.due_date} 到期",
                                    'priority': 'medium'
                                })
            
            elif setting.reminder_type == 'card_expiry':
                # 信用卡到期提醒
                if setting.card and setting.card.expiry_year and setting.card.expiry_month:
                    # 计算信用卡到期日期
                    expiry_date = date(setting.card.expiry_year, setting.card.expiry_month, 1)
                    # 获取月份的最后一天
                    last_day = calendar.monthrange(setting.card.expiry_year, setting.card.expiry_month)[1]
                    expiry_date = date(setting.card.expiry_year, setting.card.expiry_month, last_day)
                    
                    reminder_date = expiry_date - timedelta(days=setting.advance_days)
                    
                    if current_date <= reminder_date <= end_date:
                        upcoming_reminders.append({
                            'setting_id': str(setting.id),
                            'reminder_type': setting.reminder_type,
                            'reminder_name': setting.reminder_name,
                            'reminder_date': reminder_date,
                            'reminder_time': setting.reminder_time,
                            'card_name': setting.card.card_name,
                            'message': f"信用卡 {setting.card.card_name} 将在 {expiry_date} 到期",
                            'priority': 'high'
                        })
        
        # 按日期和优先级排序
        priority_order = {'high': 1, 'medium': 2, 'low': 3}
        upcoming_reminders.sort(key=lambda x: (x['reminder_date'], priority_order.get(x['priority'], 3)))
        
        logger.info(f"生成即将到来的提醒成功: 用户: {user_id}, 数量: {len(upcoming_reminders)}")
        return upcoming_reminders
    
    def create_automatic_reminders(self, user_id: UUID) -> int:
        """自动创建提醒记录"""
        
        upcoming_reminders = self.generate_upcoming_reminders(user_id, days_ahead=7)  # 7天内的提醒
        created_count = 0
        
        for reminder_data in upcoming_reminders:
            # 检查是否已存在相同的提醒记录
            existing_record = self.db.query(ReminderRecord).filter(
                and_(
                    ReminderRecord.setting_id == reminder_data['setting_id'],
                    ReminderRecord.reminder_date == reminder_data['reminder_date'],
                    ReminderRecord.status.in_(['pending', 'sent'])
                )
            ).first()
            
            if not existing_record:
                try:
                    record = ReminderRecord(
                        setting_id=UUID(reminder_data['setting_id']),
                        reminder_date=reminder_data['reminder_date'],
                        reminder_time=reminder_data['reminder_time'],
                        message=reminder_data['message'],
                        status='pending'
                    )
                    
                    self.db.add(record)
                    created_count += 1
                    
                except Exception as e:
                    logger.error(f"创建自动提醒记录失败: {str(e)}")
                    continue
        
        if created_count > 0:
            self.db.commit()
        
        logger.info(f"自动创建提醒记录成功: 用户: {user_id}, 创建数量: {created_count}")
        return created_count
    
    # ========== 提醒统计分析 ==========
    
    def get_reminder_statistics(self, user_id: UUID) -> dict:
        """获取提醒统计数据"""
        
        # 基础统计
        total_settings = self.db.query(ReminderSetting).filter(
            ReminderSetting.user_id == user_id
        ).count()
        
        active_settings = self.db.query(ReminderSetting).filter(
            and_(
                ReminderSetting.user_id == user_id,
                ReminderSetting.is_enabled == True
            )
        ).count()
        
        # 最近30天的提醒记录统计
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_records = self.db.query(ReminderRecord).join(ReminderSetting).filter(
            and_(
                ReminderSetting.user_id == user_id,
                ReminderRecord.reminder_date >= thirty_days_ago
            )
        ).all()
        
        total_reminders = len(recent_records)
        sent_reminders = len([r for r in recent_records if r.status == 'sent'])
        read_reminders = len([r for r in recent_records if r.status == 'read'])
        pending_reminders = len([r for r in recent_records if r.status == 'pending'])
        
        # 按类型统计
        type_distribution = {}
        for setting in self.db.query(ReminderSetting).filter(ReminderSetting.user_id == user_id).all():
            reminder_type = setting.reminder_type
            type_distribution[reminder_type] = type_distribution.get(reminder_type, 0) + 1
        
        # 即将到来的提醒
        upcoming_count = len(self.generate_upcoming_reminders(user_id, days_ahead=7))
        
        return {
            'total_settings': total_settings,
            'active_settings': active_settings,
            'total_reminders_30days': total_reminders,
            'sent_reminders_30days': sent_reminders,
            'read_reminders_30days': read_reminders,
            'pending_reminders_30days': pending_reminders,
            'upcoming_reminders_7days': upcoming_count,
            'type_distribution': type_distribution,
            'read_rate': round((read_reminders / sent_reminders * 100), 2) if sent_reminders > 0 else 0.0
        }
    
    def get_upcoming_reminders(self, user_id: UUID, days_ahead: int = 7) -> dict:
        """获取即将到来的提醒"""
        
        upcoming_reminders = self.generate_upcoming_reminders(user_id, days_ahead)
        
        # 按优先级分组
        high_priority = [r for r in upcoming_reminders if r['priority'] == 'high']
        medium_priority = [r for r in upcoming_reminders if r['priority'] == 'medium']
        low_priority = [r for r in upcoming_reminders if r['priority'] == 'low']
        
        return {
            'total_upcoming': len(upcoming_reminders),
            'high_priority_count': len(high_priority),
            'medium_priority_count': len(medium_priority),
            'low_priority_count': len(low_priority),
            'reminders': upcoming_reminders,
            'analysis_period': f"{days_ahead}天"
        }
    
    # ========== 私有方法 ==========
    
    def _calculate_next_billing_date(self, billing_day: int) -> date:
        """计算下一个账单日"""
        today = date.today()
        
        # 尝试当月的账单日
        try:
            next_billing = date(today.year, today.month, billing_day)
            if next_billing > today:
                return next_billing
        except ValueError:
            # 如果当月没有这一天（如2月30日），使用月末
            last_day = calendar.monthrange(today.year, today.month)[1]
            next_billing = date(today.year, today.month, min(billing_day, last_day))
            if next_billing > today:
                return next_billing
        
        # 如果当月的账单日已过，计算下个月
        if today.month == 12:
            next_year = today.year + 1
            next_month = 1
        else:
            next_year = today.year
            next_month = today.month + 1
        
        try:
            return date(next_year, next_month, billing_day)
        except ValueError:
            # 如果下个月没有这一天，使用月末
            last_day = calendar.monthrange(next_year, next_month)[1]
            return date(next_year, next_month, min(billing_day, last_day))
    
    def _to_setting_response(self, setting: ReminderSetting) -> dict:
        """转换为提醒设置响应模型"""
        return {
            'id': str(setting.id),
            'card_id': str(setting.card_id) if setting.card_id else None,
            'reminder_type': setting.reminder_type,
            'reminder_name': setting.reminder_name,
            'advance_days': setting.advance_days,
            'reminder_time': setting.reminder_time,
            'is_enabled': setting.is_enabled,
            'notification_methods': setting.notification_methods,
            'custom_message': setting.custom_message,
            'repeat_interval': setting.repeat_interval,
            'notes': setting.notes,
            'created_at': setting.created_at,
            'updated_at': setting.updated_at,
            # 关联数据
            'card_name': setting.card.card_name if setting.card else None
        }
    
    def _to_record_response(self, record: ReminderRecord) -> dict:
        """转换为提醒记录响应模型"""
        return {
            'id': str(record.id),
            'setting_id': str(record.setting_id),
            'reminder_date': record.reminder_date,
            'reminder_time': record.reminder_time,
            'message': record.message,
            'status': record.status,
            'sent_at': record.sent_at,
            'read_at': record.read_at,
            'notes': record.notes,
            'created_at': record.created_at,
            'updated_at': record.updated_at,
            # 关联数据
            'reminder_type': record.setting.reminder_type if record.setting else None,
            'card_name': record.setting.card.card_name if record.setting and record.setting.card else None
        } 