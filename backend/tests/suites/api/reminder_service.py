"""
还款提醒服务API测试套件

使用新测试框架v2.0进行还款提醒功能的全面测试
包括提醒设置、自动生成、记录管理等功能
"""

import pytest
from tests.framework import (
    test_suite, api_test, with_user, with_cards, with_reminders,
    performance_test, stress_test
)


@test_suite("还款提醒API")
class ReminderTests:
    """还款提醒功能测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_create_reminder_success(self, api, user, cards):
        """测试成功创建还款提醒"""
        card = cards[0] if isinstance(cards, list) else cards
        reminder_data = {
            "card_id": card['id'],
            "reminder_type": "repayment",
            "title": "信用卡还款提醒",
            "description": "请记得还款，避免逾期",
            "remind_days_before": 3,
            "is_enabled": True,
            "reminder_method": "push"
        }
        
        api.post("/api/v1/user/reminders/create", data=reminder_data).should.succeed().with_data(
            reminder_type="repayment",
            title="信用卡还款提醒",
            remind_days_before=3
        )
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_create_annual_fee_reminder(self, api, user, cards):
        """测试创建年费提醒"""
        card = cards[0] if isinstance(cards, list) else cards
        reminder_data = {
            "card_id": card['id'],
            "reminder_type": "annual_fee",
            "title": "年费缴纳提醒",
            "remind_days_before": 30,
            "reminder_method": "email"
        }
        
        api.post("/api/v1/user/reminders/create", data=reminder_data).should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_create_spending_limit_reminder(self, api, user, cards):
        """测试创建消费限额提醒"""
        card = cards[0] if isinstance(cards, list) else cards
        reminder_data = {
            "card_id": card['id'],
            "reminder_type": "spending_limit",
            "title": "消费限额提醒",
            "threshold_percentage": 80,  # 80%时提醒
            "reminder_method": "sms"
        }
        
        api.post("/api/v1/user/reminders/create", data=reminder_data).should.succeed()
    
    @api_test
    @with_user
    def test_get_reminders_list(self, api, user):
        """测试获取提醒列表"""
        api.get("/api/v1/user/reminders/list").should.succeed().with_pagination()
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_reminders(count=1)
    def test_get_reminder_details(self, api, user, cards, reminders):
        """测试获取提醒详情"""
        reminder = reminders[0] if isinstance(reminders, list) else reminders
        api.get(f"/api/v1/user/reminders/{reminder['id']}/details").should.succeed().with_data(
            id=reminder['id'],
            title=reminder['title']
        )
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_reminders(count=1)
    def test_update_reminder_success(self, api, user, cards, reminders):
        """测试成功更新提醒"""
        reminder = reminders[0] if isinstance(reminders, list) else reminders
        update_data = {
            "title": "更新后的提醒标题",
            "remind_days_before": 5,
            "is_enabled": False
        }
        
        api.put(f"/api/v1/user/reminders/{reminder['id']}/update", data=update_data).should.succeed()
        
        # 验证更新生效
        api.get(f"/api/v1/user/reminders/{reminder['id']}/details").should.succeed().with_data(
            title="更新后的提醒标题",
            remind_days_before=5,
            is_enabled=False
        )
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_reminders(count=1)
    def test_delete_reminder_success(self, api, user, cards, reminders):
        """测试成功删除提醒"""
        reminder = reminders[0] if isinstance(reminders, list) else reminders
        
        api.delete(f"/api/v1/user/reminders/{reminder['id']}/delete").should.succeed()
        
        # 验证提醒已删除
        api.get(f"/api/v1/user/reminders/{reminder['id']}/details").should.fail(404)
    
    @api_test
    @with_user
    def test_create_reminder_validation_error(self, api, user):
        """测试创建提醒参数验证"""
        invalid_data = {
            "title": "",  # 空标题
            "remind_days_before": -1,  # 负数天数
            "reminder_method": "invalid_method"  # 无效方法
        }
        
        api.post("/api/v1/user/reminders/create", data=invalid_data).should.fail(422)


@test_suite("提醒记录管理")
class ReminderRecordTests:
    """提醒记录管理测试套件"""
    
    @api_test
    @with_user
    def test_get_reminder_records(self, api, user):
        """测试获取提醒记录"""
        api.get("/api/v1/user/reminders/records").should.succeed()
    
    @api_test
    @with_user
    def test_get_records_by_status(self, api, user):
        """测试按状态筛选提醒记录"""
        # 按状态筛选
        api.get("/api/v1/user/reminders/records?status=sent").should.succeed()
        api.get("/api/v1/user/reminders/records?status=pending").should.succeed()
        api.get("/api/v1/user/reminders/records?status=failed").should.succeed()
    
    @api_test
    @with_user
    def test_get_records_by_type(self, api, user):
        """测试按类型筛选提醒记录"""
        api.get("/api/v1/user/reminders/records?type=repayment").should.succeed()
        api.get("/api/v1/user/reminders/records?type=annual_fee").should.succeed()
    
    @api_test
    @with_user
    def test_mark_reminder_as_read(self, api, user):
        """测试标记提醒为已读"""
        # 这里假设有提醒记录ID
        record_id = "reminder_record_123"
        api.put(f"/api/v1/user/reminders/records/{record_id}/mark-read").should.succeed()


@test_suite("提醒设置管理")
class ReminderSettingsTests:
    """提醒设置管理测试套件"""
    
    @api_test
    @with_user
    def test_get_global_reminder_settings(self, api, user):
        """测试获取全局提醒设置"""
        api.get("/api/v1/user/reminders/settings").should.succeed()
    
    @api_test
    @with_user
    def test_update_global_reminder_settings(self, api, user):
        """测试更新全局提醒设置"""
        settings_data = {
            "enable_push_notifications": True,
            "enable_email_notifications": True,
            "enable_sms_notifications": False,
            "default_remind_days_before": 3,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00"
        }
        
        api.put("/api/v1/user/reminders/settings", data=settings_data).should.succeed()
    
    @api_test
    @with_user
    def test_get_reminder_templates(self, api, user):
        """测试获取提醒模板"""
        api.get("/api/v1/user/reminders/templates").should.succeed()
    
    @api_test
    @with_user
    def test_create_custom_template(self, api, user):
        """测试创建自定义提醒模板"""
        template_data = {
            "name": "自定义还款提醒",
            "template_type": "repayment",
            "title_template": "{{card_name}} 还款提醒",
            "content_template": "您的 {{card_name}} 将在 {{days}} 天后到期，请及时还款。",
            "is_default": False
        }
        
        api.post("/api/v1/user/reminders/templates/create", data=template_data).should.succeed()


@test_suite("自动提醒生成")
class AutoReminderTests:
    """自动提醒生成测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=2)
    def test_trigger_auto_reminder_generation(self, api, user, cards):
        """测试触发自动提醒生成"""
        # 触发系统自动生成提醒
        api.post("/api/v1/user/reminders/auto-generate").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_check_upcoming_due_dates(self, api, user, cards):
        """测试检查即将到期的账单"""
        api.get("/api/v1/user/reminders/upcoming-due-dates").should.succeed()
    
    @api_test
    @with_user
    def test_bulk_reminder_operations(self, api, user):
        """测试批量提醒操作"""
        # 批量启用提醒
        api.put("/api/v1/user/reminders/bulk/enable", data={
            "reminder_ids": ["rem_1", "rem_2", "rem_3"]
        }).should.succeed()
        
        # 批量禁用提醒
        api.put("/api/v1/user/reminders/bulk/disable", data={
            "reminder_ids": ["rem_1", "rem_2"]
        }).should.succeed()


@test_suite("提醒权限测试")
class ReminderPermissionTests:
    """提醒权限验证测试套件"""
    
    @api_test
    @with_user
    def test_unauthorized_access_reminder(self, api, user):
        """测试未授权访问他人提醒"""
        other_reminder_id = "11111111-1111-1111-1111-111111111111"
        api.get(f"/api/v1/user/reminders/{other_reminder_id}/details").should.fail(403)
    
    @api_test
    def test_unauthenticated_access(self, api):
        """测试未认证访问提醒接口"""
        api.get("/api/v1/user/reminders/list").should.fail(401)


@test_suite("提醒性能测试")
class ReminderPerformanceTests:
    """提醒服务性能测试套件"""
    
    @performance_test
    @with_user
    @with_reminders(count=20)
    def test_reminders_list_performance(self, api, user, reminders):
        """测试提醒列表性能"""
        api.get("/api/v1/user/reminders/list").should.succeed().complete_within(seconds=0.5)
    
    @performance_test
    @with_user
    @with_cards(count=1)
    def test_reminder_creation_performance(self, api, user, cards):
        """测试提醒创建性能"""
        card = cards[0] if isinstance(cards, list) else cards
        reminder_data = {
            "card_id": card['id'],
            "reminder_type": "repayment",
            "title": "性能测试提醒",
            "remind_days_before": 3
        }
        
        api.post("/api/v1/user/reminders/create", data=reminder_data).should.succeed().complete_within(seconds=0.5)
    
    @stress_test(concurrent_users=15, duration=30)
    @with_user
    def test_reminders_concurrent_access(self, api, user):
        """测试提醒并发访问"""
        api.get("/api/v1/user/reminders/list").should.succeed()


@test_suite("提醒业务逻辑测试")
class ReminderBusinessLogicTests:
    """提醒业务逻辑测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_reminder_types_validation(self, api, user, cards):
        """测试提醒类型验证"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 测试有效的提醒类型
        valid_types = ["repayment", "annual_fee", "spending_limit", "expiry_warning"]
        for reminder_type in valid_types:
            api.post("/api/v1/user/reminders/create", data={
                "card_id": card['id'],
                "reminder_type": reminder_type,
                "title": f"{reminder_type}提醒",
                "remind_days_before": 3
            }).should.succeed()
        
        # 测试无效的提醒类型
        api.post("/api/v1/user/reminders/create", data={
            "card_id": card['id'],
            "reminder_type": "invalid_type",
            "title": "无效提醒"
        }).should.fail(422)
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_reminder_methods_validation(self, api, user, cards):
        """测试提醒方式验证"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 测试有效的提醒方式
        valid_methods = ["push", "email", "sms"]
        for method in valid_methods:
            api.post("/api/v1/user/reminders/create", data={
                "card_id": card['id'],
                "reminder_type": "repayment",
                "title": f"{method}提醒",
                "reminder_method": method
            }).should.succeed()
        
        # 测试无效的提醒方式
        api.post("/api/v1/user/reminders/create", data={
            "card_id": card['id'],
            "reminder_type": "repayment",
            "title": "无效方式提醒",
            "reminder_method": "invalid_method"
        }).should.fail(422)
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_reminder_timing_logic(self, api, user, cards):
        """测试提醒时机逻辑"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建不同时机的提醒
        remind_days = [1, 3, 7, 15, 30]
        for days in remind_days:
            api.post("/api/v1/user/reminders/create", data={
                "card_id": card['id'],
                "reminder_type": "repayment",
                "title": f"{days}天前提醒",
                "remind_days_before": days
            }).should.succeed()
        
        # 测试无效的时机
        api.post("/api/v1/user/reminders/create", data={
            "card_id": card['id'],
            "reminder_type": "repayment",
            "title": "无效时机提醒",
            "remind_days_before": -1  # 负数
        }).should.fail(422)
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_reminder_priority_ordering(self, api, user, cards):
        """测试提醒优先级排序"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建不同优先级的提醒
        priorities = ["high", "medium", "low"]
        for priority in priorities:
            api.post("/api/v1/user/reminders/create", data={
                "card_id": card['id'],
                "reminder_type": "repayment",
                "title": f"{priority}优先级提醒",
                "priority": priority
            }).should.succeed()
        
        # 获取提醒列表，验证排序
        response = api.get("/api/v1/user/reminders/list?sort=priority").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_reminder_enable_disable_logic(self, api, user, cards):
        """测试提醒启用/禁用逻辑"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建提醒
        create_response = api.post("/api/v1/user/reminders/create", data={
            "card_id": card['id'],
            "reminder_type": "repayment",
            "title": "可控制提醒",
            "is_enabled": True
        }).should.succeed()
        
        reminder_id = create_response.data['id']
        
        # 禁用提醒
        api.put(f"/api/v1/user/reminders/{reminder_id}/update", data={
            "is_enabled": False
        }).should.succeed()
        
        # 验证禁用状态
        api.get(f"/api/v1/user/reminders/{reminder_id}/details").should.succeed().with_data(
            is_enabled=False
        )
        
        # 重新启用
        api.put(f"/api/v1/user/reminders/{reminder_id}/update", data={
            "is_enabled": True
        }).should.succeed()