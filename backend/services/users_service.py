"""
用户管理服务层

包含用户管理相关的业务逻辑，如用户列表、状态管理、统计等。
"""

import logging
from datetime import datetime, UTC, timedelta
from typing import Optional, List, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, func, desc
from sqlalchemy.orm import Session

from models.users import (
    UserProfile,
    UserStatsInfo,
    LoginLogInfo,
    WechatBindingInfo
)
from utils.response import ResponseUtil

logger = logging.getLogger(__name__)


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

        # 导入模型
        User = self._get_user_model()
        
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

        User = self._get_user_model()
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

        User = self._get_user_model()
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

        User = self._get_user_model()
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

        User = self._get_user_model()
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.warning(f"用户不存在 - user_id: {user_id}")
            return False
        
        try:
            # 删除相关数据（级联删除应该由数据库处理）
            # 但为了确保数据一致性，我们先删除相关表的数据
            
            # 删除验证码记录
            VerificationCode = self._get_verification_code_model()
            self.db.query(VerificationCode).filter(VerificationCode.user_id == user_id).delete()
            
            # 删除微信绑定记录
            WechatBinding = self._get_wechat_binding_model()
            self.db.query(WechatBinding).filter(WechatBinding.user_id == user_id).delete()
            
            # 删除登录日志
            LoginLog = self._get_login_log_model()
            self.db.query(LoginLog).filter(LoginLog.user_id == user_id).delete()
            
            # 删除用户会话
            UserSession = self._get_user_session_model()
            self.db.query(UserSession).filter(UserSession.user_id == user_id).delete()
            
            # 最后删除用户本身
            self.db.delete(user)
            self.db.commit()
            
            logger.warning(f"用户删除成功 - user_id: {user_id}, username: {user.username}")
            return True
            
        except Exception as e:
            logger.error(f"删除用户失败 - user_id: {user_id}, error: {str(e)}")
            self.db.rollback()
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

        LoginLog = self._get_login_log_model()
        
        # 基础查询
        query = self.db.query(LoginLog).filter(LoginLog.user_id == user_id)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        skip = ResponseUtil.calculate_skip(page, page_size)
        logs = query.order_by(desc(LoginLog.created_at)).offset(skip).limit(page_size).all()
        
        # 转换为Pydantic模型
        log_infos = [LoginLogInfo.model_validate(log) for log in logs]
        
        logger.info(f"获取用户登录日志成功 - user_id: {user_id}, 返回 {len(log_infos)} 条记录")
        return log_infos, total

    def get_user_wechat_binding(self, user_id: UUID) -> Optional[WechatBindingInfo]:
        """
        获取用户微信绑定信息
        
        参数:
        - user_id: 用户ID
        
        返回:
        - 微信绑定信息，未绑定返回None
        """
        logger.info(f"获取用户微信绑定信息 - user_id: {user_id}")

        WechatBinding = self._get_wechat_binding_model()
        binding = self.db.query(WechatBinding).filter(
            and_(
                WechatBinding.user_id == user_id,
                WechatBinding.is_active == True
            )
        ).first()
        
        if binding:
            logger.info(f"获取微信绑定信息成功 - user_id: {user_id}")
            return WechatBindingInfo.model_validate(binding)
        
        logger.info(f"用户未绑定微信 - user_id: {user_id}")
        return None

    def get_users_statistics(self) -> UserStatsInfo:
        """
        获取用户统计信息
        
        返回:
        - 用户统计数据
        """
        logger.info("获取用户统计信息")

        User = self._get_user_model()
        LoginLog = self._get_login_log_model()
        
        # 总用户数
        total_users = self.db.query(User).count()
        
        # 活跃用户数（最近30天有登录）
        thirty_days_ago = datetime.now(UTC) - timedelta(days=30)
        active_users = self.db.query(User).filter(
            and_(
                User.is_active == True,
                User.last_login_at >= thirty_days_ago
            )
        ).count()
        
        # 已验证用户数
        verified_users = self.db.query(User).filter(User.is_verified == True).count()
        
        # 今日新增用户数
        today = datetime.now(UTC).date()
        today_start = datetime.combine(today, datetime.min.time(), UTC)
        new_users_today = self.db.query(User).filter(
            User.created_at >= today_start
        ).count()
        
        # 今日登录次数
        login_count_today = self.db.query(LoginLog).filter(
            and_(
                LoginLog.created_at >= today_start,
                LoginLog.is_success == True
            )
        ).count()
        
        stats = UserStatsInfo(
            total_users=total_users,
            active_users=active_users,
            verified_users=verified_users,
            new_users_today=new_users_today,
            login_count_today=login_count_today
        )
        
        logger.info(f"用户统计信息获取成功 - 总用户: {total_users}, 活跃用户: {active_users}")
        return stats

    # ==================== 私有辅助方法 ====================

    def _get_user_model(self):
        """获取User模型类"""
        from db_models.users import User
        return User

    def _get_verification_code_model(self):
        """获取VerificationCode模型类"""
        from db_models.users import VerificationCode
        return VerificationCode

    def _get_wechat_binding_model(self):
        """获取WechatBinding模型类"""
        from db_models.users import WechatBinding
        return WechatBinding

    def _get_login_log_model(self):
        """获取LoginLog模型类"""
        from db_models.users import LoginLog
        return LoginLog

    def _get_user_session_model(self):
        """获取UserSession模型类"""
        from db_models.users import UserSession
        return UserSession 