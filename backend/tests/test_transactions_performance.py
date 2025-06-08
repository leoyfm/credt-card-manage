"""
交易接口性能测试

测试交易接口在大量数据情况下的性能表现。
"""

import pytest
import time
from typing import Dict, Any
from fastapi.testclient import TestClient

from tests.conftest import create_test_transaction, assert_response_success


@pytest.mark.slow
class TestTransactionPerformance:
    """交易接口性能测试"""

    def test_create_multiple_transactions_performance(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试批量创建交易记录的性能"""
        start_time = time.time()
        
        # 创建100条交易记录
        for i in range(100):
            create_test_transaction(
                client, authenticated_user["headers"], test_card["id"], {
                    "transaction_type": "expense",
                    "amount": 100.00 + i,
                    "merchant_name": f"商户{i+1}",
                    "category": "dining" if i % 2 == 0 else "shopping"
                }
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n创建100条交易记录耗时: {duration:.2f}秒")
        print(f"平均每条记录耗时: {duration/100:.4f}秒")
        
        # 性能断言（期望每条记录创建时间不超过1秒）
        assert duration / 100 < 1.0, f"每条记录创建时间过长: {duration/100:.4f}秒"

    def test_get_transactions_list_performance(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试获取大量交易记录列表的性能"""
        # 先创建500条交易记录
        for i in range(500):
            create_test_transaction(
                client, authenticated_user["headers"], test_card["id"], {
                    "transaction_type": "expense",
                    "amount": 100.00 + i,
                    "merchant_name": f"商户{i+1}"
                }
            )
        
        # 测试分页查询性能
        start_time = time.time()
        
        response = client.get(
            "/api/transactions/?page=1&page_size=50",
            headers=authenticated_user["headers"]
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        data = assert_response_success(response)
        
        print(f"\n查询50条交易记录耗时: {duration:.4f}秒")
        print(f"总记录数: {data['pagination']['total']}")
        
        # 性能断言（期望查询时间不超过2秒）
        assert duration < 2.0, f"查询时间过长: {duration:.4f}秒"
        assert len(data["items"]) == 50

    def test_search_transactions_performance(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试交易记录搜索的性能"""
        # 创建测试数据
        merchants = ["星巴克", "麦当劳", "肯德基", "必胜客", "汉堡王"]
        for i in range(200):
            merchant = merchants[i % len(merchants)]
            create_test_transaction(
                client, authenticated_user["headers"], test_card["id"], {
                    "transaction_type": "expense",
                    "amount": 50.00 + i,
                    "merchant_name": f"{merchant}{i//len(merchants)+1}号店"
                }
            )
        
        # 测试搜索性能
        start_time = time.time()
        
        response = client.get(
            "/api/transactions/?keyword=星巴克",
            headers=authenticated_user["headers"]
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        data = assert_response_success(response)
        
        print(f"\n搜索'星巴克'耗时: {duration:.4f}秒")
        print(f"搜索结果数: {len(data['items'])}")
        
        # 性能断言
        assert duration < 1.0, f"搜索时间过长: {duration:.4f}秒"
        assert len(data["items"]) > 0

    def test_statistics_performance(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """测试统计接口的性能"""
        # 创建大量不同类型的交易记录
        categories = ["dining", "shopping", "transport", "entertainment", "medical"]
        transaction_types = ["expense", "payment", "refund"]
        
        for i in range(300):
            category = categories[i % len(categories)]
            trans_type = transaction_types[i % len(transaction_types)]
            
            create_test_transaction(
                client, authenticated_user["headers"], test_card["id"], {
                    "transaction_type": trans_type,
                    "amount": 100.00 + i,
                    "category": category,
                    "transaction_date": f"2024-{(i%12)+1:02d}-{(i%28)+1:02d}T14:30:00"
                }
            )
        
        # 测试统计概览性能
        start_time = time.time()
        response = client.get(
            "/api/transactions/statistics/overview",
            headers=authenticated_user["headers"]
        )
        overview_duration = time.time() - start_time
        assert_response_success(response)
        
        # 测试分类统计性能
        start_time = time.time()
        response = client.get(
            "/api/transactions/statistics/categories",
            headers=authenticated_user["headers"]
        )
        categories_duration = time.time() - start_time
        assert_response_success(response)
        
        # 测试月度趋势性能
        start_time = time.time()
        response = client.get(
            "/api/transactions/statistics/monthly-trend?year=2024",
            headers=authenticated_user["headers"]
        )
        trend_duration = time.time() - start_time
        assert_response_success(response)
        
        print(f"\n统计接口性能:")
        print(f"  概览统计: {overview_duration:.4f}秒")
        print(f"  分类统计: {categories_duration:.4f}秒")
        print(f"  月度趋势: {trend_duration:.4f}秒")
        
        # 性能断言（所有统计接口都应在2秒内完成）
        assert overview_duration < 2.0, f"概览统计时间过长: {overview_duration:.4f}秒"
        assert categories_duration < 2.0, f"分类统计时间过长: {categories_duration:.4f}秒"
        assert trend_duration < 2.0, f"月度趋势时间过长: {trend_duration:.4f}秒"

    def test_concurrent_operations_simulation(
        self, client: TestClient, authenticated_user: Dict[str, Any], test_card: Dict[str, Any]
    ):
        """模拟并发操作"""
        import threading
        import concurrent.futures
        
        def create_transaction():
            """创建单个交易记录"""
            try:
                create_test_transaction(
                    client, authenticated_user["headers"], test_card["id"], {
                        "transaction_type": "expense",
                        "amount": 100.00,
                        "merchant_name": f"商户{threading.current_thread().ident}"
                    }
                )
                return True
            except Exception as e:
                print(f"创建交易失败: {e}")
                return False
        
        start_time = time.time()
        
        # 模拟10个并发用户同时创建交易
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_transaction) for _ in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        duration = end_time - start_time
        
        success_count = sum(results)
        
        print(f"\n并发测试结果:")
        print(f"  总耗时: {duration:.2f}秒")
        print(f"  成功创建: {success_count}/20")
        print(f"  成功率: {success_count/20*100:.1f}%")
        
        # 断言大部分操作成功
        assert success_count >= 18, f"并发操作成功率过低: {success_count}/20" 