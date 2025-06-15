"""
用户提醒功能 TestClient 测试

测试用户提醒设置和提醒记录的完整功能，包括：
- 提醒设置的CRUD操作
- 提醒记录的管理
- 提醒统计和查询
- 权限验证
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, time, timedelta
from uuid import uuid4
import json


class TestUserReminders:
    """用户提醒功能测试类"""

    def test_create_reminder_setting_success(self, authenticated_client):
        """测试创建提醒设置成功"""
        test_client, test_user = authenticated_client
        
        # 准备测试数据
        setting_data = {
            "card_id": None,  # 全局提醒
            "reminder_type": "payment",
            "advance_days": 3,
            "reminder_time": "09:00:00",
            "email_enabled": True,
            "sms_enabled": False,
            "push_enabled": True,
            "wechat_enabled": False,
            "is_recurring": True,
            "frequency": "monthly",
            "is_enabled": True
        }

        # 发送请求
        response = test_client.post(
            "/api/v1/user/reminders/settings",
            json=setting_data
        )

        # 验证响应
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "提醒设置创建成功"
        
        # 验证返回的设置数据
        setting = data["data"]
        assert setting["reminder_type"] == "payment"
        assert setting["advance_days"] == 3
        assert setting["email_enabled"] is True
        assert setting["is_enabled"] is True
        assert "id" in setting
        assert "created_at" in setting

    def test_get_reminder_settings_list(self, authenticated_client):
        """测试获取提醒设置列表"""
        test_client, test_user = authenticated_client
        
        # 先创建一个提醒设置
        setting_data = {
            "card_id": None,
            "reminder_type": "payment",
            "advance_days": 3,
            "email_enabled": True,
            "push_enabled": True,
            "is_enabled": True
        }

        create_response = test_client.post(
            "/api/v1/user/reminders/settings",
            json=setting_data
        )
        assert create_response.status_code == 200

        # 获取设置列表
        response = test_client.get(
            "/api/v1/user/reminders/settings?page=1&page_size=10"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "pagination" in data
        assert len(data["data"]) >= 1

        # 验证分页信息
        pagination = data["pagination"]
        assert pagination["current_page"] == 1
        assert pagination["page_size"] == 10

    def test_update_reminder_setting(self, authenticated_client):
        """测试更新提醒设置"""
        test_client, test_user = authenticated_client
        
        # 先创建一个提醒设置
        setting_data = {
            "card_id": None,
            "reminder_type": "payment",
            "advance_days": 3,
            "email_enabled": True,
            "is_enabled": True
        }

        create_response = test_client.post(
            "/api/v1/user/reminders/settings",
            json=setting_data
        )
        assert create_response.status_code == 200
        setting_id = create_response.json()["data"]["id"]

        # 更新设置
        update_data = {
            "advance_days": 7,
            "reminder_time": "18:00:00",
            "sms_enabled": True,
            "is_enabled": False
        }

        response = test_client.put(
            f"/api/v1/user/reminders/settings/{setting_id}",
            json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "提醒设置更新成功"
        
        # 验证更新结果
        setting = data["data"]
        assert setting["advance_days"] == 7
        assert setting["reminder_time"] == "18:00:00"
        assert setting["sms_enabled"] is True
        assert setting["is_enabled"] is False

    def test_delete_reminder_setting(self, authenticated_client):
        """测试删除提醒设置"""
        test_client, test_user = authenticated_client
        
        # 先创建一个提醒设置
        setting_data = {
            "card_id": None,
            "reminder_type": "payment",
            "advance_days": 3,
            "is_enabled": True
        }

        create_response = test_client.post(
            "/api/v1/user/reminders/settings",
            json=setting_data
        )
        assert create_response.status_code == 200
        setting_id = create_response.json()["data"]["id"]

        # 删除设置
        response = test_client.delete(
            f"/api/v1/user/reminders/settings/{setting_id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "提醒设置删除成功"
        assert data["data"] is True

    def test_get_reminder_statistics(self, authenticated_client):
        """测试获取提醒统计"""
        test_client, test_user = authenticated_client
        
        response = test_client.get("/api/v1/user/reminders/statistics")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        stats = data["data"]
        assert "total_settings" in stats
        assert "active_settings" in stats
        assert "total_reminders_30days" in stats
        assert "pending_reminders_30days" in stats
        assert "read_rate" in stats
        assert "type_distribution" in stats
        # 根据实际API响应调整字段名
        assert "read_reminders_30days" in stats  # 实际字段名

        # 验证数据类型
        assert isinstance(stats["total_settings"], int)
        assert isinstance(stats["active_settings"], int)
        assert isinstance(stats["read_rate"], (int, float))
        assert isinstance(stats["type_distribution"], dict)
        assert isinstance(stats["read_reminders_30days"], int)

    def test_get_upcoming_reminders(self, authenticated_client):
        """测试获取即将到来的提醒"""
        test_client, test_user = authenticated_client
        
        response = test_client.get("/api/v1/user/reminders/upcoming?days_ahead=7")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        upcoming = data["data"]
        assert "total_upcoming" in upcoming
        assert "high_priority_count" in upcoming
        assert "medium_priority_count" in upcoming
        assert "low_priority_count" in upcoming
        assert "analysis_period" in upcoming
        assert "reminders" in upcoming

        # 验证数据类型
        assert isinstance(upcoming["total_upcoming"], int)
        assert isinstance(upcoming["reminders"], list)

    def test_get_unread_reminders_count(self, authenticated_client):
        """测试获取未读提醒个数"""
        test_client, test_user = authenticated_client
        
        response = test_client.get("/api/v1/user/reminders/unread-count")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        count_data = data["data"]
        assert "total_unread" in count_data
        assert "type_breakdown" in count_data
        assert "last_check_time" in count_data

        # 验证数据类型
        assert isinstance(count_data["total_unread"], int)
        assert isinstance(count_data["type_breakdown"], dict)

    def test_mark_all_reminders_as_read(self, authenticated_client):
        """测试标记所有提醒为已读"""
        test_client, test_user = authenticated_client
        
        response = test_client.post("/api/v1/user/reminders/mark-all-read")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        result = data["data"]
        assert "marked_count" in result
        assert "marked_at" in result
        assert "message" in result

        # 验证数据类型
        assert isinstance(result["marked_count"], int)
        assert isinstance(result["message"], str)

    def test_get_recent_reminders(self, authenticated_client):
        """测试获取最近的提醒"""
        test_client, test_user = authenticated_client
        
        response = test_client.get("/api/v1/user/reminders/recent?limit=5")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)

        # 验证返回数量不超过限制
        assert len(data["data"]) <= 5

    def test_generate_automatic_reminders(self, authenticated_client):
        """测试生成自动提醒"""
        test_client, test_user = authenticated_client
        
        response = test_client.post("/api/v1/user/reminders/generate-automatic")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], dict)

    def test_reminder_permission_control(self, test_client: TestClient):
        """测试提醒功能的权限控制"""
        # 创建一个没有认证的客户端
        unauthenticated_client = TestClient(test_client.app)
        
        # 测试未认证用户无法访问
        response = unauthenticated_client.get("/api/v1/user/reminders/settings")
        assert response.status_code == 401

        response = unauthenticated_client.post(
            "/api/v1/user/reminders/settings",
            json={"reminder_type": "payment", "advance_days": 3}
        )
        assert response.status_code == 401

        response = unauthenticated_client.get("/api/v1/user/reminders/statistics")
        assert response.status_code == 401

    def test_reminder_setting_not_found(self, authenticated_client):
        """测试访问不存在的提醒设置"""
        test_client, test_user = authenticated_client
        fake_id = str(uuid4())
        
        # 获取不存在的设置
        response = test_client.get(f"/api/v1/user/reminders/settings/{fake_id}")
        assert response.status_code == 400  # 资源不存在应该返回400
        data = response.json()
        assert data["success"] is False

        # 更新不存在的设置
        response = test_client.put(
            f"/api/v1/user/reminders/settings/{fake_id}",
            json={"advance_days": 5}
        )
        assert response.status_code == 400  # 资源不存在应该返回400
        data = response.json()
        assert data["success"] is False

        # 删除不存在的设置
        response = test_client.delete(f"/api/v1/user/reminders/settings/{fake_id}")
        assert response.status_code == 400  # 资源不存在应该返回400
        data = response.json()
        assert data["success"] is False 