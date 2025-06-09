"""
测试基础类

提供统一的测试基础设施和公共方法，支持两种测试模式：
1. 单元测试模式（TestClient）
2. 集成测试模式（Requests）
"""

import pytest
import requests
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union, List
from fastapi.testclient import TestClient
from uuid import uuid4
import time
import json

from main import app
from tests.conftest import assert_response_success, assert_response_error

logger = logging.getLogger(__name__)


class BaseTestClient(ABC):
    """测试客户端基础类"""
    
    @abstractmethod
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict] = None):
        """GET请求"""
        pass
    
    @abstractmethod
    def post(self, url: str, json: Optional[Dict] = None, headers: Optional[Dict[str, str]] = None):
        """POST请求"""
        pass
    
    @abstractmethod
    def put(self, url: str, json: Optional[Dict] = None, headers: Optional[Dict[str, str]] = None):
        """PUT请求"""
        pass
    
    @abstractmethod
    def delete(self, url: str, headers: Optional[Dict[str, str]] = None):
        """DELETE请求"""
        pass


class FastAPITestClient(BaseTestClient):
    """FastAPI TestClient封装"""
    
    def __init__(self):
        self.client = TestClient(app)
    
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict] = None):
        return self.client.get(url, headers=headers, params=params)
    
    def post(self, url: str, json: Optional[Dict] = None, headers: Optional[Dict[str, str]] = None):
        return self.client.post(url, json=json, headers=headers)
    
    def put(self, url: str, json: Optional[Dict] = None, headers: Optional[Dict[str, str]] = None):
        return self.client.put(url, json=json, headers=headers)
    
    def delete(self, url: str, headers: Optional[Dict[str, str]] = None):
        return self.client.delete(url, headers=headers)


class RequestsTestClient(BaseTestClient):
    """Requests HTTP客户端封装"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
    
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict] = None):
        return requests.get(f"{self.base_url}{url}", headers=headers, params=params)
    
    def post(self, url: str, json: Optional[Dict] = None, headers: Optional[Dict[str, str]] = None):
        return requests.post(f"{self.base_url}{url}", json=json, headers=headers)
    
    def put(self, url: str, json: Optional[Dict] = None, headers: Optional[Dict[str, str]] = None):
        return requests.put(f"{self.base_url}{url}", json=json, headers=headers)
    
    def delete(self, url: str, headers: Optional[Dict[str, str]] = None):
        return requests.delete(f"{self.base_url}{url}", headers=headers)


class BaseAPITest:
    """API测试基础类"""
    
    # 测试配置
    TEST_USER = {
        "username": "test_user",
        "password": "TestPass123456",
        "email": "test@example.com",
        "nickname": "测试用户"
    }
    
    def __init__(self, client: BaseTestClient):
        self.client = client
        self.auth_token = None
        self.user_id = None
        self.headers = {}
    
    def setup_test_user(self) -> Dict[str, Any]:
        """设置测试用户（自动注册和登录）"""
        unique_id = uuid4().hex[:8]
        test_user = {
            "username": f"{self.TEST_USER['username']}_{unique_id}",
            "email": f"test_{unique_id}@example.com", 
            "password": self.TEST_USER["password"],
            "nickname": f"{self.TEST_USER['nickname']}_{unique_id}"
        }
        
        # 尝试注册用户
        register_response = self.client.post("/api/auth/register", json=test_user)
        if register_response.status_code not in [200, 201]:
            logger.warning(f"用户注册失败: {register_response.text}")
        
        # 登录获取token
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        
        login_response = self.client.post("/api/auth/login/username", json=login_data)
        assert login_response.status_code == 200, f"登录失败: {login_response.text}"
        
        result = login_response.json()
        assert result.get("success", True), f"登录失败: {result}"
        
        # 解析token和用户信息
        if result.get("data"):
            self.auth_token = result["data"]["access_token"]
            self.user_id = result["data"]["user"]["id"]
        else:
            # 兼容老格式
            self.auth_token = result.get("access_token")
            self.user_id = result.get("user", {}).get("id")
        
        self.headers = {"Authorization": f"Bearer {self.auth_token}"}
        
        logger.info(f"✅ 测试用户设置成功: {test_user['username']}")
        return {
            "user": test_user,
            "token": self.auth_token,
            "user_id": self.user_id,
            "headers": self.headers
        }
    
    def create_test_card(self, card_data: Optional[Dict] = None) -> Dict[str, Any]:
        """创建测试信用卡"""
        if not self.headers:
            raise ValueError("请先调用setup_test_user()设置认证信息")
        
        import random
        default_card_data = {
            "card_name": "测试信用卡",
            "bank_name": "测试银行",
            "card_number": f"6225{random.randint(100000000000, 999999999999)}",
            "card_type": "visa",
            "credit_limit": 50000.00,
            "expiry_month": 12,
            "expiry_year": 2027,
            "billing_day": 5,
            "due_day": 25,
            "used_amount": 0.0,
            "annual_fee_enabled": False
        }
        
        if card_data:
            default_card_data.update(card_data)
        
        response = self.client.post("/api/cards", json=default_card_data, headers=self.headers)
        assert response.status_code in [200, 201], f"创建信用卡失败: {response.text}"
        
        result = response.json()
        if result.get("success", True):
            return result["data"]
        else:
            raise ValueError(f"创建信用卡失败: {result}")
    
    def create_test_transaction(self, card_id: str, transaction_data: Optional[Dict] = None) -> Dict[str, Any]:
        """创建测试交易记录"""
        if not self.headers:
            raise ValueError("请先调用setup_test_user()设置认证信息")
        
        default_transaction_data = {
            "card_id": card_id,
            "transaction_type": "expense",
            "amount": 100.00,
            "transaction_date": "2024-06-08T14:30:00",
            "merchant_name": "测试商户",
            "description": "测试交易",
            "category": "dining",
            "status": "completed",
            "points_earned": 10.0,
            "points_rate": 1.0,
            "reference_number": f"TEST{uuid4().hex[:8]}",
            "location": "测试地点",
            "is_installment": False,
            "installment_count": None
        }
        
        if transaction_data:
            default_transaction_data.update(transaction_data)
        
        response = self.client.post("/api/transactions", json=default_transaction_data, headers=self.headers)
        assert response.status_code in [200, 201], f"创建交易记录失败: {response.text}"
        
        result = response.json()
        if result.get("success", True):
            return result["data"]
        else:
            raise ValueError(f"创建交易记录失败: {result}")
    
    def assert_api_success(self, response, expected_status: int = 200) -> Dict[str, Any]:
        """断言API响应成功"""
        assert response.status_code == expected_status, f"期望状态码{expected_status}，实际{response.status_code}: {response.text}"
        
        result = response.json()
        assert result.get("success", True), f"API调用失败: {result.get('message', '未知错误')}"
        
        return result.get("data", {})
    
    def assert_api_error(self, response, expected_status: Optional[int] = None) -> Dict[str, Any]:
        """断言API响应错误"""
        if expected_status:
            assert response.status_code == expected_status, f"期望状态码{expected_status}，实际{response.status_code}"
        
        result = response.json()
        if "success" in result:
            assert result["success"] is False, "期望API调用失败，但实际成功"
        
        return result
    
    def assert_pagination_response(self, data: Dict[str, Any], min_items: int = 0) -> None:
        """断言分页响应格式正确"""
        assert "items" in data, "响应缺少items字段"
        assert "pagination" in data, "响应缺少pagination字段"
        
        pagination = data["pagination"]
        required_fields = ["total", "current_page", "page_size", "total_pages"]
        for field in required_fields:
            assert field in pagination, f"分页信息缺少{field}字段"
        
        assert len(data["items"]) >= min_items, f"期望至少{min_items}个项目，实际{len(data['items'])}个"
        assert pagination["total"] >= len(data["items"]), "分页总数不能小于当前页项目数"


class BaseRecommendationTest(BaseAPITest):
    """推荐接口测试基础类"""
    
    def test_user_profile_stats(self):
        """测试用户画像分析"""
        response = self.client.get("/api/recommendations/stats/user-profile", headers=self.headers)
        data = self.assert_api_success(response)
        
        # 验证用户画像数据结构
        required_fields = [
            "total_cards", "total_limit", "used_limit", "utilization_rate",
            "monthly_spending", "top_categories", "avg_transaction_amount"
        ]
        for field in required_fields:
            assert field in data, f"用户画像缺少{field}字段"
        
        return data
    
    def test_generate_recommendations(self):
        """测试生成个性化推荐"""
        response = self.client.post("/api/recommendations/generate", headers=self.headers)
        data = self.assert_api_success(response)
        
        assert isinstance(data, list), "推荐结果应该是列表"
        
        # 验证推荐结构
        for rec in data[:3]:  # 检查前3条
            required_fields = [
                "id", "title", "bank_name", "card_name", "recommendation_type",
                "recommendation_score", "reason", "description"
            ]
            for field in required_fields:
                assert field in rec, f"推荐缺少{field}字段"
            
            assert 0 <= rec["recommendation_score"] <= 100, "推荐评分应在0-100范围内"
        
        return data
    
    def test_get_recommendations_list(self, page: int = 1, page_size: int = 20, keyword: str = ""):
        """测试获取推荐列表"""
        params = {"page": page, "page_size": page_size}
        if keyword:
            params["keyword"] = keyword
        
        response = self.client.get("/api/recommendations", headers=self.headers, params=params)
        data = self.assert_api_success(response)
        
        self.assert_pagination_response(data)
        return data


class BaseStatisticsTest(BaseAPITest):
    """统计接口测试基础类"""
    
    def test_statistics_overview(self):
        """测试统计概览"""
        response = self.client.get("/api/statistics/overview", headers=self.headers)
        data = self.assert_api_success(response)
        
        # 验证统计概览结构
        required_sections = [
            "card_stats", "credit_stats", "transaction_stats", 
            "annual_fee_stats", "top_categories", "monthly_trends", "bank_distribution"
        ]
        for section in required_sections:
            assert section in data, f"统计概览缺少{section}部分"
        
        return data
    
    def test_card_statistics(self):
        """测试信用卡统计"""
        response = self.client.get("/api/statistics/cards", headers=self.headers)
        data = self.assert_api_success(response)
        
        required_fields = [
            "total_cards", "active_cards", "inactive_cards", 
            "frozen_cards", "cancelled_cards", "expired_cards", "expiring_soon_cards"
        ]
        for field in required_fields:
            assert field in data, f"信用卡统计缺少{field}字段"
            assert isinstance(data[field], int), f"{field}应该是整数"
            assert data[field] >= 0, f"{field}不能为负数"
        
        return data
    
    def test_transaction_statistics(self):
        """测试交易统计"""
        response = self.client.get("/api/statistics/transactions", headers=self.headers)
        data = self.assert_api_success(response)
        
        required_fields = [
            "total_transactions", "total_expense_amount", "total_payment_amount",
            "total_points_earned", "current_month_transactions", 
            "current_month_expense_amount", "average_transaction_amount"
        ]
        for field in required_fields:
            assert field in data, f"交易统计缺少{field}字段"
        
        return data


class TestPerformanceMixin:
    """性能测试混入类"""
    
    def measure_response_time(self, func, max_time: float = 2.0, description: str = "操作"):
        """测量单次响应时间"""
        import time
        start_time = time.time()
        result = func()
        end_time = time.time()
        
        duration = end_time - start_time
        success = duration < max_time
        
        if not success:
            print(f"❌ {description}响应时间过长: {duration:.3f}s > {max_time}s")
        else:
            print(f"⏱️  {description}响应时间: {duration:.3f}s")
        
        return {
            "success": success,
            "response_time": duration,
            "result": result
        }
    
    def measure_multiple_requests(self, func, count: int = 10, max_avg_time: float = 1.0, description: str = "批量操作"):
        """测量多次请求的平均性能"""
        import time
        results = []
        total_time = 0
        
        for i in range(count):
            start_time = time.time()
            result = func()
            end_time = time.time()
            
            duration = end_time - start_time
            total_time += duration
            results.append(result)
        
        avg_time = total_time / count
        success = avg_time < max_avg_time
        
        if not success:
            print(f"❌ {description}平均响应时间过长: {avg_time:.3f}s > {max_avg_time}s")
        else:
            print(f"📊 {description}性能: 平均 {avg_time:.3f}s，总计 {count} 次")
        
        return {
            "success": success,
            "avg_response_time": avg_time,
            "total_time": total_time,
            "total_requests": count,
            "results": results
        }
    
    def measure_batch_operations_performance(self, operation_func, count: int = 10, max_avg_time: float = 1.0, description: str = "批量操作"):
        """测量批量操作性能"""
        import time
        start_time = time.time()
        
        result = operation_func()
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / count if count > 0 else total_time
        
        success = avg_time < max_avg_time
        
        if not success:
            print(f"❌ {description}平均操作时间过长: {avg_time:.3f}s > {max_avg_time}s")
        else:
            print(f"📊 {description}: {count}次操作，总时间{total_time:.3f}s，平均{avg_time:.3f}s")
        
        return {
            "success": success,
            "avg_response_time": avg_time,
            "total_time": total_time,
            "count": count,
            "result": result
        }
    
    def measure_concurrent_operations_performance(self, operation_func, concurrent_count: int = 5, iterations_per_thread: int = 2, max_avg_time: float = 3.0, description: str = "并发操作"):
        """测量并发操作性能"""
        import time
        import threading
        
        results = []
        times = []
        lock = threading.Lock()
        
        def worker():
            for _ in range(iterations_per_thread):
                start_time = time.time()
                success = operation_func()
                end_time = time.time()
                
                with lock:
                    results.append(success)
                    times.append(end_time - start_time)
        
        # 启动并发线程
        threads = []
        start_time = time.time()
        
        for _ in range(concurrent_count):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 计算统计信息
        success_count = sum(1 for r in results if r)
        total_operations = len(results)
        success_rate = success_count / total_operations if total_operations > 0 else 0
        avg_time = sum(times) / len(times) if times else 0
        
        overall_success = avg_time < max_avg_time
        
        if not overall_success:
            print(f"❌ {description}平均时间过长: {avg_time:.3f}s > {max_avg_time}s")
        else:
            print(f"🔄 {description}: {concurrent_count}并发×{iterations_per_thread}次，成功率{success_rate:.1%}，平均{avg_time:.3f}s")
        
        return {
            "success": overall_success,
            "avg_response_time": avg_time,
            "total_time": total_time,
            "concurrent_count": concurrent_count,
            "iterations_per_thread": iterations_per_thread,
            "total_operations": total_operations,
            "success_count": success_count,
            "success_rate": success_rate
        }


class TestDataGenerator:
    """测试数据生成器"""
    
    @staticmethod
    def generate_test_cards(count: int = 5) -> List[Dict[str, Any]]:
        """生成测试信用卡数据"""
        import random
        banks = ["招商银行", "工商银行", "建设银行", "农业银行", "中信银行"]
        card_types = ["visa", "mastercard", "unionpay"]
        
        cards = []
        for i in range(count):
            cards.append({
                "card_name": f"测试信用卡{i+1}",
                "bank_name": banks[i % len(banks)],
                "card_number": f"6225{random.randint(100000000000, 999999999999)}",
                "card_type": card_types[i % len(card_types)],
                "credit_limit": 10000.0 * (i + 1),
                "expiry_month": (i % 12) + 1,
                "expiry_year": 2026 + (i % 3),  # 改为2026-2028
                "billing_day": (i % 28) + 1,
                "due_day": (i % 28) + 1,
                "used_amount": 1000.0 * i,
                "annual_fee_enabled": i % 2 == 0
            })
        
        return cards
    
    @staticmethod
    def generate_test_transactions(card_id: str, count: int = 10) -> List[Dict[str, Any]]:
        """生成测试交易数据"""
        categories = ["dining", "shopping", "transport", "entertainment", "medical"]
        merchants = ["星巴克", "麦当劳", "滴滴出行", "万达影城", "协和医院"]
        
        transactions = []
        for i in range(count):
            is_installment = i % 5 == 0
            transactions.append({
                "card_id": card_id,
                "transaction_type": "expense",
                "amount": 50.0 + i * 25.0,
                "transaction_date": f"2024-{(i%12)+1:02d}-{(i%28)+1:02d}T14:30:00",
                "merchant_name": merchants[i % len(merchants)],
                "description": f"测试交易{i+1}",
                "category": categories[i % len(categories)],
                "status": "completed",
                "points_earned": (50.0 + i * 25.0) * 0.1,
                "points_rate": 1.0,
                "reference_number": f"TEST{uuid4().hex[:8]}",
                "location": f"测试地点{i+1}",
                "is_installment": is_installment,
                "installment_count": 12 if is_installment else None
            })
        
        return transactions 