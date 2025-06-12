"""
用户服务层 - 业务逻辑处理
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime, timedelta, timezone
from uuid import UUID
import bcrypt

from app.models.database.user import User, LoginLog, WechatBinding
from app.models.schemas.user import (
    UserProfileResponse, UserProfileUpdateRequest, ChangePasswordRequest,
    LoginLogResponse, AccountDeletionRequest, WechatBindingResponse,
    UserStatisticsResponse, UserSearchRequest, UserStatusUpdateRequest
)
from app.core.exceptions.custom import (
    ValidationError, ResourceNotFoundError, AuthenticationError,
    BusinessRuleError
)
from app.core.logging.logger import app_logger as logger


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========== 用户资料管理 ==========
    
    def get_user_profile(self, user_id: UUID) -> UserProfileResponse:
        """
        获取用户资料
        
        Args:
            user_id: 用户ID
            
        Returns:
            UserProfileResponse: 用户资料信息
            
        Raises:
            ResourceNotFoundError: 用户不存在
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"用户不存在: {user_id}")
                raise ResourceNotFoundError("用户不存在")
            
            logger.info(f"获取用户资料成功: {user_id}")
            return UserProfileResponse.model_validate(user)
            
        except Exception as e:
            logger.error(f"获取用户资料失败: {user_id}, 错误: {str(e)}")
            raise
    
    def update_user_profile(
        self, 
        user_id: UUID, 
        update_data: UserProfileUpdateRequest
    ) -> UserProfileResponse:
        """
        更新用户资料
        
        Args:
            user_id: 用户ID
            update_data: 更新数据
            
        Returns:
            UserProfileResponse: 更新后的用户资料
            
        Raises:
            ResourceNotFoundError: 用户不存在
            ValidationError: 数据验证失败
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"用户不存在: {user_id}")
                raise ResourceNotFoundError("用户不存在")
            
            # 更新字段
            update_dict = update_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            user.updated_at = datetime.now(timezone(timedelta(hours=8)))
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"更新用户资料成功: {user_id}, 字段: {list(update_dict.keys())}")
            return UserProfileResponse.model_validate(user)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户资料失败: {user_id}, 错误: {str(e)}")
            raise
    
    def change_password(
        self, 
        user_id: UUID, 
        password_data: ChangePasswordRequest
    ) -> bool:
        """
        修改用户密码
        
        Args:
            user_id: 用户ID
            password_data: 密码修改数据
            
        Returns:
            bool: 修改是否成功
            
        Raises:
            ResourceNotFoundError: 用户不存在
            AuthenticationError: 当前密码错误
            ValidationError: 新密码确认不匹配
        """
        try:
            # 验证确认密码
            if password_data.new_password != password_data.confirm_password:
                raise ValidationError("新密码与确认密码不匹配")
            
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"用户不存在: {user_id}")
                raise ResourceNotFoundError("用户不存在")
            
            # 验证当前密码
            if not bcrypt.checkpw(
                password_data.current_password.encode('utf-8'),
                user.password_hash.encode('utf-8')
            ):
                logger.warning(f"密码修改失败，当前密码错误: {user_id}")
                raise AuthenticationError("当前密码错误")
            
            # 加密新密码
            salt = bcrypt.gensalt()
            new_password_hash = bcrypt.hashpw(
                password_data.new_password.encode('utf-8'), 
                salt
            ).decode('utf-8')
            
            user.password_hash = new_password_hash
            user.updated_at = datetime.now(timezone(timedelta(hours=8)))
            self.db.commit()
            
            logger.info(f"用户密码修改成功: {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"修改密码失败: {user_id}, 错误: {str(e)}")
            raise
    
    # ========== 登录日志管理 ==========
    
    def get_user_login_logs(
        self, 
        user_id: UUID, 
        page: int = 1, 
        page_size: int = 20
    ) -> Tuple[List[LoginLogResponse], int]:
        """
        获取用户登录日志（分页）
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页大小
            
        Returns:
            Tuple[List[LoginLogResponse], int]: 登录日志列表和总数
        """
        try:
            # 计算偏移量
            skip = (page - 1) * page_size
            
            # 查询登录日志
            query = self.db.query(LoginLog).filter(LoginLog.user_id == user_id)
            total = query.count()
            
            logs = query.order_by(desc(LoginLog.created_at))\
                        .offset(skip)\
                        .limit(page_size)\
                        .all()
            
            log_responses = [LoginLogResponse.model_validate(log) for log in logs]
            
            logger.info(f"获取用户登录日志成功: {user_id}, 页码: {page}, 总数: {total}")
            return log_responses, total
            
        except Exception as e:
            logger.error(f"获取用户登录日志失败: {user_id}, 错误: {str(e)}")
            raise
    
    def create_login_log(
        self,
        user_id: UUID,
        login_type: str,
        login_method: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        location: Optional[str] = None,
        is_success: bool = True,
        failure_reason: Optional[str] = None
    ) -> LoginLogResponse:
        """
        创建登录日志记录
        
        Args:
            user_id: 用户ID
            login_type: 登录类型
            login_method: 登录方式
            ip_address: IP地址
            user_agent: 用户代理
            location: 地理位置
            is_success: 是否成功
            failure_reason: 失败原因
            
        Returns:
            LoginLogResponse: 创建的登录日志
        """
        try:
            login_log = LoginLog(
                user_id=user_id,
                login_type=login_type,
                login_method=login_method,
                ip_address=ip_address,
                user_agent=user_agent,
                location=location,
                is_success=is_success,
                failure_reason=failure_reason,
                created_at=datetime.now(timezone(timedelta(hours=8)))
            )
            
            self.db.add(login_log)
            self.db.commit()
            self.db.refresh(login_log)
            
            logger.info(f"创建登录日志成功: {user_id}, 类型: {login_type}, 成功: {is_success}")
            return LoginLogResponse.model_validate(login_log)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"创建登录日志失败: {user_id}, 错误: {str(e)}")
            raise
    
    # ========== 账户操作 ==========
    
    def delete_user_account(
        self, 
        user_id: UUID, 
        deletion_data: AccountDeletionRequest
    ) -> bool:
        """
        注销用户账户（软删除）
        
        Args:
            user_id: 用户ID
            deletion_data: 注销数据
            
        Returns:
            bool: 注销是否成功
            
        Raises:
            ResourceNotFoundError: 用户不存在
            AuthenticationError: 密码错误
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"用户不存在: {user_id}")
                raise ResourceNotFoundError("用户不存在")
            
            # 验证密码
            if not bcrypt.checkpw(
                deletion_data.password.encode('utf-8'),
                user.password_hash.encode('utf-8')
            ):
                logger.warning(f"账户注销失败，密码错误: {user_id}")
                raise AuthenticationError("密码错误")
            
            # 软删除：禁用账户
            user.is_active = False
            user.updated_at = datetime.now(timezone(timedelta(hours=8)))
            
            # 记录注销日志
            self.create_login_log(
                user_id=user_id,
                login_type="account",
                login_method="deletion",
                is_success=True,
                failure_reason=deletion_data.reason
            )
            
            self.db.commit()
            
            logger.info(f"用户账户注销成功: {user_id}, 原因: {deletion_data.reason}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"用户账户注销失败: {user_id}, 错误: {str(e)}")
            raise
    
    # ========== 微信绑定管理 ==========
    
    def get_wechat_bindings(self, user_id: UUID) -> List[WechatBindingResponse]:
        """
        获取用户微信绑定列表
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[WechatBindingResponse]: 微信绑定列表
        """
        try:
            bindings = self.db.query(WechatBinding)\
                            .filter(WechatBinding.user_id == user_id)\
                            .filter(WechatBinding.is_active == True)\
                            .all()
            
            binding_responses = [WechatBindingResponse.from_orm(binding) for binding in bindings]
            
            logger.info(f"获取用户微信绑定成功: {user_id}, 数量: {len(binding_responses)}")
            return binding_responses
            
        except Exception as e:
            logger.error(f"获取用户微信绑定失败: {user_id}, 错误: {str(e)}")
            raise
    
    # ========== 用户统计 ==========
    
    def get_user_statistics(self, user_id: UUID) -> UserStatisticsResponse:
        """
        获取用户统计信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            UserStatisticsResponse: 用户统计信息
        """
        try:
            # 获取用户基础信息
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ResourceNotFoundError("用户不存在")
            
            # 这里需要根据实际的数据库表结构来实现统计逻辑
            # 暂时返回模拟数据，实际实现需要联合查询其他表
            
            # 计算账户天数
            account_age_days = (datetime.now(timezone(timedelta(hours=8))) - user.created_at).days
            
            # 实际实现时需要查询以下表：
            # - credit_cards: 信用卡统计
            # - transactions: 交易统计  
            # - annual_fee_records: 年费统计
            # - reminder_settings: 提醒统计
            
            statistics = UserStatisticsResponse(
                # 基础统计 - 需要从credit_cards表查询
                total_cards=0,
                active_cards=0,
                total_credit_limit=0.0,
                total_used_limit=0.0,
                credit_utilization=0.0,
                
                # 交易统计 - 需要从transactions表查询
                total_transactions=0,
                total_spending=0.0,
                this_month_spending=0.0,
                total_income=0.0,
                avg_transaction=0.0,
                
                # 年费统计 - 需要从annual_fee_records表查询
                total_annual_fees=0.0,
                waived_fees=0.0,
                pending_fees=0.0,
                
                # 积分统计 - 需要从transactions表汇总
                total_points_earned=0,
                total_cashback_earned=0.0,
                
                # 提醒统计 - 需要从reminder_settings表查询
                active_reminders=0,
                
                # 时间统计
                account_age_days=account_age_days,
                last_transaction_date=None
            )
            
            logger.info(f"获取用户统计信息成功: {user_id}")
            return statistics
            
        except Exception as e:
            logger.error(f"获取用户统计信息失败: {user_id}, 错误: {str(e)}")
            raise
    
    # ========== 管理员功能 ==========
    
    def search_users(
        self, 
        search_params: UserSearchRequest,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[UserProfileResponse], int]:
        """
        搜索用户（管理员功能）
        
        Args:
            search_params: 搜索参数
            page: 页码
            page_size: 每页大小
            
        Returns:
            Tuple[List[UserProfileResponse], int]: 用户列表和总数
        """
        try:
            query = self.db.query(User)
            
            # 关键词搜索
            if search_params.keyword:
                keyword = f"%{search_params.keyword}%"
                query = query.filter(
                    User.username.ilike(keyword) |
                    User.email.ilike(keyword) |
                    User.nickname.ilike(keyword)
                )
            
            # 状态筛选
            if search_params.is_active is not None:
                query = query.filter(User.is_active == search_params.is_active)
            
            if search_params.is_verified is not None:
                query = query.filter(User.is_verified == search_params.is_verified)
            
            if search_params.is_admin is not None:
                query = query.filter(User.is_admin == search_params.is_admin)
            
            # 时间筛选
            if search_params.start_date:
                query = query.filter(User.created_at >= search_params.start_date)
            
            if search_params.end_date:
                query = query.filter(User.created_at <= search_params.end_date)
            
            # 统计总数
            total = query.count()
            
            # 分页查询
            skip = (page - 1) * page_size
            users = query.order_by(desc(User.created_at))\
                        .offset(skip)\
                        .limit(page_size)\
                        .all()
            
            user_responses = [UserProfileResponse.from_orm(user) for user in users]
            
            logger.info(f"用户搜索成功, 关键词: {search_params.keyword}, 总数: {total}")
            return user_responses, total
            
        except Exception as e:
            logger.error(f"用户搜索失败, 错误: {str(e)}")
            raise
    
    def update_user_status(
        self, 
        user_id: UUID, 
        status_data: UserStatusUpdateRequest
    ) -> UserProfileResponse:
        """
        更新用户状态（管理员功能）
        
        Args:
            user_id: 用户ID
            status_data: 状态更新数据
            
        Returns:
            UserProfileResponse: 更新后的用户信息
            
        Raises:
            ResourceNotFoundError: 用户不存在
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.warning(f"用户不存在: {user_id}")
                raise ResourceNotFoundError("用户不存在")
            
            # 更新状态字段
            update_dict = status_data.model_dump(exclude_unset=True)
            for field, value in update_dict.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            
            user.updated_at = datetime.now(timezone(timedelta(hours=8)))
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"更新用户状态成功: {user_id}, 字段: {list(update_dict.keys())}")
            return UserProfileResponse.from_orm(user)
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户状态失败: {user_id}, 错误: {str(e)}")
            raise
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """
        根据ID获取用户（内部使用）
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[User]: 用户对象
        """
        try:
            return self.db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            logger.error(f"根据ID获取用户失败: {user_id}, 错误: {str(e)}")
            raise 