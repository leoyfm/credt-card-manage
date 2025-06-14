"""
管理员服务 - 用户管理功能
"""
from typing import List, Dict, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from sqlalchemy.exc import SQLAlchemyError

from app.models.database.user import User, LoginLog
from app.models.schemas.admin import (
    UserSummaryResponse, UserStatusUpdateRequest, UserPermissionsUpdateRequest,
    UserDeletionRequest, LoginLogResponse, UserStatisticsResponse
)
from app.core.exceptions.custom import (
    ResourceNotFoundError, BusinessRuleError, ValidationError
)
from app.core.logging.logger import app_logger as logger
from app.models.schemas.common import PaginationInfo


class AdminUserService:
    """管理员用户管理服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_users_list(
        self, 
        page: int = 1, 
        page_size: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_admin: Optional[bool] = None,
        is_verified: Optional[bool] = None
    ) -> Tuple[List[UserSummaryResponse], PaginationInfo]:
        """
        获取用户列表（管理员权限）
        
        Args:
            page: 页码
            page_size: 每页大小
            search: 搜索关键词（用户名或邮箱）
            is_active: 过滤活跃状态
            is_admin: 过滤管理员
            is_verified: 过滤验证状态
            
        Returns:
            Tuple[List[UserSummaryResponse], PaginationInfo]: 用户列表和分页信息
        """
        try:
            query = self.db.query(User)
            
            # 搜索过滤
            if search:
                query = query.filter(
                    or_(
                        User.username.ilike(f"%{search}%"),
                        User.email.ilike(f"%{search}%"),
                        User.nickname.ilike(f"%{search}%")
                    )
                )
            
            # 状态过滤
            if is_active is not None:
                query = query.filter(User.is_active == is_active)
            if is_admin is not None:
                query = query.filter(User.is_admin == is_admin)
            if is_verified is not None:
                query = query.filter(User.is_verified == is_verified)
            
            # 总数统计
            total = query.count()
            
            # 分页和排序
            users = query.order_by(desc(User.created_at)).offset((page - 1) * page_size).limit(page_size).all()
            
            # 获取统计信息（批量查询避免N+1问题）
            user_ids = [user.id for user in users]
            
            # 暂时设置为0，因为相关表可能还未创建
            cards_counts = {}
            transactions_counts = {}
            
            # 查询登录日志数量
            login_logs_counts = {}
            if user_ids:
                login_logs_result = (
                    self.db.query(LoginLog.user_id, func.count(LoginLog.id))
                    .filter(LoginLog.user_id.in_(user_ids))
                    .group_by(LoginLog.user_id)
                    .all()
                )
                login_logs_counts = dict(login_logs_result)
            
            # 构建响应数据
            user_summaries = []
            for user in users:
                user_summary = UserSummaryResponse(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    nickname=user.nickname,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    is_admin=user.is_admin,
                    timezone=user.timezone,
                    language=user.language,
                    currency=user.currency,
                    last_login_at=user.last_login_at,
                    email_verified_at=user.email_verified_at,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    cards_count=cards_counts.get(user.id, 0),
                    transactions_count=transactions_counts.get(user.id, 0),
                    login_logs_count=login_logs_counts.get(user.id, 0)
                )
                user_summaries.append(user_summary)
            
            # 计算分页信息
            total_pages = (total + page_size - 1) // page_size if total > 0 else 0
            has_next = page < total_pages
            has_prev = page > 1
            
            pagination_info = PaginationInfo(
                current_page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
                has_next=has_next,
                has_prev=has_prev
            )
            
            logger.info(f"管理员查询用户列表成功: total={total}, page={page}, size={page_size}")
            return user_summaries, pagination_info
            
        except SQLAlchemyError as e:
            logger.error(f"查询用户列表失败: {str(e)}")
            raise BusinessRuleError("查询用户列表失败")
    
    def get_user_details(self, user_id: UUID) -> UserSummaryResponse:
        """
        获取用户详情（管理员权限）
        
        Args:
            user_id: 用户ID
            
        Returns:
            UserSummaryResponse: 用户详情
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ResourceNotFoundError("用户不存在")
            
            # 获取统计信息
            # 暂时设置为0，因为相关表可能还未创建
            cards_count = 0
            transactions_count = 0
            login_logs_count = self.db.query(LoginLog).filter(LoginLog.user_id == user_id).count()
            
            user_summary = UserSummaryResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                nickname=user.nickname,
                is_active=user.is_active,
                is_verified=user.is_verified,
                is_admin=user.is_admin,
                timezone=user.timezone,
                language=user.language,
                currency=user.currency,
                last_login_at=user.last_login_at,
                email_verified_at=user.email_verified_at,
                created_at=user.created_at,
                updated_at=user.updated_at,
                cards_count=cards_count,
                transactions_count=transactions_count,
                login_logs_count=login_logs_count
            )
            
            logger.info(f"管理员查询用户详情成功: user_id={user_id}")
            return user_summary
            
        except SQLAlchemyError as e:
            logger.error(f"查询用户详情失败: user_id={user_id}, error={str(e)}")
            raise BusinessRuleError("查询用户详情失败")
    
    def update_user_status(
        self, 
        user_id: UUID, 
        status_update: UserStatusUpdateRequest,
        admin_user_id: UUID
    ) -> UserSummaryResponse:
        """
        更新用户状态（管理员权限）
        
        Args:
            user_id: 用户ID
            status_update: 状态更新请求
            admin_user_id: 管理员用户ID
            
        Returns:
            UserSummaryResponse: 更新后的用户信息
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ResourceNotFoundError("用户不存在")
            
            # 防止管理员禁用自己
            if user_id == admin_user_id and not status_update.is_active:
                raise BusinessRuleError("不能禁用自己的账户")
            
            # 记录原状态
            old_status = user.is_active
            
            # 更新状态
            user.is_active = status_update.is_active
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # 记录审计日志
            logger.info(f"管理员更新用户状态: admin_id={admin_user_id}, user_id={user_id}, "
                       f"old_status={old_status}, new_status={status_update.is_active}, "
                       f"reason={status_update.reason}")
            
            return self.get_user_details(user_id)
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"更新用户状态失败: user_id={user_id}, error={str(e)}")
            raise BusinessRuleError("更新用户状态失败")
    
    def update_user_permissions(
        self, 
        user_id: UUID, 
        permissions_update: UserPermissionsUpdateRequest,
        admin_user_id: UUID
    ) -> UserSummaryResponse:
        """
        更新用户权限（管理员权限）
        
        Args:
            user_id: 用户ID
            permissions_update: 权限更新请求
            admin_user_id: 管理员用户ID
            
        Returns:
            UserSummaryResponse: 更新后的用户信息
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ResourceNotFoundError("用户不存在")
            
            # 防止管理员撤销自己的管理员权限
            if user_id == admin_user_id and not permissions_update.is_admin:
                raise BusinessRuleError("不能撤销自己的管理员权限")
            
            # 记录原权限
            old_admin = user.is_admin
            old_verified = user.is_verified
            
            # 更新权限
            user.is_admin = permissions_update.is_admin
            user.is_verified = permissions_update.is_verified
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            
            # 记录审计日志
            logger.info(f"管理员更新用户权限: admin_id={admin_user_id}, user_id={user_id}, "
                       f"admin: {old_admin}->{permissions_update.is_admin}, "
                       f"verified: {old_verified}->{permissions_update.is_verified}, "
                       f"reason={permissions_update.reason}")
            
            return self.get_user_details(user_id)
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"更新用户权限失败: user_id={user_id}, error={str(e)}")
            raise BusinessRuleError("更新用户权限失败")
    
    def get_user_login_logs(
        self, 
        user_id: UUID, 
        page: int = 1, 
        page_size: int = 20
    ) -> Tuple[List[LoginLogResponse], PaginationInfo]:
        """
        获取用户登录日志（管理员权限）
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页大小
            
        Returns:
            Tuple[List[LoginLogResponse], PaginationInfo]: 登录日志列表和分页信息
        """
        try:
            # 验证用户存在
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ResourceNotFoundError("用户不存在")
            
            query = self.db.query(LoginLog).filter(LoginLog.user_id == user_id)
            total = query.count()
            
            # 分页查询，按时间倒序
            logs = query.order_by(desc(LoginLog.created_at)).offset((page - 1) * page_size).limit(page_size).all()
            
            # 转换为响应模型
            log_responses = [
                LoginLogResponse(
                    id=log.id,
                    user_id=log.user_id,
                    login_type=log.login_type,
                    login_method=log.login_method,
                    ip_address=str(log.ip_address) if log.ip_address else None,
                    user_agent=log.user_agent,
                    location=log.location,
                    is_success=log.is_success,
                    failure_reason=log.failure_reason,
                    created_at=log.created_at
                )
                for log in logs
            ]
            
            # 计算分页信息
            total_pages = (total + page_size - 1) // page_size if total > 0 else 0
            has_next = page < total_pages
            has_prev = page > 1
            
            pagination_info = PaginationInfo(
                current_page=page,
                page_size=page_size,
                total=total,
                total_pages=total_pages,
                has_next=has_next,
                has_prev=has_prev
            )
            
            logger.info(f"管理员查询用户登录日志成功: user_id={user_id}, total={total}")
            return log_responses, pagination_info
            
        except SQLAlchemyError as e:
            logger.error(f"查询用户登录日志失败: user_id={user_id}, error={str(e)}")
            raise BusinessRuleError("查询用户登录日志失败")
    
    def delete_user(
        self, 
        user_id: UUID, 
        deletion_request: UserDeletionRequest,
        admin_user_id: UUID
    ) -> bool:
        """
        删除用户（管理员权限）
        
        Args:
            user_id: 用户ID
            deletion_request: 删除请求
            admin_user_id: 管理员用户ID
            
        Returns:
            bool: 删除成功返回True
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ResourceNotFoundError("用户不存在")
            
            # 验证用户名
            if user.username != deletion_request.confirm_username:
                raise BusinessRuleError("确认用户名不匹配")
            
            # 防止管理员删除自己
            if user_id == admin_user_id:
                raise BusinessRuleError("不能删除自己的账户")
            
            # 防止删除其他管理员（除非是超级管理员）
            if user.is_admin:
                # 这里可以加入超级管理员的逻辑
                raise BusinessRuleError("不能删除管理员账户")
            
            # 记录删除前的信息
            deleted_username = user.username
            deleted_email = user.email
            
            # 执行软删除或硬删除
            # 这里实现硬删除，如果需要软删除可以添加 deleted_at 字段
            self.db.delete(user)
            self.db.commit()
            
            # 记录审计日志
            logger.warning(f"管理员删除用户: admin_id={admin_user_id}, deleted_user_id={user_id}, "
                          f"username={deleted_username}, email={deleted_email}, "
                          f"reason={deletion_request.reason}")
            
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"删除用户失败: user_id={user_id}, error={str(e)}")
            raise BusinessRuleError("删除用户失败")
    
    def get_user_statistics(self) -> UserStatisticsResponse:
        """
        获取用户统计信息（管理员权限）
        
        Returns:
            UserStatisticsResponse: 用户统计数据
        """
        try:
            # 基础统计
            total_users = self.db.query(User).count()
            active_users = self.db.query(User).filter(User.is_active == True).count()
            verified_users = self.db.query(User).filter(User.is_verified == True).count()
            admin_users = self.db.query(User).filter(User.is_admin == True).count()
            
            # 时间范围统计
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = today_start - timedelta(days=now.weekday())
            month_start = today_start.replace(day=1)
            
            new_users_today = self.db.query(User).filter(User.created_at >= today_start).count()
            new_users_this_week = self.db.query(User).filter(User.created_at >= week_start).count()
            new_users_this_month = self.db.query(User).filter(User.created_at >= month_start).count()
            
            # 用户分布统计
            timezone_distribution = dict(
                self.db.query(User.timezone, func.count(User.id))
                .group_by(User.timezone)
                .all()
            )
            
            language_distribution = dict(
                self.db.query(User.language, func.count(User.id))
                .group_by(User.language)
                .all()
            )
            
            # 登录统计
            today_login_logs = self.db.query(LoginLog).filter(LoginLog.created_at >= today_start)
            total_logins_today = today_login_logs.count()
            successful_logins_today = today_login_logs.filter(LoginLog.is_success == True).count()
            failed_logins_today = total_logins_today - successful_logins_today
            
            statistics = UserStatisticsResponse(
                total_users=total_users,
                active_users=active_users,
                verified_users=verified_users,
                admin_users=admin_users,
                new_users_today=new_users_today,
                new_users_this_week=new_users_this_week,
                new_users_this_month=new_users_this_month,
                user_distribution={
                    "by_timezone": timezone_distribution,
                    "by_language": language_distribution
                },
                login_statistics={
                    "total_logins_today": total_logins_today,
                    "successful_logins_today": successful_logins_today,
                    "failed_logins_today": failed_logins_today
                }
            )
            
            logger.info("管理员查询用户统计信息成功")
            return statistics
            
        except SQLAlchemyError as e:
            logger.error(f"查询用户统计失败: {str(e)}")
            raise BusinessRuleError("查询用户统计失败") 