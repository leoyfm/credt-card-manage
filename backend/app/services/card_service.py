"""
信用卡管理服务层

提供信用卡和银行相关的业务逻辑处理
"""

from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from datetime import datetime, timedelta
import calendar

from app.models.database.card import CreditCard, Bank
from app.models.database.user import User
from app.models.schemas.card import (
    CreditCardCreate, CreditCardUpdate, CreditCardQueryParams,
    CreditCardResponse, CreditCardSummary, CreditCardStatistics,
    BankCreate, BankUpdate, BankResponse
)
from app.core.exceptions.custom import (
    ResourceNotFoundError, BusinessRuleError, ValidationError
)
from app.core.logging.logger import app_logger as logger
from app.utils.pagination import apply_service_pagination


class CardService:
    """信用卡管理服务"""

    def __init__(self, db: Session):
        self.db = db

    # ============ 银行管理 ============

    def create_bank(self, bank_data: BankCreate) -> BankResponse:
        """创建银行"""
        try:
            # 检查银行代码是否已存在
            existing_bank = self.db.query(Bank).filter(Bank.bank_code == bank_data.bank_code).first()
            if existing_bank:
                raise BusinessRuleError(f"银行代码 {bank_data.bank_code} 已存在")

            # 创建银行
            bank = Bank(**bank_data.model_dump())
            self.db.add(bank)
            self.db.commit()
            self.db.refresh(bank)

            logger.info(f"创建银行成功: {bank.bank_name} (ID: {bank.id})")
            return BankResponse.model_validate(bank)

        except Exception as e:
            self.db.rollback()
            logger.error(f"创建银行失败: {str(e)}")
            raise

    def get_banks(self, active_only: bool = True) -> List[BankResponse]:
        """获取银行列表"""
        try:
            query = self.db.query(Bank)
            if active_only:
                query = query.filter(Bank.is_active == True)
            
            banks = query.order_by(Bank.sort_order, Bank.bank_name).all()
            return [BankResponse.model_validate(bank) for bank in banks]

        except Exception as e:
            logger.error(f"获取银行列表失败: {str(e)}")
            raise

    def get_bank_by_id(self, bank_id: UUID) -> Optional[BankResponse]:
        """根据ID获取银行"""
        try:
            bank = self.db.query(Bank).filter(Bank.id == bank_id).first()
            return BankResponse.model_validate(bank) if bank else None

        except Exception as e:
            logger.error(f"获取银行详情失败: {str(e)}")
            raise

    def get_or_create_bank_by_name(self, bank_name: str) -> Bank:
        """根据银行名称获取或创建银行"""
        try:
            # 先尝试查找现有银行
            bank = self.db.query(Bank).filter(Bank.bank_name == bank_name).first()
            if bank:
                return bank

            # 如果不存在，创建新银行
            bank_code = bank_name[:10].upper()  # 简单生成银行代码
            bank = Bank(
                bank_code=bank_code,
                bank_name=bank_name,
                is_active=True
            )
            self.db.add(bank)
            self.db.flush()  # 获取ID但不提交事务
            
            logger.info(f"自动创建银行: {bank_name}")
            return bank

        except Exception as e:
            logger.error(f"获取或创建银行失败: {str(e)}")
            raise

    # ============ 信用卡管理 ============

    def create_credit_card(self, user_id: UUID, card_data: CreditCardCreate) -> CreditCardResponse:
        """创建信用卡"""
        try:
            # 验证用户存在
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ResourceNotFoundError("用户不存在")

            # 处理银行信息
            bank = None
            if card_data.bank_id:
                bank = self.db.query(Bank).filter(Bank.id == card_data.bank_id).first()
                if not bank:
                    raise ResourceNotFoundError("银行不存在")
            elif card_data.bank_name:
                bank = self.get_or_create_bank_by_name(card_data.bank_name)

            # 检查卡号是否已存在（同一用户）
            existing_card = self.db.query(CreditCard).filter(
                and_(
                    CreditCard.user_id == user_id,
                    CreditCard.card_number == card_data.card_number
                )
            ).first()
            if existing_card:
                raise BusinessRuleError("该卡号已存在")

            # 创建信用卡数据
            card_dict = card_data.model_dump(exclude={'bank_id', 'bank_name'})
            card_dict['user_id'] = user_id
            if bank:
                card_dict['bank_id'] = bank.id

            # 设置可用额度
            card_dict['available_limit'] = card_data.credit_limit

            # 如果是第一张卡，自动设为主卡
            if not self.db.query(CreditCard).filter(CreditCard.user_id == user_id).first():
                card_dict['is_primary'] = True

            card = CreditCard(**card_dict)
            self.db.add(card)
            self.db.commit()
            self.db.refresh(card)

            # 加载关联数据
            card = self.db.query(CreditCard).options(joinedload(CreditCard.bank)).filter(
                CreditCard.id == card.id
            ).first()

            logger.info(f"用户 {user_id} 创建信用卡成功: {card.card_name} (ID: {card.id})")
            return self._build_card_response(card)

        except Exception as e:
            self.db.rollback()
            logger.error(f"创建信用卡失败: {str(e)}")
            raise

    def get_user_cards(self, user_id: UUID, params: CreditCardQueryParams) -> Tuple[List[CreditCardResponse], int]:
        """获取用户信用卡列表"""
        try:
            # 构建查询
            query = self.db.query(CreditCard).options(joinedload(CreditCard.bank)).filter(
                CreditCard.user_id == user_id
            )

            # 应用筛选条件
            if params.keyword:
                keyword_filter = or_(
                    CreditCard.card_name.ilike(f"%{params.keyword}%"),
                    Bank.bank_name.ilike(f"%{params.keyword}%")
                )
                query = query.join(Bank, CreditCard.bank_id == Bank.id, isouter=True).filter(keyword_filter)

            if params.status:
                query = query.filter(CreditCard.status == params.status)

            if params.bank_id:
                query = query.filter(CreditCard.bank_id == params.bank_id)

            if params.card_type:
                query = query.filter(CreditCard.card_type == params.card_type)

            if params.is_primary is not None:
                query = query.filter(CreditCard.is_primary == params.is_primary)

            if params.expiring_soon:
                # 查询3个月内过期的卡片
                future_date = datetime.now() + timedelta(days=90)
                query = query.filter(
                    or_(
                        CreditCard.expiry_year < future_date.year,
                        and_(
                            CreditCard.expiry_year == future_date.year,
                            CreditCard.expiry_month <= future_date.month
                        )
                    )
                )

            # 应用分页和排序
            cards, total = apply_service_pagination(
                query,
                params.page,
                params.page_size,
                order_by=[desc(CreditCard.is_primary), CreditCard.created_at.desc()]
            )

            # 构建响应
            card_responses = [self._build_card_response(card) for card in cards]

            logger.info(f"获取用户 {user_id} 信用卡列表成功，共 {total} 张卡片")
            return card_responses, total

        except Exception as e:
            logger.error(f"获取用户信用卡列表失败: {str(e)}")
            raise

    def get_card_by_id(self, user_id: UUID, card_id: UUID) -> Optional[CreditCardResponse]:
        """获取信用卡详情"""
        try:
            card = self.db.query(CreditCard).options(joinedload(CreditCard.bank)).filter(
                and_(
                    CreditCard.id == card_id,
                    CreditCard.user_id == user_id
                )
            ).first()

            if not card:
                return None

            return self._build_card_response(card)

        except Exception as e:
            logger.error(f"获取信用卡详情失败: {str(e)}")
            raise

    def update_credit_card(self, user_id: UUID, card_id: UUID, update_data: CreditCardUpdate) -> CreditCardResponse:
        """更新信用卡"""
        try:
            # 获取信用卡
            card = self.db.query(CreditCard).filter(
                and_(
                    CreditCard.id == card_id,
                    CreditCard.user_id == user_id
                )
            ).first()

            if not card:
                raise ResourceNotFoundError("信用卡不存在")

            # 更新字段
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                setattr(card, field, value)

            # 如果更新了信用额度，同时更新可用额度
            if 'credit_limit' in update_dict:
                used_limit = card.used_limit or 0
                card.available_limit = update_data.credit_limit - used_limit

            self.db.commit()
            self.db.refresh(card)

            # 重新加载关联数据
            card = self.db.query(CreditCard).options(joinedload(CreditCard.bank)).filter(
                CreditCard.id == card_id
            ).first()

            logger.info(f"更新信用卡成功: {card.card_name} (ID: {card_id})")
            return self._build_card_response(card)

        except Exception as e:
            self.db.rollback()
            logger.error(f"更新信用卡失败: {str(e)}")
            raise

    def update_card_status(self, user_id: UUID, card_id: UUID, status: str, reason: Optional[str] = None) -> CreditCardResponse:
        """更新信用卡状态"""
        try:
            card = self.db.query(CreditCard).filter(
                and_(
                    CreditCard.id == card_id,
                    CreditCard.user_id == user_id
                )
            ).first()

            if not card:
                raise ResourceNotFoundError("信用卡不存在")

            old_status = card.status
            card.status = status
            
            # 记录状态变更原因到备注
            if reason:
                status_note = f"状态变更: {old_status} -> {status}, 原因: {reason}"
                if card.notes:
                    card.notes += f"\n{status_note}"
                else:
                    card.notes = status_note

            self.db.commit()
            self.db.refresh(card)

            logger.info(f"更新信用卡状态成功: {card.card_name} {old_status} -> {status}")
            return self._build_card_response(card)

        except Exception as e:
            self.db.rollback()
            logger.error(f"更新信用卡状态失败: {str(e)}")
            raise

    def delete_credit_card(self, user_id: UUID, card_id: UUID) -> bool:
        """删除信用卡"""
        try:
            card = self.db.query(CreditCard).filter(
                and_(
                    CreditCard.id == card_id,
                    CreditCard.user_id == user_id
                )
            ).first()

            if not card:
                raise ResourceNotFoundError("信用卡不存在")

            # 检查是否有未完成的交易或年费记录
            # 这里可以添加业务规则检查

            card_name = card.card_name
            self.db.delete(card)
            self.db.commit()

            logger.info(f"删除信用卡成功: {card_name} (ID: {card_id})")
            return True

        except Exception as e:
            self.db.rollback()
            logger.error(f"删除信用卡失败: {str(e)}")
            raise

    def get_card_summary(self, user_id: UUID) -> CreditCardSummary:
        """获取信用卡摘要统计"""
        try:
            # 基础统计
            total_cards = self.db.query(CreditCard).filter(CreditCard.user_id == user_id).count()
            active_cards = self.db.query(CreditCard).filter(
                and_(
                    CreditCard.user_id == user_id,
                    CreditCard.status == 'active'
                )
            ).count()

            # 额度统计
            limit_stats = self.db.query(
                func.sum(CreditCard.credit_limit).label('total_credit'),
                func.sum(CreditCard.used_limit).label('total_used'),
                func.sum(CreditCard.available_limit).label('total_available')
            ).filter(
                and_(
                    CreditCard.user_id == user_id,
                    CreditCard.status == 'active'
                )
            ).first()

            total_credit_limit = limit_stats.total_credit or 0
            total_used_limit = limit_stats.total_used or 0
            total_available_limit = limit_stats.total_available or 0

            # 计算平均使用率
            average_utilization_rate = 0.0
            if total_credit_limit > 0:
                average_utilization_rate = float(total_used_limit) / float(total_credit_limit) * 100

            # 即将过期的卡片数
            future_date = datetime.now() + timedelta(days=90)
            cards_expiring_soon = self.db.query(CreditCard).filter(
                and_(
                    CreditCard.user_id == user_id,
                    CreditCard.status == 'active',
                    or_(
                        CreditCard.expiry_year < future_date.year,
                        and_(
                            CreditCard.expiry_year == future_date.year,
                            CreditCard.expiry_month <= future_date.month
                        )
                    )
                )
            ).count()

            # 计算最长免息天数
            max_interest_free_days = self._calculate_max_interest_free_days(user_id)

            return CreditCardSummary(
                total_cards=total_cards,
                active_cards=active_cards,
                total_credit_limit=total_credit_limit,
                total_used_limit=total_used_limit,
                total_available_limit=total_available_limit,
                average_utilization_rate=round(average_utilization_rate, 2),
                cards_expiring_soon=cards_expiring_soon,
                max_interest_free_days=max_interest_free_days
            )

        except Exception as e:
            logger.error(f"获取信用卡摘要失败: {str(e)}")
            raise

    def get_card_statistics(self, user_id: UUID) -> CreditCardStatistics:
        """获取信用卡详细统计"""
        try:
            summary = self.get_card_summary(user_id)

            # 按银行统计
            by_bank = self.db.query(
                Bank.bank_name,
                func.count(CreditCard.id).label('count'),
                func.sum(CreditCard.credit_limit).label('total_limit')
            ).join(CreditCard).filter(
                CreditCard.user_id == user_id
            ).group_by(Bank.bank_name).all()

            # 按状态统计
            by_status = self.db.query(
                CreditCard.status,
                func.count(CreditCard.id).label('count')
            ).filter(
                CreditCard.user_id == user_id
            ).group_by(CreditCard.status).all()

            # 按卡片等级统计
            by_card_level = self.db.query(
                CreditCard.card_level,
                func.count(CreditCard.id).label('count')
            ).filter(
                CreditCard.user_id == user_id
            ).group_by(CreditCard.card_level).all()

            # 使用率分布
            utilization_distribution = []
            ranges = [(0, 30), (30, 60), (60, 80), (80, 100)]
            for min_rate, max_rate in ranges:
                count = self.db.query(CreditCard).filter(
                    and_(
                        CreditCard.user_id == user_id,
                        CreditCard.status == 'active',
                        CreditCard.credit_limit > 0,
                        (CreditCard.used_limit / CreditCard.credit_limit * 100) >= min_rate,
                        (CreditCard.used_limit / CreditCard.credit_limit * 100) < max_rate
                    )
                ).count()
                utilization_distribution.append({
                    'range': f'{min_rate}-{max_rate}%',
                    'count': count
                })

            return CreditCardStatistics(
                summary=summary,
                by_bank=[{'bank_name': item.bank_name, 'count': item.count, 'total_limit': float(item.total_limit or 0)} for item in by_bank],
                by_status=[{'status': item.status, 'count': item.count} for item in by_status],
                by_card_level=[{'card_level': item.card_level or '未分级', 'count': item.count} for item in by_card_level],
                utilization_distribution=utilization_distribution
            )

        except Exception as e:
            logger.error(f"获取信用卡统计失败: {str(e)}")
            raise

    def _build_card_response(self, card: CreditCard) -> CreditCardResponse:
        """构建信用卡响应对象"""
        try:
            # 安全地获取银行信息
            bank_data = None
            if card.bank:
                bank_data = BankResponse.model_validate(card.bank)
            
            # 安全地获取计算属性
            expiry_display = f"{card.expiry_month:02d}/{str(card.expiry_year)[-2:]}"
            
            # 安全地计算是否过期
            from datetime import datetime
            now = datetime.now()
            is_expired = (card.expiry_year < now.year or 
                         (card.expiry_year == now.year and card.expiry_month < now.month))
            
            # 安全地计算使用率
            credit_utilization_rate = 0.0
            if card.credit_limit and float(card.credit_limit) > 0:
                credit_utilization_rate = float(card.used_limit or 0) / float(card.credit_limit) * 100
            
            response_data = {
                'id': card.id,
                'user_id': card.user_id,
                'bank_id': card.bank_id,
                'card_name': card.card_name,
                'card_number': card.card_number,
                'card_type': card.card_type,
                'card_network': card.card_network,
                'card_level': card.card_level,
                'credit_limit': card.credit_limit,
                'available_limit': card.available_limit,
                'used_limit': card.used_limit,
                'expiry_month': card.expiry_month,
                'expiry_year': card.expiry_year,
                'billing_date': card.billing_date,
                'due_date': card.due_date,
                'annual_fee': card.annual_fee,
                'fee_waivable': card.fee_waivable,
                'fee_auto_deduct': card.fee_auto_deduct,
                'fee_due_month': card.fee_due_month,
                'features': card.features or [],
                'points_rate': card.points_rate,
                'cashback_rate': card.cashback_rate,
                'status': card.status,
                'is_primary': card.is_primary,
                'notes': card.notes,
                'created_at': card.created_at,
                'updated_at': card.updated_at,
                'bank': bank_data,
                'expiry_display': expiry_display,
                'is_expired': is_expired,
                'credit_utilization_rate': round(credit_utilization_rate, 2)
            }
            
            return CreditCardResponse(**response_data)
            
        except Exception as e:
            logger.error(f"构建信用卡响应对象失败: {str(e)}")
            raise

    def _calculate_max_interest_free_days(self, user_id: UUID) -> int:
        """计算用户所有信用卡中的最长免息天数
        
        算法说明：
        1. 从今天开始消费，计算到最晚还款日的天数
        2. 考虑账单日和还款日的关系：
           - 如果还款日 > 账单日：同月还款
           - 如果还款日 < 账单日：跨月还款
        3. 根据今天与账单日的关系，计算最优消费时机的免息天数
        
        示例：
        - 今天12号，账单日20号，还款日24号：从12号消费到24号 = 12天
        - 今天12号，账单日20号，还款日4号：从12号消费到下月4号 = 22天
        - 今天25号，账单日20号，还款日4号：从25号消费到下下月4号 = 40天
        """
        try:
            from datetime import datetime, timedelta
            import calendar
            
            # 获取用户所有有账单日和还款日的活跃信用卡
            cards = self.db.query(CreditCard).filter(
                and_(
                    CreditCard.user_id == user_id,
                    CreditCard.status == 'active',
                    CreditCard.billing_date.isnot(None),
                    CreditCard.due_date.isnot(None)
                )
            ).all()

            if not cards:
                return 0

            today = datetime.now().date()
            max_days = 0
            
            for card in cards:
                billing_date = card.billing_date  # 账单日
                due_date = card.due_date          # 还款日
                
                # 计算当前月份的账单日和还款日
                current_year = today.year
                current_month = today.month
                
                # 构造当前月的账单日
                try:
                    current_billing_date = datetime(current_year, current_month, billing_date).date()
                except ValueError:
                    # 处理月末日期不存在的情况（如2月30日）
                    last_day = calendar.monthrange(current_year, current_month)[1]
                    current_billing_date = datetime(current_year, current_month, min(billing_date, last_day)).date()
                
                # 计算还款日期
                if due_date >= billing_date:
                    # 同月还款：还款日在账单日当月或之后
                    try:
                        current_due_date = datetime(current_year, current_month, due_date).date()
                    except ValueError:
                        last_day = calendar.monthrange(current_year, current_month)[1]
                        current_due_date = datetime(current_year, current_month, min(due_date, last_day)).date()
                else:
                    # 跨月还款：还款日在账单日的下个月
                    next_month = current_month + 1
                    next_year = current_year
                    if next_month > 12:
                        next_month = 1
                        next_year += 1
                    
                    try:
                        current_due_date = datetime(next_year, next_month, due_date).date()
                    except ValueError:
                        last_day = calendar.monthrange(next_year, next_month)[1]
                        current_due_date = datetime(next_year, next_month, min(due_date, last_day)).date()
                
                # 根据今天与账单日的关系计算免息天数
                if today <= current_billing_date:
                    # 情况1：今天在账单日之前或当天
                    # 今天消费，在当前账单周期的还款日还款
                    interest_free_days = (current_due_date - today).days
                else:
                    # 情况2：今天在账单日之后
                    # 今天消费，计入下个账单周期，在下个周期的还款日还款
                    
                    # 计算下个月的账单日
                    next_month = current_month + 1
                    next_year = current_year
                    if next_month > 12:
                        next_month = 1
                        next_year += 1
                    
                    try:
                        next_billing_date = datetime(next_year, next_month, billing_date).date()
                    except ValueError:
                        last_day = calendar.monthrange(next_year, next_month)[1]
                        next_billing_date = datetime(next_year, next_month, min(billing_date, last_day)).date()
                    
                    # 计算下个周期的还款日
                    if due_date >= billing_date:
                        # 同月还款
                        try:
                            next_due_date = datetime(next_year, next_month, due_date).date()
                        except ValueError:
                            last_day = calendar.monthrange(next_year, next_month)[1]
                            next_due_date = datetime(next_year, next_month, min(due_date, last_day)).date()
                    else:
                        # 跨月还款
                        due_month = next_month + 1
                        due_year = next_year
                        if due_month > 12:
                            due_month = 1
                            due_year += 1
                        
                        try:
                            next_due_date = datetime(due_year, due_month, due_date).date()
                        except ValueError:
                            last_day = calendar.monthrange(due_year, due_month)[1]
                            next_due_date = datetime(due_year, due_month, min(due_date, last_day)).date()
                    
                    interest_free_days = (next_due_date - today).days
                
                # 确保免息天数不为负数
                interest_free_days = max(0, interest_free_days)
                max_days = max(max_days, interest_free_days)

            return max_days

        except Exception as e:
            logger.error(f"计算最长免息天数失败: {str(e)}")
            return 0 