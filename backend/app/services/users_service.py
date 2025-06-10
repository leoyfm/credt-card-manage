"""
用户管理服务层

包含用户管理相关的业务逻辑，如用户列表、状态管理、统计等。
新架构下的用户管理服务。
"""

import logging
from datetime import datetime, UTC, timedelta
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

from app.models.schemas.user import (
    UserProfile,
    UserStatsInfo,
    LoginLogInfo,
    WechatBindingInfo
)
from app.models.database.user import User, LoginLog, WechatBinding, VerificationCode
from app.utils.response import ResponseUtil
from app.core.logging.logger import get_logger

logger = get_logger(__name__)


class UsersService:
    """用户管理服务"""

    def __init__(self, db: Session):
        self.db = db

    def get_users_list(
        self,
        page: int = 1,
        page_size: int = 20,
        keyword: str = "",
        is_active: Optional[bool] = None,
        is_verified: Optional[bool] = None,
        is_admin: Optional[bool] = None
    ) -> Tuple[List[UserProfile], int]:
        """
        获取用户列表
        
        支持分页和多条件筛选的用户列表查询。
        
        参数:
        - page: 页码，从1开始
        - page_size: 每页数量
        - keyword: 搜索关键词
        - is_active: 筛选激活状态
        - is_verified: 筛选验证状态
        - is_admin: 筛选管理员状态
        
        返回:
        - (用户列表, 总数量)
        """
        logger.info(f"获取用户列表 - page: {page}, page_size: {page_size}, keyword: {keyword}")
        
        # 基础查询
        query = self.db.query(User)
        
        # 关键词搜索
        if keyword:
            search_filter = or_(
                User.username.ilike(f"%{keyword}%"),
                User.email.ilike(f"%{keyword}%"),
                User.nickname.ilike(f"%{keyword}%"),
                User.phone.ilike(f"%{keyword}%")
            )
            query = query.filter(search_filter)
        
        # 状态筛选
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        if is_verified is not None:
            query = query.filter(User.is_verified == is_verified)
        
        if is_admin is not None:
            query = query.filter(User.is_admin == is_admin)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        skip = ResponseUtil.calculate_skip(page, page_size)
        users = query.order_by(desc(User.created_at)).offset(skip).limit(page_size).all()
        
        # 转换为Pydantic模型
        user_profiles = [UserProfile.model_validate(user) for user in users]
        
        logger.info(f"获取用户列表成功 - 返回 {len(user_profiles)} 条记录，总共 {total} 条")
        return user_profiles, total

    def get_user_by_id(self, user_id: UUID) -> Optional[UserProfile]:
        """
        根据用户ID获取用户信息
        
        参数:
        - user_id: 用户ID
        
        返回:
        - 用户资料信息，不存在返回None
        """
        logger.info(f"根据ID获取用户信息 - user_id: {user_id}")

        user = self.db.query(User).filter(User.id == user_id).first()
        
        if user:
            logger.info(f"用户信息获取成功 - username: {user.username}")
            return UserProfile.model_validate(user)
        
        logger.warning(f"用户不存在 - user_id: {user_id}")
        return None

    def update_user_status(self, user_id: UUID, is_active: bool) -> Optional[UserProfile]:
        """
        更新用户状态
        
        参数:
        - user_id: 用户ID
        - is_active: 是否激活
        
        返回:
        - 更新后的用户信息，不存在返回None
        """
        logger.info(f"更新用户状态 - user_id: {user_id}, is_active: {is_active}")

        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.warning(f"用户不存在 - user_id: {user_id}")
            return None
        
        # 更新状态
        user.is_active = is_active
        user.updated_at = datetime.now(UTC)
        
        self.db.commit()
        self.db.refresh(user)
        
        status_text = "激活" if is_active else "禁用"
        logger.info(f"用户状态更新成功 - user_id: {user_id}, {status_text}")
        return UserProfile.model_validate(user)

    def update_user_admin_status(self, user_id: UUID, is_admin: bool) -> Optional[UserProfile]:
        """
        更新用户管理员权限
        
        参数:
        - user_id: 用户ID
        - is_admin: 是否为管理员
        
        返回:
        - 更新后的用户信息，不存在返回None
        """
        logger.info(f"更新用户管理员权限 - user_id: {user_id}, is_admin: {is_admin}")

        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.warning(f"用户不存在 - user_id: {user_id}")
            return None
        
        # 更新管理员权限
        user.is_admin = is_admin
        user.updated_at = datetime.now(UTC)
        
        self.db.commit()
        self.db.refresh(user)
        
        permission_text = "设置" if is_admin else "取消"
        logger.info(f"用户管理员权限更新成功 - user_id: {user_id}, {permission_text}")
        return UserProfile.model_validate(user)

    def delete_user(self, user_id: UUID) -> bool:
        """
        删除用户
        
        彻底删除用户及其相关数据。
        
        参数:
        - user_id: 用户ID
        
        返回:
        - 是否删除成功
        """
        logger.warning(f"删除用户 - user_id: {user_id}")

        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.warning(f"用户不存在 - user_id: {user_id}")
            return False
        
        try:
            # 删除相关数据
            # 删除登录日志
            self.db.query(LoginLog).filter(LoginLog.user_id == user_id).delete()
            
            # 删除微信绑定
            self.db.query(WechatBinding).filter(WechatBinding.user_id == user_id).delete()
            
            # 删除验证码记录
            self.db.query(VerificationCode).filter(VerificationCode.user_id == user_id).delete()
            
            # 删除用户会话
            self.db.query(UserSession).filter(UserSession.user_id == user_id).delete()
            
            # 删除用户
            self.db.delete(user)
            
            self.db.commit()
            logger.info(f"用户删除成功 - user_id: {user_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"删除用户失败 - user_id: {user_id}, error: {e}")
            return False

    def get_user_login_logs(
        self, 
        user_id: UUID, 
        page: int = 1, 
        page_size: int = 20
    ) -> Tuple[List[LoginLogInfo], int]:
        """
        获取用户登录日志
        
        参数:
        - user_id: 用户ID
        - page: 页码
        - page_size: 每页数量
        
        返回:
        - (登录日志列表, 总数量)
        """
        logger.info(f"获取用户登录日志 - user_id: {user_id}, page: {page}")
        
        # 基础查询
        query = self.db.query(LoginLog).filter(LoginLog.user_id == user_id)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        skip = ResponseUtil.calculate_skip(page, page_size)
        logs = query.order_by(desc(LoginLog.created_at)).offset(skip).limit(page_size).all()
        
        # 转换为Pydantic模型
        login_logs = [LoginLogInfo.model_validate(log) for log in logs]
        
        logger.info(f"获取登录日志成功 - 返回 {len(login_logs)} 条记录")
        return login_logs, total

    def get_user_wechat_binding(self, user_id: UUID) -> Optional[WechatBindingInfo]:
        """
        获取用户微信绑定信息
        
        参数:
        - user_id: 用户ID
        
        返回:
        - 微信绑定信息，不存在返回None
        """
        logger.info(f"获取用户微信绑定信息 - user_id: {user_id}")
        
        binding = self.db.query(WechatBinding).filter(WechatBinding.user_id == user_id).first()
        
        if binding:
            logger.info(f"微信绑定信息获取成功 - openid: {binding.openid[:10]}...")
            return WechatBindingInfo.model_validate(binding)
        
        logger.info(f"用户未绑定微信 - user_id: {user_id}")
        return None

    def get_users_statistics(self) -> UserStatsInfo:
        """
        获取用户统计信息
        
        返回:
        - 用户统计信息
        """
        logger.info("获取用户统计信息")
        
        # 基础统计
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        verified_users = self.db.query(User).filter(User.is_verified == True).count()
        admin_users = self.db.query(User).filter(User.is_admin == True).count()
        
        # 今日新增用户
        today_start = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)
        today_new_users = self.db.query(User).filter(User.created_at >= today_start).count()
        
        # 本周新增用户
        week_start = today_start - timedelta(days=today_start.weekday())
        week_new_users = self.db.query(User).filter(User.created_at >= week_start).count()
        
        # 本月新增用户
        month_start = today_start.replace(day=1)
        month_new_users = self.db.query(User).filter(User.created_at >= month_start).count()
        
        # 微信绑定用户
        wechat_bound_users = self.db.query(WechatBinding).count()
        
        # 今日活跃用户（有登录记录）
        today_active_users = self.db.query(LoginLog).filter(
            and_(
                LoginLog.created_at >= today_start,
                LoginLog.is_success == True
            )
        ).distinct(LoginLog.user_id).count()
        
        # 最近登录用户统计
        last_30_days = today_start - timedelta(days=30)
        recent_login_users = self.db.query(User).filter(
            User.last_login_at >= last_30_days
        ).count()
        
        stats = UserStatsInfo(
            total_users=total_users,
            active_users=active_users,
            verified_users=verified_users,
            admin_users=admin_users,
            today_new_users=today_new_users,
            week_new_users=week_new_users,
            month_new_users=month_new_users,
            wechat_bound_users=wechat_bound_users,
            today_active_users=today_active_users,
            recent_login_users=recent_login_users
        )
        
        logger.info(f"用户统计信息获取成功 - 总用户数: {total_users}")
        return stats