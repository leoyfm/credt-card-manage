"""
示例测试套件

展示新测试框架v2.0的各种功能和用法。
"""

import time
from typing import Any, Dict

# 导入测试框架组件
from tests.framework.decorators.test import (
    test_suite, api_test, smoke_test, performance_test, stress_test,
    tag, priority, timeout, retry, parametrize
)
from tests.framework.decorators.data import with_user, with_cards, with_transactions
from tests.framework.clients.api import FluentAPIClient
from tests.framework.core.assertion import expect, expect_response
from tests.framework.core.suite import TestPriority


@test_suite("示例测试套件", "展示新测试框架v2.0功能的示例套件")
class ExampleTestSuite:
    """示例测试套件类"""
    
    @smoke_test("基础连通性测试")
    @tag("critical", "smoke")
    def test_basic_connectivity(self, api: FluentAPIClient):
        """测试基础API连通性"""
        # 使用流畅的API客户端
        response = api.health_check()
        
        # 使用流畅的断言
        response.should.succeed()
        response.should.with_data(status="ok")
        
        print("✅ 基础连通性测试通过")
    
    @api_test("用户注册流程测试")
    @tag("api", "auth")
    @priority(TestPriority.HIGH)
    def test_user_registration(self, api: FluentAPIClient):
        """测试用户注册流程"""
        # 准备测试数据
        user_data = {
            "username": "test_user_demo",
            "email": "demo@example.com",
            "password": "TestPass123456",
            "nickname": "演示用户"
        }
        
        # 执行注册
        response = api.register_user(user_data)
        
        # 验证响应
        response.should.succeed().with_data(
            username=user_data["username"],
            email=user_data["email"],
            nickname=user_data["nickname"]
        )
        
        print("✅ 用户注册测试通过")
    
    @with_user(username="demo_user")
    @api_test("用户登录测试")
    @tag("api", "auth")
    def test_user_login(self, api: FluentAPIClient, user):
        """测试用户登录功能"""
        # 用户数据已由装饰器自动创建
        print(f"🔐 测试用户: {user.username}")
        
        # 用户已自动登录，验证认证状态
        profile_response = api.get_user_profile()
        profile_response.should.succeed().with_data(
            username=user.username,
            email=user.email
        )
        
        print("✅ 用户登录测试通过")
    
    @with_user()
    @with_cards(count=2, bank_name="演示银行")
    @api_test("信用卡管理测试")
    @tag("api", "cards")
    def test_card_management(self, api: FluentAPIClient, user, cards):
        """测试信用卡管理功能"""
        print(f"💳 用户 {user.username} 有 {len(cards)} 张信用卡")
        
        # 获取信用卡列表
        cards_response = api.get_cards_list()
        cards_response.should.succeed().with_pagination(
            total_items=2,
            items_type="cards"
        )
        
        # 验证每张卡片
        for card in cards:
            print(f"  • {card.card_name} - {card.bank_name}")
            
            # 获取单个卡片详情
            card_detail = api.get(f"/api/v1/user/cards/{card.id}/detail")
            card_detail.should.succeed().with_data(
                card_name=card.card_name,
                bank_name=card.bank_name
            )
        
        print("✅ 信用卡管理测试通过")
    
    @with_user()
    @with_cards(count=1)
    @with_transactions(count=5)
    @api_test("交易记录测试")
    @tag("api", "transactions")
    def test_transaction_management(self, api: FluentAPIClient, user, card, transactions):
        """测试交易记录管理"""
        print(f"💰 用户 {user.username} 有 {len(transactions)} 条交易记录")
        
        # 获取交易列表
        transactions_response = api.get_transactions_list()
        transactions_response.should.succeed().with_pagination(
            total_items=5,
            items_type="transactions"
        )
        
        # 验证交易数据
        total_amount = sum(t.amount for t in transactions)
        print(f"  总消费金额: ¥{total_amount:.2f}")
        
        # 测试交易筛选
        filter_response = api.get("/api/v1/user/transactions/list", {
            "transaction_type": "expense",
            "page_size": 10
        })
        filter_response.should.succeed()
        
        print("✅ 交易记录测试通过")
    
    @performance_test("API响应性能测试", max_duration=2.0)
    @tag("performance", "api")
    def test_api_performance(self, api: FluentAPIClient):
        """测试API响应性能"""
        start_time = time.time()
        
        # 测试多个API端点的响应时间
        endpoints = [
            "/api/v1/public/system/health",
            "/api/v1/user/profile/info",
            "/api/v1/user/cards/list",
            "/api/v1/user/transactions/list",
        ]
        
        for endpoint in endpoints:
            response = api.get(endpoint)
            response.should.succeed()
            print(f"  📊 {endpoint}: {response.response.elapsed.total_seconds():.3f}s")
        
        total_time = time.time() - start_time
        print(f"⏱️ 总响应时间: {total_time:.3f}s")
        
        # 验证总时间在合理范围内
        expect(total_time).should.be_less_than(2.0)
    
    @stress_test("并发压力测试", iterations=20)
    @tag("stress", "api")
    @timeout(30)
    def test_concurrent_requests(self, api: FluentAPIClient):
        """测试并发请求压力"""
        # 这个测试会被压力测试装饰器重复执行20次
        response = api.health_check()
        response.should.succeed()
        
        # 模拟一些处理时间
        time.sleep(0.01)
    
    @parametrize("status_code", [200, 404, 500])
    @api_test("HTTP状态码测试")
    @tag("api", "http")
    def test_http_status_codes(self, api: FluentAPIClient, status_code: int):
        """参数化测试不同的HTTP状态码"""
        if status_code == 200:
            response = api.health_check()
            response.should.succeed()
        elif status_code == 404:
            response = api.get("/api/v1/nonexistent/endpoint")
            response.should.fail(404)
        elif status_code == 500:
            # 假设有一个故意引发500错误的端点
            response = api.get("/api/v1/test/error500")
            response.should.fail(500)
    
    @retry(count=3, delay=1.0)
    @api_test("重试机制测试")
    @tag("reliability", "retry")
    def test_retry_mechanism(self, api: FluentAPIClient):
        """测试重试机制"""
        # 这个测试如果失败会自动重试3次
        import random
        
        # 随机失败来测试重试
        if random.random() < 0.6:  # 60%的失败概率
            raise Exception("模拟的网络错误")
        
        response = api.health_check()
        response.should.succeed()
    
    @api_test("数据验证测试")
    @tag("validation", "data")
    def test_data_validation(self, api: FluentAPIClient):
        """测试数据验证和断言"""
        response = api.health_check()
        
        # 各种断言示例
        expect(response.response.status_code).equal(200)
        expect(response.response.headers.get("content-type")).contain("application/json")
        
        if response.data:
            expect(response.data).have_key("success")
            expect(response.data["success"]).be_true()
            
            # 如果有timestamp字段，验证格式
            if "timestamp" in response.data:
                timestamp = response.data["timestamp"]
                expect(timestamp).not_be_none()
                expect(str(timestamp)).match_pattern(r"\d{4}-\d{2}-\d{2}")
        
        print("✅ 数据验证测试通过")
    
    @api_test("错误处理测试")
    @tag("error", "handling")
    def test_error_handling(self, api: FluentAPIClient):
        """测试错误处理"""
        # 测试无效的请求参数
        invalid_data = {
            "username": "",  # 空用户名
            "email": "invalid-email",  # 无效邮箱
            "password": "123"  # 密码太短
        }
        
        response = api.register_user(invalid_data)
        response.should.fail(422)  # 验证失败
        response.should.with_error()  # 应该包含错误信息
        
        print("✅ 错误处理测试通过")
    
    @api_test("数据类型验证测试")
    @tag("validation", "types")
    def test_data_types(self, api: FluentAPIClient):
        """测试数据类型验证"""
        response = api.health_check()
        response.should.succeed()
        
        # 验证响应数据类型
        data = response.data
        if data:
            expect(data).be_instance_of(dict)
            
            if "success" in data:
                expect(data["success"]).be_instance_of(bool)
            
            if "timestamp" in data:
                expect(data["timestamp"]).be_instance_of(str)
        
        print("✅ 数据类型验证测试通过")


# 如果直接运行此文件，执行一些简单测试
if __name__ == "__main__":
    print("🧪 运行示例测试套件...")
    
    # 创建API客户端
    api = FluentAPIClient()
    
    # 创建测试套件实例
    suite = ExampleTestSuite()
    
    try:
        # 运行基础连通性测试
        print("\n1️⃣ 测试基础连通性...")
        suite.test_basic_connectivity(api)
        
        # 运行数据验证测试
        print("\n2️⃣ 测试数据验证...")
        suite.test_data_validation(api)
        
        print("\n✅ 示例测试完成！")
        print("💡 使用 python run_tests_v2.py 运行完整测试套件")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        print("💡 请确保服务器正在运行: python start.py dev") 