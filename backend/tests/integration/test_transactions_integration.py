"""
交易模块集成测试

使用真实HTTP请求测试交易模块的端到端功能。
需要手动启动服务器：python start.py dev

覆盖范围：
- 端到端交易流程测试
- 复杂业务场景验证
- 网络层协议验证
- 真实用户操作模拟
- 安全性和权限验证
- 数据一致性检查
"""

import pytest
import logging
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List
from uuid import uuid4

from tests.base_test import RequestsTestClient, BaseAPITest

logger = logging.getLogger(__name__)


class TransactionIntegrationTestDataGenerator:
    """交易集成测试数据生成器"""
    
    @staticmethod
    def generate_integration_card_data() -> Dict[str, Any]:
        """生成集成测试用信用卡数据"""
        unique_id = int(time.time() * 1000000) % 1000000  # 微秒级时间戳
        return {
            "card_name": f"集成测试卡{unique_id}",
            "bank_name": "集成测试银行",
            "card_number": f"622588{unique_id:010d}",  # 确保16位数字
            "card_type": "visa",
            "credit_limit": 100000.00,
            "expiry_month": 12,
            "expiry_year": 2027,
            "billing_day": 5,
            "due_day": 25,
            "used_amount": 0.0,
            "annual_fee_enabled": True,
            "annual_fee": 599.0
        }
    
    @staticmethod
    def generate_integration_transaction_data(card_id: str) -> Dict[str, Any]:
        """生成集成测试用交易数据"""
        unique_id = int(time.time() * 1000000) % 1000000
        return {
            "card_id": card_id,
            "transaction_type": "expense",
            "amount": 258.80,
            "transaction_date": datetime.now().isoformat(),
            "merchant_name": f"集成测试商户{unique_id}",
            "description": f"集成测试交易{unique_id}",
            "category": "dining",
            "status": "completed",
            "points_earned": 25.88,
            "points_rate": 1.0,
            "reference_number": f"INTTEST{unique_id}",
            "location": f"集成测试地点{unique_id}",
            "is_installment": False,
            "installment_months": None,
            "installment_fee": None,
            "notes": f"集成测试备注{unique_id}"
        }
    
    @staticmethod
    def generate_batch_transactions(card_id: str, count: int = 5) -> List[Dict[str, Any]]:
        """生成批量交易数据"""
        transactions = []
        base_time = datetime.now()
        
        for i in range(count):
            unique_id = int(time.time() * 1000000) % 1000000 + i
            transaction_time = base_time - timedelta(days=i)
            
            transactions.append({
                "card_id": card_id,
                "transaction_type": "expense",
                "amount": 100.0 + (i * 50),
                "transaction_date": transaction_time.isoformat(),
                "merchant_name": f"批量商户{unique_id}",
                "description": f"批量交易{i+1}",
                "category": ["dining", "shopping", "transport", "entertainment", "fuel"][i % 5],
                "status": "completed",
                "points_earned": 10.0 + (i * 5),
                "points_rate": 1.0,
                "reference_number": f"BATCH{unique_id}",
                "location": f"地点{i+1}",
                "is_installment": False,
                "notes": f"批量测试交易{i+1}"
            })
        
        return transactions


@pytest.mark.integration
@pytest.mark.requires_server
class TestTransactionsIntegration(BaseAPITest):
    """交易模块集成测试"""
    
    def setup_class(self):
        """测试类初始化"""
        client = RequestsTestClient()
        super().__init__(client)  # 正确初始化父类
        self._check_server_availability()
        self.user_data = self.setup_test_user()
        self.test_card = self.create_test_card(
            TransactionIntegrationTestDataGenerator.generate_integration_card_data()
        )
        logger.info("✅ 交易集成测试环境设置完成")
    
    def _check_server_availability(self):
        """检查服务器是否可用"""
        try:
            response = self.client.get("/health")
            if response.status_code != 200:
                raise Exception(f"服务器健康检查失败: {response.status_code}")
            logger.info("✅ 服务器可用")
        except Exception as e:
            pytest.skip(f"❌ 服务器不可用，跳过集成测试: {str(e)}\n"
                        f"请先启动服务器: python start.py dev")
    
    # ==================== 端到端流程测试 ====================
    
    def test_01_complete_transaction_lifecycle(self):
        """测试完整的交易生命周期"""
        logger.info("🧪 测试完整交易生命周期")
        
        # 1. 创建交易
        transaction_data = TransactionIntegrationTestDataGenerator.generate_integration_transaction_data(
            self.test_card["id"]
        )
        
        create_response = self.client.post(
            "/api/transactions", 
            json=transaction_data, 
            headers=self.headers
        )
        create_result = self.assert_api_success(create_response, 200)
        created_transaction = create_result["data"]
        
        assert created_transaction["id"] is not None
        assert created_transaction["amount"] == transaction_data["amount"]
        assert created_transaction["merchant_name"] == transaction_data["merchant_name"]
        
        transaction_id = created_transaction["id"]
        
        # 2. 查询交易详情
        get_response = self.client.get(
            f"/api/transactions/{transaction_id}",
            headers=self.headers
        )
        get_result = self.assert_api_success(get_response, 200)
        retrieved_transaction = get_result["data"]
        
        assert retrieved_transaction["id"] == transaction_id
        assert retrieved_transaction["status"] == "completed"
        
        # 3. 更新交易信息
        update_data = {
            "notes": "集成测试更新备注",
            "category": "shopping"
        }
        
        update_response = self.client.put(
            f"/api/transactions/{transaction_id}",
            json=update_data,
            headers=self.headers
        )
        update_result = self.assert_api_success(update_response, 200)
        updated_transaction = update_result["data"]
        
        assert updated_transaction["notes"] == update_data["notes"]
        assert updated_transaction["category"] == update_data["category"]
        
        # 4. 在列表中验证交易
        list_response = self.client.get(
            "/api/transactions",
            params={"page": 1, "page_size": 10},
            headers=self.headers
        )
        list_result = self.assert_api_success(list_response, 200)
        
        found_transaction = None
        for transaction in list_result["data"]["items"]:
            if transaction["id"] == transaction_id:
                found_transaction = transaction
                break
        
        assert found_transaction is not None
        assert found_transaction["notes"] == update_data["notes"]
        
        # 5. 删除交易
        delete_response = self.client.delete(
            f"/api/transactions/{transaction_id}",
            headers=self.headers
        )
        self.assert_api_success(delete_response, 200)
        
        # 6. 验证删除成功
        verify_response = self.client.get(
            f"/api/transactions/{transaction_id}",
            headers=self.headers
        )
        assert verify_response.status_code == 404
        
        logger.info("✅ 完整交易生命周期测试通过")
    
    def test_02_network_and_format_validation(self):
        """测试网络层和数据格式验证"""
        logger.info("🧪 测试网络层和数据格式验证")
        
        # 测试HTTP响应头
        response = self.client.get("/api/transactions", headers=self.headers)
        
        assert response.headers.get("content-type", "").startswith("application/json")
        assert response.status_code == 200
        
        # 测试JSON响应格式
        result = response.json()
        assert "success" in result
        assert "data" in result
        assert "message" in result
        
        # 验证分页响应格式
        data = result["data"]
        self.assert_pagination_response(data, min_items=0)
        
        logger.info("✅ 网络层和数据格式验证通过")
    
    def test_03_concurrent_operations(self):
        """测试并发操作"""
        logger.info("🧪 测试并发交易操作")
        
        import threading
        import queue
        
        # 创建多个交易数据
        transaction_data_list = [
            TransactionIntegrationTestDataGenerator.generate_integration_transaction_data(
                self.test_card["id"]
            ) for _ in range(3)
        ]
        
        results = queue.Queue()
        
        def create_transaction(data):
            try:
                response = self.client.post(
                    "/api/transactions", 
                    json=data, 
                    headers=self.headers
                )
                results.put({
                    "success": response.status_code == 200,
                    "response": response,
                    "data": data
                })
            except Exception as e:
                results.put({
                    "success": False,
                    "error": str(e),
                    "data": data
                })
        
        # 启动并发线程
        threads = []
        for data in transaction_data_list:
            thread = threading.Thread(target=create_transaction, args=(data,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 收集结果
        success_count = 0
        while not results.empty():
            result = results.get()
            if result["success"]:
                success_count += 1
            else:
                logger.warning(f"并发操作失败: {result.get('error', 'Unknown error')}")
        
        # 并发成功率应该大于等于80%
        success_rate = success_count / len(transaction_data_list)
        assert success_rate >= 0.8, f"并发成功率过低: {success_rate:.2%}"
        
        logger.info(f"✅ 并发操作测试通过，成功率: {success_rate:.2%}")
    
    def test_04_user_data_isolation(self):
        """测试用户数据隔离"""
        logger.info("🧪 测试用户数据隔离")
        
        # 创建另一个测试用户
        second_client = RequestsTestClient()
        second_api = BaseAPITest(second_client)
        second_user_data = second_api.setup_test_user()
        second_card = second_api.create_test_card(
            TransactionIntegrationTestDataGenerator.generate_integration_card_data()
        )
        
        # 用户1创建交易
        transaction_data = TransactionIntegrationTestDataGenerator.generate_integration_transaction_data(
            self.test_card["id"]
        )
        
        create_response = self.client.post(
            "/api/transactions", 
            json=transaction_data, 
            headers=self.headers
        )
        create_result = self.assert_api_success(create_response, 200)
        transaction_id = create_result["data"]["id"]
        
        # 用户2尝试访问用户1的交易
        unauthorized_response = second_client.get(
            f"/api/transactions/{transaction_id}",
            headers=second_user_data["headers"]
        )
        assert unauthorized_response.status_code == 404  # 应该返回404表示不存在
        
        # 用户2查看自己的交易列表应该为空
        list_response = second_client.get(
            "/api/transactions",
            headers=second_user_data["headers"]
        )
        list_result = self.assert_api_success(list_response, 200)
        assert len(list_result["data"]["items"]) == 0
        
        logger.info("✅ 用户数据隔离测试通过")
    
    # ==================== 复杂业务场景测试 ====================
    
    def test_05_complex_filtering_scenarios(self):
        """测试复杂筛选场景"""
        logger.info("🧪 测试复杂筛选场景")
        
        # 创建多种类型的交易数据
        transactions_data = TransactionIntegrationTestDataGenerator.generate_batch_transactions(
            self.test_card["id"], 5
        )
        
        created_transactions = []
        for data in transactions_data:
            response = self.client.post(
                "/api/transactions", 
                json=data, 
                headers=self.headers
            )
            result = self.assert_api_success(response, 200)
            created_transactions.append(result["data"])
        
        # 等待数据完全写入
        time.sleep(0.5)
        
        # 测试按金额范围筛选
        response = self.client.get(
            "/api/transactions",
            params={
                "min_amount": 150,
                "max_amount": 300,
                "page": 1,
                "page_size": 10
            },
            headers=self.headers
        )
        result = self.assert_api_success(response, 200)
        
        for transaction in result["data"]["items"]:
            amount = float(transaction["amount"])
            assert 150 <= amount <= 300, f"金额筛选失败: {amount}"
        
        # 测试按分类筛选
        response = self.client.get(
            "/api/transactions",
            params={
                "category": "dining",
                "page": 1,
                "page_size": 10
            },
            headers=self.headers
        )
        result = self.assert_api_success(response, 200)
        
        for transaction in result["data"]["items"]:
            if transaction["category"]:  # 如果有分类信息
                assert transaction["category"] == "dining"
        
        # 测试关键词搜索
        response = self.client.get(
            "/api/transactions",
            params={
                "keyword": "批量",
                "page": 1,
                "page_size": 10
            },
            headers=self.headers
        )
        result = self.assert_api_success(response, 200)
        
        assert len(result["data"]["items"]) > 0
        
        logger.info("✅ 复杂筛选场景测试通过")
    
    def test_06_statistics_integration(self):
        """测试统计功能集成"""
        logger.info("🧪 测试统计功能集成")
        
        # 创建一些交易数据用于统计
        for i in range(3):
            transaction_data = TransactionIntegrationTestDataGenerator.generate_integration_transaction_data(
                self.test_card["id"]
            )
            transaction_data["amount"] = 100.0 * (i + 1)  # 不同金额
            
            response = self.client.post(
                "/api/transactions", 
                json=transaction_data, 
                headers=self.headers
            )
            self.assert_api_success(response, 200)
        
        # 等待数据完全写入
        time.sleep(1.0)
        
        # 测试统计概览
        stats_response = self.client.get(
            "/api/transactions/statistics/overview",
            headers=self.headers
        )
        stats_result = self.assert_api_success(stats_response, 200)
        statistics = stats_result["data"]
        
        assert "total_transactions" in statistics
        assert "total_amount" in statistics
        assert statistics["total_transactions"] >= 3
        assert float(statistics["total_amount"]) > 0
        
        # 测试分类统计
        category_response = self.client.get(
            "/api/transactions/statistics/categories",
            headers=self.headers
        )
        category_result = self.assert_api_success(category_response, 200)
        category_stats = category_result["data"]
        
        assert isinstance(category_stats, list)
        
        # 测试月度趋势
        trend_response = self.client.get(
            "/api/transactions/statistics/monthly-trend",
            headers=self.headers
        )
        trend_result = self.assert_api_success(trend_response, 200)
        trend_data = trend_result["data"]
        
        assert isinstance(trend_data, list)
        
        logger.info("✅ 统计功能集成测试通过")
    
    def test_07_pagination_integration(self):
        """测试分页功能集成"""
        logger.info("🧪 测试分页功能集成")
        
        # 创建足够的交易数据来测试分页
        batch_size = 8
        transactions_data = TransactionIntegrationTestDataGenerator.generate_batch_transactions(
            self.test_card["id"], batch_size
        )
        
        for data in transactions_data:
            response = self.client.post(
                "/api/transactions", 
                json=data, 
                headers=self.headers
            )
            self.assert_api_success(response, 200)
        
        # 等待数据完全写入
        time.sleep(1.0)
        
        # 测试第一页
        page1_response = self.client.get(
            "/api/transactions",
            params={"page": 1, "page_size": 5},
            headers=self.headers
        )
        page1_result = self.assert_api_success(page1_response, 200)
        
        assert len(page1_result["data"]["items"]) >= 5
        assert page1_result["data"]["current_page"] == 1
        assert page1_result["data"]["total"] >= batch_size
        
        # 测试第二页
        page2_response = self.client.get(
            "/api/transactions",
            params={"page": 2, "page_size": 5},
            headers=self.headers
        )
        page2_result = self.assert_api_success(page2_response, 200)
        
        assert page2_result["data"]["current_page"] == 2
        
        # 验证两页数据不重复
        page1_ids = {item["id"] for item in page1_result["data"]["items"]}
        page2_ids = {item["id"] for item in page2_result["data"]["items"]}
        
        assert len(page1_ids.intersection(page2_ids)) == 0, "分页数据存在重复"
        
        logger.info("✅ 分页功能集成测试通过")
    
    def test_08_error_handling_integration(self):
        """测试错误处理集成"""
        logger.info("🧪 测试错误处理集成")
        
        # 测试无效的交易ID
        invalid_response = self.client.get(
            "/api/transactions/invalid-uuid",
            headers=self.headers
        )
        assert invalid_response.status_code in [400, 422, 404]
        
        # 测试不存在的交易ID
        nonexistent_id = str(uuid4())
        nonexistent_response = self.client.get(
            f"/api/transactions/{nonexistent_id}",
            headers=self.headers
        )
        assert nonexistent_response.status_code == 404
        
        # 测试无效的交易数据
        invalid_data = {
            "card_id": "invalid-uuid",
            "amount": -100,  # 负数金额
            "transaction_type": "invalid_type"
        }
        
        invalid_create_response = self.client.post(
            "/api/transactions",
            json=invalid_data,
            headers=self.headers
        )
        assert invalid_create_response.status_code in [400, 422]
        
        # 测试未认证请求
        unauth_response = self.client.get("/api/transactions")
        assert unauth_response.status_code == 401
        
        logger.info("✅ 错误处理集成测试通过")
    
    def test_09_performance_integration(self):
        """测试基本性能集成"""
        logger.info("🧪 测试基本性能集成")
        
        start_time = time.time()
        
        # 创建交易
        transaction_data = TransactionIntegrationTestDataGenerator.generate_integration_transaction_data(
            self.test_card["id"]
        )
        
        create_response = self.client.post(
            "/api/transactions", 
            json=transaction_data, 
            headers=self.headers
        )
        self.assert_api_success(create_response, 200)
        
        create_time = time.time() - start_time
        assert create_time < 5.0, f"创建交易响应时间过长: {create_time:.2f}s"
        
        # 查询列表
        start_time = time.time()
        list_response = self.client.get(
            "/api/transactions",
            params={"page": 1, "page_size": 20},
            headers=self.headers
        )
        self.assert_api_success(list_response, 200)
        
        list_time = time.time() - start_time
        assert list_time < 3.0, f"查询列表响应时间过长: {list_time:.2f}s"
        
        logger.info(f"✅ 基本性能集成测试通过 - 创建: {create_time:.2f}s, 列表: {list_time:.2f}s")
    
    # ==================== 真实用户场景测试 ====================
    
    def test_10_realistic_user_workflow(self):
        """测试真实用户工作流程"""
        logger.info("🧪 测试真实用户工作流程")
        
        # 模拟用户一天的交易记录
        daily_transactions = [
            {
                "description": "早餐 - 星巴克",
                "amount": 35.0,
                "category": "dining",
                "merchant_name": "星巴克咖啡"
            },
            {
                "description": "地铁通勤",
                "amount": 6.0,
                "category": "transport",
                "merchant_name": "地铁"
            },
            {
                "description": "午餐 - 商务套餐",
                "amount": 85.0,
                "category": "dining",
                "merchant_name": "商务酒店"
            },
            {
                "description": "加油",
                "amount": 320.0,
                "category": "fuel",
                "merchant_name": "中石化"
            },
            {
                "description": "超市购物",
                "amount": 156.8,
                "category": "shopping",
                "merchant_name": "沃尔玛"
            }
        ]
        
        created_transaction_ids = []
        
        # 逐个创建交易，模拟实时记录
        for i, tx_info in enumerate(daily_transactions):
            transaction_data = TransactionIntegrationTestDataGenerator.generate_integration_transaction_data(
                self.test_card["id"]
            )
            
            # 覆盖特定信息
            transaction_data.update(tx_info)
            transaction_data["transaction_date"] = (
                datetime.now() - timedelta(hours=8-i*2)
            ).isoformat()
            
            response = self.client.post(
                "/api/transactions", 
                json=transaction_data, 
                headers=self.headers
            )
            result = self.assert_api_success(response, 200)
            created_transaction_ids.append(result["data"]["id"])
            
            # 模拟用户操作间隔
            time.sleep(0.1)
        
        # 用户查看今日消费总览
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        stats_response = self.client.get(
            "/api/transactions/statistics/overview",
            params={
                "start_date": today_start.isoformat(),
                "card_id": self.test_card["id"]
            },
            headers=self.headers
        )
        stats_result = self.assert_api_success(stats_response, 200)
        
        # 验证统计数据合理性
        total_amount = float(stats_result["data"]["total_amount"])
        expected_total = sum(tx["amount"] for tx in daily_transactions)
        
        # 允许一定的误差范围（考虑其他可能的交易）
        assert total_amount >= expected_total
        
        # 用户查看分类统计
        category_response = self.client.get(
            "/api/transactions/statistics/categories",
            params={"start_date": today_start.isoformat()},
            headers=self.headers
        )
        category_result = self.assert_api_success(category_response, 200)
        
        dining_total = sum(
            float(cat["total_amount"]) 
            for cat in category_result["data"] 
            if cat["category"] == "dining"
        )
        
        expected_dining = sum(
            tx["amount"] for tx in daily_transactions 
            if tx["category"] == "dining"
        )
        
        assert dining_total >= expected_dining
        
        logger.info(f"✅ 真实用户工作流程测试通过 - 今日消费: ¥{total_amount:.2f}")
    
    def test_11_data_consistency_check(self):
        """测试数据一致性"""
        logger.info("🧪 测试数据一致性")
        
        # 创建交易并立即查询
        transaction_data = TransactionIntegrationTestDataGenerator.generate_integration_transaction_data(
            self.test_card["id"]
        )
        
        create_response = self.client.post(
            "/api/transactions", 
            json=transaction_data, 
            headers=self.headers
        )
        create_result = self.assert_api_success(create_response, 200)
        created_transaction = create_result["data"]
        transaction_id = created_transaction["id"]
        
        # 多次查询验证数据一致性
        for i in range(3):
            get_response = self.client.get(
                f"/api/transactions/{transaction_id}",
                headers=self.headers
            )
            get_result = self.assert_api_success(get_response, 200)
            retrieved_transaction = get_result["data"]
            
            # 验证关键字段一致性
            assert retrieved_transaction["id"] == created_transaction["id"]
            assert retrieved_transaction["amount"] == created_transaction["amount"]
            assert retrieved_transaction["merchant_name"] == created_transaction["merchant_name"]
            assert retrieved_transaction["status"] == created_transaction["status"]
            
            time.sleep(0.1)
        
        # 在列表中查找并验证数据一致性
        list_response = self.client.get(
            "/api/transactions",
            params={"page": 1, "page_size": 50},
            headers=self.headers
        )
        list_result = self.assert_api_success(list_response, 200)
        
        found_in_list = None
        for transaction in list_result["data"]["items"]:
            if transaction["id"] == transaction_id:
                found_in_list = transaction
                break
        
        assert found_in_list is not None, "创建的交易在列表中找不到"
        assert found_in_list["amount"] == created_transaction["amount"]
        assert found_in_list["merchant_name"] == created_transaction["merchant_name"]
        
        logger.info("✅ 数据一致性检查通过")
    
    def test_12_authentication_security_integration(self):
        """测试认证安全性集成"""
        logger.info("🧪 测试认证安全性集成")
        
        # 测试无token访问
        no_auth_response = self.client.get("/api/transactions")
        assert no_auth_response.status_code == 401
        
        # 测试无效token
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
        invalid_auth_response = self.client.get(
            "/api/transactions",
            headers=invalid_headers
        )
        assert invalid_auth_response.status_code == 401
        
        # 测试过期token（模拟）
        expired_headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.expired"}
        expired_auth_response = self.client.get(
            "/api/transactions",
            headers=expired_headers
        )
        assert expired_auth_response.status_code == 401
        
        # 测试正确认证的访问
        valid_response = self.client.get(
            "/api/transactions",
            headers=self.headers
        )
        assert valid_response.status_code == 200
        
        logger.info("✅ 认证安全性集成测试通过")

