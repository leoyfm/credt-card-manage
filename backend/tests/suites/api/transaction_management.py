"""
交易管理API测试套件

使用新测试框架v2.0进行交易管理功能的全面测试
包括交易记录管理、分类、筛选、统计等功能
"""

import pytest
from tests.framework import (
    test_suite, api_test, with_user, with_cards, with_transactions,
    performance_test, stress_test
)


@test_suite("交易管理API")
class TransactionManagementTests:
    """交易管理功能测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_create_transaction_success(self, api, user, cards):
        """测试成功创建交易记录"""
        card = cards[0] if isinstance(cards, list) else cards
        transaction_data = {
            "card_id": card['id'],
            "transaction_type": "expense",
            "amount": 299.99,
            "description": "测试购物消费",
            "merchant_name": "测试商户",
            "merchant_category": "购物",
            "transaction_date": "2024-12-01T10:30:00Z"
        }
        
        api.post("/api/v1/user/transactions/create", data=transaction_data).should.succeed().with_data(
            transaction_type="expense",
            amount=299.99,
            description="测试购物消费"
        )
    
    @api_test
    @with_user
    def test_create_transaction_validation_error(self, api, user):
        """测试创建交易参数验证"""
        invalid_data = {
            "amount": -100,  # 负金额
            "transaction_type": "invalid_type"  # 无效类型
        }
        
        api.post("/api/v1/user/transactions/create", data=invalid_data).should.fail(422)
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=5)
    def test_get_transactions_list(self, api, user, cards, transactions):
        """测试获取交易列表"""
        api.get("/api/v1/user/transactions/list").should.succeed().with_pagination(
            total_items=5,
            items_type="transaction"
        )
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=1)
    def test_get_transaction_details(self, api, user, cards, transactions):
        """测试获取交易详情"""
        transaction = transactions[0] if isinstance(transactions, list) else transactions
        api.get(f"/api/v1/user/transactions/{transaction['id']}/details").should.succeed().with_data(
            id=transaction['id'],
            amount=transaction['amount']
        )
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=1)
    def test_update_transaction_success(self, api, user, cards, transactions):
        """测试成功更新交易记录"""
        transaction = transactions[0] if isinstance(transactions, list) else transactions
        update_data = {
            "description": "更新后的交易描述",
            "amount": 599.99,
            "merchant_name": "更新商户"
        }
        
        api.put(f"/api/v1/user/transactions/{transaction['id']}/update", data=update_data).should.succeed()
        
        # 验证更新生效
        api.get(f"/api/v1/user/transactions/{transaction['id']}/details").should.succeed().with_data(
            description="更新后的交易描述",
            amount=599.99
        )
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=1)
    def test_delete_transaction_success(self, api, user, cards, transactions):
        """测试成功删除交易记录"""
        transaction = transactions[0] if isinstance(transactions, list) else transactions
        
        api.delete(f"/api/v1/user/transactions/{transaction['id']}/delete").should.succeed()
        
        # 验证交易已删除
        api.get(f"/api/v1/user/transactions/{transaction['id']}/details").should.fail(404)
    
    @api_test
    @with_user
    def test_access_nonexistent_transaction(self, api, user):
        """测试访问不存在的交易"""
        fake_id = "00000000-0000-0000-0000-000000000000"
        api.get(f"/api/v1/user/transactions/{fake_id}/details").should.fail(404)


@test_suite("交易分类管理")
class TransactionCategoryTests:
    """交易分类管理测试套件"""
    
    @api_test
    @with_user
    def test_get_categories(self, api, user):
        """测试获取交易分类"""
        api.get("/api/v1/user/transactions/categories").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_transactions_by_category(self, api, user, cards):
        """测试按分类筛选交易"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建不同分类的交易
        categories = ["餐饮", "购物", "交通"]
        for category in categories:
            api.post("/api/v1/user/transactions/create", data={
                "card_id": card['id'],
                "transaction_type": "expense",
                "amount": 100.00,
                "description": f"{category}消费",
                "merchant_category": category
            }).should.succeed()
        
        # 按分类筛选
        api.get("/api/v1/user/transactions/list?category=餐饮").should.succeed()


@test_suite("交易筛选和排序")
class TransactionFilterTests:
    """交易筛选和排序测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=20)
    def test_transactions_pagination(self, api, user, cards, transactions):
        """测试交易分页功能"""
        # 第一页
        api.get("/api/v1/user/transactions/list?page=1&page_size=10").should.succeed().with_pagination(
            current_page=1,
            total_items=20
        )
        
        # 第二页
        api.get("/api/v1/user/transactions/list?page=2&page_size=10").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_transactions_date_filter(self, api, user, cards):
        """测试按日期筛选交易"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建不同日期的交易
        dates = ["2024-12-01", "2024-11-15", "2024-10-20"]
        for date in dates:
            api.post("/api/v1/user/transactions/create", data={
                "card_id": card['id'],
                "transaction_type": "expense",
                "amount": 100.00,
                "description": f"{date}交易",
                "transaction_date": f"{date}T10:00:00Z"
            }).should.succeed()
        
        # 按日期范围筛选
        api.get("/api/v1/user/transactions/list?start_date=2024-11-01&end_date=2024-12-31").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_transactions_amount_filter(self, api, user, cards):
        """测试按金额筛选交易"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建不同金额的交易
        amounts = [50.00, 150.00, 500.00]
        for amount in amounts:
            api.post("/api/v1/user/transactions/create", data={
                "card_id": card['id'],
                "transaction_type": "expense",
                "amount": amount,
                "description": f"{amount}元交易"
            }).should.succeed()
        
        # 按金额范围筛选
        api.get("/api/v1/user/transactions/list?min_amount=100&max_amount=600").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=10)
    def test_transactions_sorting(self, api, user, cards, transactions):
        """测试交易排序功能"""
        # 按时间降序
        api.get("/api/v1/user/transactions/list?sort=date&order=desc").should.succeed()
        
        # 按金额升序
        api.get("/api/v1/user/transactions/list?sort=amount&order=asc").should.succeed()


@test_suite("交易权限测试")
class TransactionPermissionTests:
    """交易权限验证测试套件"""
    
    @api_test
    @with_user
    def test_unauthorized_access_transaction(self, api, user):
        """测试未授权访问他人交易"""
        other_transaction_id = "11111111-1111-1111-1111-111111111111"
        api.get(f"/api/v1/user/transactions/{other_transaction_id}/details").should.fail(403)
    
    @api_test
    def test_unauthenticated_access(self, api):
        """测试未认证访问交易接口"""
        api.get("/api/v1/user/transactions/list").should.fail(401)


@test_suite("交易性能测试")
class TransactionPerformanceTests:
    """交易管理性能测试套件"""
    
    @performance_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=100)
    def test_transactions_list_performance(self, api, user, cards, transactions):
        """测试交易列表性能"""
        api.get("/api/v1/user/transactions/list").should.succeed().complete_within(seconds=1.0)
    
    @performance_test
    @with_user
    @with_cards(count=1)
    def test_transaction_creation_performance(self, api, user, cards):
        """测试交易创建性能"""
        card = cards[0] if isinstance(cards, list) else cards
        transaction_data = {
            "card_id": card['id'],
            "transaction_type": "expense",
            "amount": 199.99,
            "description": "性能测试交易"
        }
        
        api.post("/api/v1/user/transactions/create", data=transaction_data).should.succeed().complete_within(seconds=0.5)
    
    @stress_test(concurrent_users=15, duration=30)
    @with_user
    @with_cards(count=1)
    def test_transactions_concurrent_access(self, api, user, cards):
        """测试交易并发访问"""
        api.get("/api/v1/user/transactions/list").should.succeed()


@test_suite("交易业务逻辑测试")
class TransactionBusinessLogicTests:
    """交易业务逻辑测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_transaction_types_validation(self, api, user, cards):
        """测试交易类型验证"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 测试有效的交易类型
        valid_types = ["expense", "income", "transfer"]
        for trans_type in valid_types:
            api.post("/api/v1/user/transactions/create", data={
                "card_id": card['id'],
                "transaction_type": trans_type,
                "amount": 100.00,
                "description": f"{trans_type}测试"
            }).should.succeed()
        
        # 测试无效的交易类型
        api.post("/api/v1/user/transactions/create", data={
            "card_id": card['id'],
            "transaction_type": "invalid",
            "amount": 100.00
        }).should.fail(422)
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_transaction_points_calculation(self, api, user, cards):
        """测试交易积分计算"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建交易，应该自动计算积分
        response = api.post("/api/v1/user/transactions/create", data={
            "card_id": card['id'],
            "transaction_type": "expense",
            "amount": 1000.00,  # 1000元消费
            "description": "积分测试交易"
        }).should.succeed()
        
        # 验证积分计算（假设1元=1积分）
        transaction = response.data
        assert transaction.get("points_earned", 0) > 0, "应该获得积分"
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_monthly_transaction_summary(self, api, user, cards):
        """测试月度交易汇总"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建本月交易
        for i in range(5):
            api.post("/api/v1/user/transactions/create", data={
                "card_id": card['id'],
                "transaction_type": "expense",
                "amount": 200.00,
                "description": f"月度测试交易{i+1}"
            }).should.succeed()
        
        # 获取月度汇总
        api.get("/api/v1/user/transactions/list?summary=monthly").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_transaction_tagging(self, api, user, cards):
        """测试交易标签功能"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建带标签的交易
        api.post("/api/v1/user/transactions/create", data={
            "card_id": card['id'],
            "transaction_type": "expense",
            "amount": 150.00,
            "description": "标签测试交易",
            "tags": ["工作", "报销", "差旅"]
        }).should.succeed()
        
        # 按标签筛选
        api.get("/api/v1/user/transactions/list?tags=工作").should.succeed()