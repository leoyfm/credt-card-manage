"""
交易记录模块单元测试

使用FastAPI TestClient进行交易记录功能的单元测试。
测试覆盖交易记录的CRUD操作、统计功能、安全性和边界条件。

覆盖范围：
- 基础CRUD操作（创建、读取、更新、删除）
- 列表查询和分页
- 筛选和搜索功能  
- 统计数据接口
- 认证和权限验证
- 边界条件和异常处理
"""

import pytest
import logging
import time
import threading
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List
from uuid import uuid4

from tests.base_test import FastAPITestClient, BaseAPITest

logger = logging.getLogger(__name__)


@pytest.mark.unit
class TestTransactionsUnit:
    """交易记录单元测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        self.client = FastAPITestClient()
        self.api_test = BaseAPITest(self.client)
        self.test_user = self.api_test.setup_test_user()
        self.headers = {"Authorization": f"Bearer {self.test_user['token']}"}
        
        # 创建测试信用卡
        self.test_card = self.api_test.create_test_card()
        self.card_id = self.test_card["id"]
        
        logger.info(f"✅ 单元测试环境准备就绪: 用户{self.test_user['user_id']}, 卡片{self.card_id}")
    
    # ==================== 基础CRUD测试 ====================
    
    def test_01_create_transaction_success(self):
        """测试创建交易记录 - 成功案例"""
        transaction_data = {
            "card_id": self.card_id,
            "transaction_type": "expense",
            "amount": 199.50,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "星巴克咖啡",
            "description": "早餐咖啡和面包",
            "category": "dining",
            "status": "completed",
            "points_earned": 19.95,
            "points_rate": 1.0,
            "location": "北京市朝阳区"
        }
        
        response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证返回数据
        assert data["card_id"] == self.card_id
        assert data["transaction_type"] == "expense"
        assert float(data["amount"]) == 199.50
        assert data["merchant_name"] == "星巴克咖啡"
        assert data["category"] == "dining"
        assert data["status"] == "completed"
        assert float(data["points_earned"]) == 19.95
        assert "id" in data
        assert "created_at" in data
        
        logger.info(f"✅ 创建交易记录成功: {data['id']}")
    
    def test_02_create_transaction_invalid_card(self):
        """测试创建交易记录（无效信用卡）"""
        invalid_card_id = str(uuid4())
        
        transaction_data = {
            "card_id": invalid_card_id,
            "transaction_type": "expense",
            "amount": 100.00,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "测试商户",
            "category": "dining"
        }
        
        response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        
        # 应该返回400或500错误（取决于后端实现）
        assert response.status_code in [400, 500]
        
        logger.info("✅ 无效信用卡交易创建验证成功")
    
    def test_03_create_transaction_missing_required_fields(self):
        """测试创建交易记录 - 缺少必填字段"""
        transaction_data = {
            "transaction_type": "expense",
            "amount": 100.00
            # 缺少 card_id 和 transaction_date
        }
        
        response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        assert response.status_code == 422  # 数据验证错误
        
        logger.info("✅ 必填字段验证成功")
    
    def test_04_create_transaction_invalid_amount(self):
        """测试创建交易记录 - 无效金额"""
        transaction_data = {
            "card_id": self.card_id,
            "transaction_type": "expense",
            "amount": -100.00,  # 负数金额
            "transaction_date": "2024-06-08T14:30:00",
            "category": "dining"
        }
        
        response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        assert response.status_code == 422  # 数据验证错误
        
        logger.info("✅ 金额验证成功")
    
    def test_05_get_transactions_list_empty(self):
        """测试获取交易记录列表 - 空列表"""
        response = self.client.get("/api/transactions", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证分页响应格式
        self.api_test.assert_pagination_response(data, min_items=0)
        assert data["items"] == []
        assert data["pagination"]["total"] == 0
        
        logger.info("✅ 空交易列表验证成功")
    
    def test_06_get_transactions_list_with_data(self):
        """测试获取交易记录列表 - 有数据"""
        # 先创建几条交易记录
        for i in range(3):
            transaction_data = {
                "card_id": self.card_id,
                "transaction_type": "expense",
                "amount": 100.00 + i * 50,
                "transaction_date": f"2024-06-0{8-i}T14:30:00",
                "merchant_name": f"测试商户{i+1}",
                "category": "dining"
            }
            response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        # 获取交易列表
        response = self.client.get("/api/transactions", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证分页响应格式
        self.api_test.assert_pagination_response(data, min_items=3)
        assert len(data["items"]) == 3
        assert data["pagination"]["total"] == 3
        
        # 验证按时间倒序排列
        transactions = data["items"]
        for i in range(len(transactions) - 1):
            current_date = datetime.fromisoformat(transactions[i]["transaction_date"].replace('Z', '+00:00'))
            next_date = datetime.fromisoformat(transactions[i+1]["transaction_date"].replace('Z', '+00:00'))
            assert current_date >= next_date, "交易记录应该按时间倒序排列"
        
        logger.info(f"✅ 获取交易列表成功，共{len(transactions)}条记录")
    
    def test_07_get_transaction_detail_success(self):
        """测试获取交易记录详情 - 成功案例"""
        # 先创建一条交易记录
        transaction_data = {
            "card_id": self.card_id,
            "transaction_type": "expense",
            "amount": 299.99,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "苹果专卖店",
            "description": "购买AirPods",
            "category": "shopping",
            "status": "completed",
            "location": "北京市海淀区"
        }
        
        create_response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        created_transaction = self.api_test.assert_api_success(create_response, 200)
        transaction_id = created_transaction["id"]
        
        # 获取交易详情
        response = self.client.get(f"/api/transactions/{transaction_id}", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证返回数据
        assert data["id"] == transaction_id
        assert data["card_id"] == self.card_id
        assert float(data["amount"]) == 299.99
        assert data["merchant_name"] == "苹果专卖店"
        assert data["description"] == "购买AirPods"
        assert data["category"] == "shopping"
        
        logger.info(f"✅ 获取交易详情成功: {transaction_id}")
    
    def test_08_get_transaction_detail_not_found(self):
        """测试获取交易记录详情 - 记录不存在"""
        fake_id = str(uuid4())
        response = self.client.get(f"/api/transactions/{fake_id}", headers=self.headers)
        
        # 检查返回的是成功响应但数据为空，还是错误响应
        if response.status_code == 200:
            result = response.json()
            assert not result.get("success", True) or result.get("data") is None
        else:
            assert response.status_code == 404
        
        logger.info("✅ 交易记录不存在验证成功")
    
    def test_09_update_transaction_success(self):
        """测试更新交易记录 - 成功案例"""
        # 先创建一条交易记录
        transaction_data = {
            "card_id": self.card_id,
            "transaction_type": "expense",
            "amount": 150.00,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "原商户",
            "category": "dining"
        }
        
        create_response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        created_transaction = self.api_test.assert_api_success(create_response, 200)
        transaction_id = created_transaction["id"]
        
        # 更新交易记录
        update_data = {
            "amount": 200.00,
            "merchant_name": "更新后的商户",
            "description": "更新后的描述",
            "category": "shopping"
        }
        
        response = self.client.put(f"/api/transactions/{transaction_id}", json=update_data, headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证更新结果
        assert data["id"] == transaction_id
        assert float(data["amount"]) == 200.00
        assert data["merchant_name"] == "更新后的商户"
        assert data["description"] == "更新后的描述"
        assert data["category"] == "shopping"
        
        logger.info(f"✅ 更新交易记录成功: {transaction_id}")
    
    def test_10_update_transaction_not_found(self):
        """测试更新交易记录 - 记录不存在"""
        fake_id = str(uuid4())
        update_data = {
            "amount": 200.00,
            "merchant_name": "测试商户"
        }
        
        response = self.client.put(f"/api/transactions/{fake_id}", json=update_data, headers=self.headers)
        
        # 检查返回的是错误响应
        if response.status_code == 200:
            result = response.json()
            assert not result.get("success", True) or result.get("data") is None
        else:
            assert response.status_code == 404
        
        logger.info("✅ 更新不存在记录验证成功")
    
    def test_11_delete_transaction_success(self):
        """测试删除交易记录 - 成功案例"""
        # 先创建一条交易记录
        transaction_data = {
            "card_id": self.card_id,
            "transaction_type": "expense",
            "amount": 100.00,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "测试商户",
            "category": "dining"
        }
        
        create_response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        created_transaction = self.api_test.assert_api_success(create_response, 200)
        transaction_id = created_transaction["id"]
        
        # 删除交易记录
        response = self.client.delete(f"/api/transactions/{transaction_id}", headers=self.headers)
        
        # 验证删除成功（可能返回204或200）
        assert response.status_code in [200, 204]
        
        # 再次尝试获取应该失败
        get_response = self.client.get(f"/api/transactions/{transaction_id}", headers=self.headers)
        assert get_response.status_code in [404] or (
            get_response.status_code == 200 and 
            not get_response.json().get("success", True)
        )
        
        logger.info(f"✅ 删除交易记录成功: {transaction_id}")
    
    def test_12_delete_transaction_not_found(self):
        """测试删除交易记录 - 记录不存在"""
        fake_id = str(uuid4())
        response = self.client.delete(f"/api/transactions/{fake_id}", headers=self.headers)
        
        # 可能返回404或者200但成功标志为false
        assert response.status_code in [404] or (
            response.status_code == 200 and 
            not response.json().get("success", True)
        )
        
        logger.info("✅ 删除不存在记录验证成功")
    
    # ==================== 筛选和搜索测试 ====================
    
    def test_13_filter_by_transaction_type(self):
        """测试按交易类型筛选"""
        # 创建不同类型的交易记录
        transactions = [
            {"type": "expense", "amount": 100.00, "merchant": "支出商户"},
            {"type": "payment", "amount": 200.00, "merchant": "还款"},
            {"type": "refund", "amount": 50.00, "merchant": "退款来源"}
        ]
        
        for i, trans in enumerate(transactions):
            transaction_data = {
                "card_id": self.card_id,
                "transaction_type": trans["type"],
                "amount": trans["amount"],
                "transaction_date": f"2024-06-0{8-i}T14:30:00",
                "merchant_name": trans["merchant"],
                "category": "shopping"
            }
            response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        # 按支出类型筛选
        response = self.client.get("/api/transactions?transaction_type=expense", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        self.api_test.assert_pagination_response(data, min_items=1)
        assert len(data["items"]) >= 1
        
        # 验证所有记录都是支出类型
        for item in data["items"]:
            assert item["transaction_type"] == "expense"
        
        logger.info("✅ 按交易类型筛选验证成功")
    
    def test_14_filter_by_amount_range(self):
        """测试按金额范围筛选"""
        # 创建不同金额的交易记录
        amounts = [50.00, 150.00, 250.00, 350.00]
        for i, amount in enumerate(amounts):
            transaction_data = {
                "card_id": self.card_id,
                "transaction_type": "expense",
                "amount": amount,
                "transaction_date": f"2024-06-0{8-i}T14:30:00",
                "merchant_name": f"商户{i+1}",
                "category": "shopping"
            }
            response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        # 筛选100-200范围的交易
        response = self.client.get("/api/transactions?min_amount=100&max_amount=200", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        self.api_test.assert_pagination_response(data, min_items=0)
        
        # 验证所有记录都在指定范围内
        for item in data["items"]:
            amount = float(item["amount"])
            assert 100 <= amount <= 200, f"金额{amount}不在指定范围内"
        
        logger.info("✅ 按金额范围筛选验证成功")
    
    def test_15_search_by_keyword(self):
        """测试关键词搜索"""
        # 创建包含特定关键词的交易记录
        transaction_data = {
            "card_id": self.card_id,
            "transaction_type": "expense",
            "amount": 199.99,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "星巴克咖啡店",
            "description": "早餐咖啡和三明治",
            "category": "dining"
        }
        
        response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        self.api_test.assert_api_success(response, 200)
        
        # 搜索关键词
        response = self.client.get("/api/transactions?keyword=星巴克", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        self.api_test.assert_pagination_response(data, min_items=0)
        
        # 验证搜索结果包含关键词
        if data["items"]:
            found = False
            for item in data["items"]:
                if "星巴克" in item["merchant_name"] or "星巴克" in item.get("description", ""):
                    found = True
                    break
            assert found, "搜索结果中没有找到包含关键词的记录"
        
        logger.info("✅ 关键词搜索验证成功")
    
    def test_16_filter_by_date_range(self):
        """测试按日期范围筛选"""
        # 创建不同日期的交易记录
        dates = ["2024-06-01", "2024-06-05", "2024-06-10", "2024-06-15"]
        for i, date in enumerate(dates):
            transaction_data = {
                "card_id": self.card_id,
                "transaction_type": "expense",
                "amount": 100.00 + i * 50,
                "transaction_date": f"{date}T14:30:00",
                "merchant_name": f"商户{i+1}",
                "category": "shopping"
            }
            response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        # 筛选6月5日到6月10日的交易
        response = self.client.get(
            "/api/transactions?start_date=2024-06-05T00:00:00&end_date=2024-06-10T23:59:59", 
            headers=self.headers
        )
        data = self.api_test.assert_api_success(response, 200)
        
        self.api_test.assert_pagination_response(data, min_items=0)
        
        # 验证所有记录都在指定日期范围内
        start_date = datetime.fromisoformat("2024-06-05T00:00:00")
        end_date = datetime.fromisoformat("2024-06-10T23:59:59")
        
        for item in data["items"]:
            transaction_date = datetime.fromisoformat(item["transaction_date"].replace('Z', '+00:00').replace('+00:00', ''))
            assert start_date <= transaction_date <= end_date, f"交易日期{transaction_date}不在指定范围内"
        
        logger.info("✅ 按日期范围筛选验证成功")
    
    # ==================== 分页测试 ====================
    
    def test_17_pagination_basic(self):
        """测试基础分页功能"""
        # 创建10条交易记录
        for i in range(10):
            transaction_data = {
                "card_id": self.card_id,
                "transaction_type": "expense",
                "amount": 100.00 + i,
                "transaction_date": f"2024-06-{(i % 28) + 1:02d}T14:30:00",
                "merchant_name": f"测试商户{i+1}",
                "category": "shopping"
            }
            response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        # 测试第一页（每页5条）
        response = self.client.get("/api/transactions?page=1&page_size=5", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        self.api_test.assert_pagination_response(data, min_items=5)
        assert len(data["items"]) == 5
        assert data["pagination"]["current_page"] == 1
        assert data["pagination"]["page_size"] == 5
        assert data["pagination"]["total"] >= 10
        
        # 测试第二页
        response = self.client.get("/api/transactions?page=2&page_size=5", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        self.api_test.assert_pagination_response(data, min_items=0)
        assert data["pagination"]["current_page"] == 2
        assert data["pagination"]["page_size"] == 5
        
        logger.info("✅ 基础分页功能验证成功")
    
    # ==================== 统计测试 ====================
    
    def test_18_transaction_statistics_overview(self):
        """测试交易统计概览"""
        # 创建测试数据
        test_transactions = [
            {"type": "expense", "amount": 100.00, "category": "dining"},
            {"type": "expense", "amount": 200.00, "category": "shopping"},
            {"type": "payment", "amount": 500.00, "category": "other"},
            {"type": "refund", "amount": 50.00, "category": "shopping"}
        ]
        
        for i, trans in enumerate(test_transactions):
            transaction_data = {
                "card_id": self.card_id,
                "transaction_type": trans["type"],
                "amount": trans["amount"],
                "transaction_date": f"2024-06-0{i+1}T14:30:00",
                "merchant_name": f"测试商户{i+1}",
                "category": trans["category"]
            }
            response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        # 获取统计概览
        response = self.client.get("/api/transactions/statistics/overview", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证统计数据结构
        assert "total_transactions" in data
        assert "expense_amount" in data
        assert "income_amount" in data
        assert "total_amount" in data
        assert isinstance(data["total_transactions"], int)
        assert data["total_transactions"] >= 4
        
        logger.info("✅ 交易统计概览验证成功")
    
    def test_19_category_statistics(self):
        """测试分类统计"""
        # 创建不同分类的交易记录
        categories = ["dining", "shopping", "transport", "entertainment"]
        for i, category in enumerate(categories):
            transaction_data = {
                "card_id": self.card_id,
                "transaction_type": "expense",
                "amount": 100.00 + i * 50,
                "transaction_date": f"2024-06-0{i+1}T14:30:00",
                "merchant_name": f"测试商户{i+1}",
                "category": category
            }
            response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        # 获取分类统计
        response = self.client.get("/api/transactions/statistics/categories", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证统计数据
        assert isinstance(data, list)
        if data:
            first_category = data[0]
            assert "category" in first_category
            assert "total_amount" in first_category
            assert "transaction_count" in first_category
            assert "percentage" in first_category
        
        logger.info("✅ 分类统计验证成功")
    
    def test_20_monthly_trend(self):
        """测试月度趋势统计"""
        # 创建跨月的交易记录
        test_data = [
            {"month": "05", "amount": 1000.00},
            {"month": "06", "amount": 1500.00},
            {"month": "07", "amount": 800.00}
        ]
        
        for i, data_item in enumerate(test_data):
            transaction_data = {
                "card_id": self.card_id,
                "transaction_type": "expense",
                "amount": data_item["amount"],
                "transaction_date": f"2024-{data_item['month']}-15T14:30:00",
                "merchant_name": f"测试商户{i+1}",
                "category": "shopping"
            }
            response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
            self.api_test.assert_api_success(response, 200)
        
        # 获取月度趋势
        response = self.client.get("/api/transactions/statistics/monthly-trend", headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证趋势数据
        assert isinstance(data, list)
        if data:
            first_month = data[0]
            assert "month" in first_month
            assert "total_amount" in first_month
            assert "transaction_count" in first_month
        
        logger.info("✅ 月度趋势统计验证成功")
    
    # ==================== 安全性测试 ====================
    
    def test_21_unauthorized_access(self):
        """测试未授权访问"""
        response = self.client.get("/api/transactions")
        assert response.status_code == 403
        
        logger.info("✅ 未授权访问验证成功")
    
    def test_22_invalid_token_access(self):
        """测试无效token访问"""
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = self.client.get("/api/transactions", headers=invalid_headers)
        assert response.status_code == 401
        
        logger.info("✅ 无效token访问验证成功")
    
    def test_23_data_isolation(self):
        """测试用户数据隔离"""
        # 创建另一个用户
        other_client = FastAPITestClient()
        other_api_test = BaseAPITest(other_client)
        other_user = other_api_test.setup_test_user()
        other_headers = {"Authorization": f"Bearer {other_user['token']}"}
        
        # 为第一个用户创建交易记录
        transaction_data = {
            "card_id": self.card_id,
            "transaction_type": "expense",
            "amount": 100.00,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "用户1的交易",
            "category": "dining"
        }
        
        response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        created_transaction = self.api_test.assert_api_success(response, 200)
        transaction_id = created_transaction["id"]
        
        # 第二个用户尝试访问第一个用户的交易记录
        response = other_client.get(f"/api/transactions/{transaction_id}", headers=other_headers)
        
        # 应该访问失败或者返回空数据
        if response.status_code == 200:
            result = response.json()
            assert not result.get("success", True) or result.get("data") is None
        else:
            assert response.status_code in [403, 404]
        
        # 第二个用户获取交易列表不应该看到第一个用户的数据
        response = other_client.get("/api/transactions", headers=other_headers)
        data = other_api_test.assert_api_success(response, 200)
        
        # 不应该包含第一个用户的交易记录
        for item in data.get("items", []):
            assert item["id"] != transaction_id
        
        logger.info("✅ 用户数据隔离验证成功")
    
    # ==================== 边界条件测试 ====================
    
    def test_24_large_amount_transaction(self):
        """测试大金额交易"""
        transaction_data = {
            "card_id": self.card_id,
            "transaction_type": "expense",
            "amount": 999999.99,  # 很大的金额
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "大额交易商户",
            "category": "shopping"
        }
        
        response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        assert float(data["amount"]) == 999999.99
        
        logger.info("✅ 大金额交易验证成功")
    
    def test_25_long_text_fields(self):
        """测试长文本字段"""
        long_text = "x" * 1000  # 1000个字符的长文本
        
        transaction_data = {
            "card_id": self.card_id,
            "transaction_type": "expense",
            "amount": 100.00,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": long_text[:100],  # 商户名限制在100字符
            "description": long_text,  # 描述可能支持更长文本
            "category": "shopping"
        }
        
        response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        
        # 可能成功创建或者返回验证错误
        if response.status_code == 200:
            data = self.api_test.assert_api_success(response, 200)
            # 验证数据被正确保存
            assert len(data["merchant_name"]) <= 100
        else:
            assert response.status_code == 422  # 数据验证错误
        
        logger.info("✅ 长文本字段验证成功")
    
    def test_26_decimal_precision(self):
        """测试小数精度"""
        transaction_data = {
            "card_id": self.card_id,
            "transaction_type": "expense",
            "amount": 123.456789,  # 多位小数
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "精度测试商户",
            "category": "shopping"
        }
        
        response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证小数精度（通常保留2位小数）
        amount = float(data["amount"])
        assert abs(amount - 123.46) < 0.01, f"金额精度异常: {amount}"
        
        logger.info("✅ 小数精度验证成功")
    
    def test_27_special_characters(self):
        """测试特殊字符处理"""
        special_text = "测试@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        
        transaction_data = {
            "card_id": self.card_id,
            "transaction_type": "expense",
            "amount": 100.00,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": special_text[:50],
            "description": special_text,
            "category": "shopping"
        }
        
        response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        # 验证特殊字符被正确处理
        assert data["merchant_name"] == special_text[:50]
        assert data["description"] == special_text
        
        logger.info("✅ 特殊字符处理验证成功")
    
    def test_28_concurrent_operations(self):
        """测试并发操作"""
        results = []
        errors = []
        
        def create_transaction(thread_id):
            try:
                transaction_data = {
                    "card_id": self.card_id,
                    "transaction_type": "expense",
                    "amount": 100.00 + thread_id,
                    "transaction_date": "2024-06-08T14:30:00",
                    "merchant_name": f"并发测试商户{thread_id}",
                    "category": "shopping"
                }
                
                response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
                if response.status_code == 200:
                    results.append(response.json())
                else:
                    errors.append(f"Thread {thread_id}: {response.status_code}")
            except Exception as e:
                errors.append(f"Thread {thread_id}: {str(e)}")
        
        # 启动5个并发线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_transaction, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        assert len(results) >= 3, f"并发创建成功数量不足，成功{len(results)}个，错误{len(errors)}个"
        if errors:
            logger.warning(f"并发操作中有错误: {errors}")
        
        logger.info(f"✅ 并发操作验证成功，成功{len(results)}个，错误{len(errors)}个")
    
    def test_29_performance_baseline(self):
        """测试性能基准"""
        # 测试创建操作的性能
        start_time = time.time()
        
        transaction_data = {
            "card_id": self.card_id,
            "transaction_type": "expense",
            "amount": 100.00,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "性能测试商户",
            "category": "shopping"
        }
        
        response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        data = self.api_test.assert_api_success(response, 200)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 创建操作应该在2秒内完成
        assert response_time < 2.0, f"创建操作耗时过长: {response_time:.2f}秒"
        
        # 测试查询操作的性能
        start_time = time.time()
        
        response = self.client.get("/api/transactions", headers=self.headers)
        self.api_test.assert_api_success(response, 200)
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # 查询操作应该在1秒内完成
        assert response_time < 1.0, f"查询操作耗时过长: {response_time:.2f}秒"
        
        logger.info("✅ 性能基准验证成功")
    
    def test_30_transaction_types_validation(self):
        """测试交易类型验证"""
        valid_types = ["expense", "payment", "refund", "transfer"]
        invalid_type = "invalid_type"
        
        # 测试有效类型
        for trans_type in valid_types:
            transaction_data = {
                "card_id": self.card_id,
                "transaction_type": trans_type,
                "amount": 100.00,
                "transaction_date": "2024-06-08T14:30:00",
                "merchant_name": f"测试{trans_type}",
                "category": "shopping"
            }
            
            response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
            # 应该成功创建或者有其他业务逻辑限制
            assert response.status_code in [200, 400, 422]
        
        # 测试无效类型
        transaction_data = {
            "card_id": self.card_id,
            "transaction_type": invalid_type,
            "amount": 100.00,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "测试无效类型",
            "category": "shopping"
        }
        
        response = self.client.post("/api/transactions", json=transaction_data, headers=self.headers)
        assert response.status_code == 422  # 数据验证错误
        
        logger.info("✅ 交易类型验证成功")


class TransactionTestDataGenerator:
    """交易测试数据生成器"""
    
    @staticmethod
    def generate_test_transaction(card_id: str, **kwargs) -> Dict:
        """生成单个测试交易记录"""
        import time
        import random
        
        timestamp = int(time.time() * 1000000) % 1000000  # 微秒级时间戳
        
        default_data = {
            "card_id": card_id,
            "transaction_type": "expense",
            "amount": round(random.uniform(10.0, 1000.0), 2),
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": f"测试商户{timestamp}",
            "description": f"测试交易{timestamp}",
            "category": random.choice(["dining", "shopping", "transport", "entertainment", "other"]),
            "status": "completed",
            "points_earned": 0.0,
            "points_rate": 1.0,
            "location": "测试地点"
        }
        
        # 用传入的参数覆盖默认值
        default_data.update(kwargs)
        return default_data
    
    @staticmethod
    def generate_multiple_transactions(card_id: str, count: int = 5) -> List[Dict]:
        """生成多个测试交易记录"""
        transactions = []
        for i in range(count):
            transactions.append(
                TransactionTestDataGenerator.generate_test_transaction(
                    card_id, 
                    merchant_name=f"测试商户{i+1}",
                    amount=100.0 + i * 50.0
                )
            )
        return transactions