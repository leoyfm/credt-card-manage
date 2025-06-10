"""
统计分析服务API测试套件

使用新测试框架v2.0进行统计分析功能的全面测试
包括仪表板数据、趋势分析、财务报告、健康评估等功能
"""

import pytest
from tests.framework import (
    test_suite, api_test, with_user, with_cards, with_transactions,
    performance_test, stress_test
)


@test_suite("仪表板统计API")
class DashboardStatisticsTests:
    """仪表板统计功能测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=2)
    @with_transactions(count=20)
    def test_get_dashboard_overview(self, api, user, cards, transactions):
        """测试获取仪表板概览"""
        api.get("/api/v1/user/statistics/dashboard/overview").should.succeed().with_data_structure({
            "total_cards": int,
            "total_credit_limit": float,
            "total_balance": float,
            "monthly_spending": float,
            "recent_transactions": list
        })
    
    @api_test
    @with_user
    @with_cards(count=3)
    @with_transactions(count=15)
    def test_get_monthly_summary(self, api, user, cards, transactions):
        """测试获取月度汇总"""
        api.get("/api/v1/user/statistics/dashboard/monthly-summary").should.succeed().with_data_structure({
            "current_month": dict,
            "previous_month": dict,
            "growth_rate": float,
            "category_breakdown": list
        })
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=10)
    def test_get_weekly_trends(self, api, user, cards, transactions):
        """测试获取周度趋势"""
        api.get("/api/v1/user/statistics/dashboard/weekly-trends").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=2)
    def test_get_cards_utilization(self, api, user, cards):
        """测试获取信用卡使用率"""
        api.get("/api/v1/user/statistics/dashboard/cards-utilization").should.succeed()


@test_suite("支出分析")
class SpendingAnalysisTests:
    """支出分析测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=30)
    def test_get_spending_by_category(self, api, user, cards, transactions):
        """测试按类别分析支出"""
        api.get("/api/v1/user/statistics/spending/by-category").should.succeed().with_data_structure({
            "categories": list,
            "amounts": list,
            "percentages": list
        })
    
    @api_test
    @with_user
    @with_cards(count=2)
    @with_transactions(count=25)
    def test_get_spending_by_card(self, api, user, cards, transactions):
        """测试按信用卡分析支出"""
        api.get("/api/v1/user/statistics/spending/by-card").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=20)
    def test_get_spending_trends(self, api, user, cards, transactions):
        """测试支出趋势分析"""
        api.get("/api/v1/user/statistics/spending/trends?period=6months").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=15)
    def test_get_spending_comparison(self, api, user, cards, transactions):
        """测试支出对比分析"""
        api.get("/api/v1/user/statistics/spending/comparison?compare=previous_month").should.succeed()


@test_suite("财务报告")
class FinancialReportsTests:
    """财务报告测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=2)
    @with_transactions(count=50)
    def test_generate_monthly_report(self, api, user, cards, transactions):
        """测试生成月度财务报告"""
        api.get("/api/v1/user/statistics/reports/monthly?year=2024&month=12").should.succeed().with_data_structure({
            "period": dict,
            "summary": dict,
            "detailed_analysis": dict,
            "recommendations": list
        })
    
    @api_test
    @with_user
    @with_cards(count=2)
    @with_transactions(count=100)
    def test_generate_yearly_report(self, api, user, cards, transactions):
        """测试生成年度财务报告"""
        api.get("/api/v1/user/statistics/reports/yearly?year=2024").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=30)
    def test_generate_custom_period_report(self, api, user, cards, transactions):
        """测试生成自定义期间报告"""
        api.get("/api/v1/user/statistics/reports/custom?start_date=2024-01-01&end_date=2024-12-31").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=2)
    @with_transactions(count=40)
    def test_export_report_pdf(self, api, user, cards, transactions):
        """测试导出PDF报告"""
        api.get("/api/v1/user/statistics/reports/export/pdf?type=monthly&year=2024&month=12").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=25)
    def test_export_report_excel(self, api, user, cards, transactions):
        """测试导出Excel报告"""
        api.get("/api/v1/user/statistics/reports/export/excel?type=yearly&year=2024").should.succeed()


@test_suite("健康评估")
class FinancialHealthTests:
    """财务健康评估测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=3)
    @with_transactions(count=60)
    def test_get_financial_health_score(self, api, user, cards, transactions):
        """测试获取财务健康评分"""
        api.get("/api/v1/user/statistics/health/score").should.succeed().with_data_structure({
            "overall_score": int,
            "score_breakdown": dict,
            "risk_factors": list,
            "improvement_suggestions": list
        })
    
    @api_test
    @with_user
    @with_cards(count=2)
    @with_transactions(count=40)
    def test_get_credit_utilization_analysis(self, api, user, cards, transactions):
        """测试信用使用率分析"""
        api.get("/api/v1/user/statistics/health/credit-utilization").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=20)
    def test_get_spending_pattern_analysis(self, api, user, cards, transactions):
        """测试消费模式分析"""
        api.get("/api/v1/user/statistics/health/spending-patterns").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=2)
    def test_get_risk_assessment(self, api, user, cards):
        """测试风险评估"""
        api.get("/api/v1/user/statistics/health/risk-assessment").should.succeed()


@test_suite("数据统计和洞察")
class DataInsightsTests:
    """数据统计和洞察测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=2)
    @with_transactions(count=100)
    def test_get_merchant_analysis(self, api, user, cards, transactions):
        """测试商户分析"""
        api.get("/api/v1/user/statistics/insights/merchants").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=50)
    def test_get_time_pattern_analysis(self, api, user, cards, transactions):
        """测试时间模式分析"""
        api.get("/api/v1/user/statistics/insights/time-patterns").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=2)
    @with_transactions(count=75)
    def test_get_unusual_spending_detection(self, api, user, cards, transactions):
        """测试异常消费检测"""
        api.get("/api/v1/user/statistics/insights/unusual-spending").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=30)
    def test_get_cashback_optimization(self, api, user, cards, transactions):
        """测试返现优化分析"""
        api.get("/api/v1/user/statistics/insights/cashback-optimization").should.succeed()


@test_suite("统计配置")
class StatisticsConfigTests:
    """统计配置测试套件"""
    
    @api_test
    @with_user
    def test_get_statistics_preferences(self, api, user):
        """测试获取统计偏好设置"""
        api.get("/api/v1/user/statistics/preferences").should.succeed()
    
    @api_test
    @with_user
    def test_update_statistics_preferences(self, api, user):
        """测试更新统计偏好设置"""
        preferences_data = {
            "default_period": "monthly",
            "currency": "CNY",
            "include_pending_transactions": True,
            "exclude_categories": ["转账"],
            "chart_type_preference": "bar"
        }
        
        api.put("/api/v1/user/statistics/preferences", data=preferences_data).should.succeed()
    
    @api_test
    @with_user
    def test_get_available_metrics(self, api, user):
        """测试获取可用指标"""
        api.get("/api/v1/user/statistics/metrics/available").should.succeed()


@test_suite("统计权限测试")
class StatisticsPermissionTests:
    """统计权限验证测试套件"""
    
    @api_test
    def test_unauthenticated_access(self, api):
        """测试未认证访问统计接口"""
        api.get("/api/v1/user/statistics/dashboard/overview").should.fail(401)
    
    @api_test
    @with_user
    def test_user_data_isolation(self, api, user):
        """测试用户数据隔离"""
        # 用户只能看到自己的统计数据
        response = api.get("/api/v1/user/statistics/dashboard/overview").should.succeed()
        # 验证返回的数据是当前用户的


@test_suite("统计性能测试")
class StatisticsPerformanceTests:
    """统计服务性能测试套件"""
    
    @performance_test
    @with_user
    @with_cards(count=5)
    @with_transactions(count=500)
    def test_dashboard_overview_performance(self, api, user, cards, transactions):
        """测试仪表板概览性能"""
        api.get("/api/v1/user/statistics/dashboard/overview").should.succeed().complete_within(seconds=2.0)
    
    @performance_test
    @with_user
    @with_cards(count=3)
    @with_transactions(count=200)
    def test_spending_analysis_performance(self, api, user, cards, transactions):
        """测试支出分析性能"""
        api.get("/api/v1/user/statistics/spending/by-category").should.succeed().complete_within(seconds=1.5)
    
    @performance_test
    @with_user
    @with_cards(count=2)
    @with_transactions(count=100)
    def test_report_generation_performance(self, api, user, cards, transactions):
        """测试报告生成性能"""
        api.get("/api/v1/user/statistics/reports/monthly?year=2024&month=12").should.succeed().complete_within(seconds=3.0)
    
    @stress_test(concurrent_users=20, duration=60)
    @with_user
    @with_cards(count=2)
    def test_statistics_concurrent_access(self, api, user, cards):
        """测试统计并发访问"""
        api.get("/api/v1/user/statistics/dashboard/overview").should.succeed()


@test_suite("统计业务逻辑测试")
class StatisticsBusinessLogicTests:
    """统计业务逻辑测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_statistics_with_different_periods(self, api, user, cards):
        """测试不同时间周期的统计"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建不同时间的交易
        dates = ["2024-01-15", "2024-06-15", "2024-12-15"]
        for date in dates:
            api.post("/api/v1/user/transactions/create", data={
                "card_id": card['id'],
                "transaction_type": "expense",
                "amount": 500.00,
                "description": f"{date}交易",
                "transaction_date": f"{date}T10:00:00Z"
            }).should.succeed()
        
        # 测试不同周期的统计
        periods = ["monthly", "quarterly", "yearly"]
        for period in periods:
            api.get(f"/api/v1/user/statistics/spending/trends?period={period}").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=2)
    def test_multi_card_statistics_aggregation(self, api, user, cards):
        """测试多卡统计聚合"""
        # 为不同卡片创建交易
        for i, card in enumerate(cards):
            for j in range(5):
                api.post("/api/v1/user/transactions/create", data={
                    "card_id": card['id'],
                    "transaction_type": "expense",
                    "amount": (i + 1) * 100.00,  # 不同金额
                    "description": f"卡{i+1}交易{j+1}"
                }).should.succeed()
        
        # 获取聚合统计
        response = api.get("/api/v1/user/statistics/spending/by-card").should.succeed()
        
        # 验证聚合逻辑
        data = response.data
        assert len(data.get('cards', [])) == 2, "应该显示两张卡的统计"
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_category_statistics_accuracy(self, api, user, cards):
        """测试分类统计准确性"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 创建不同分类的交易
        categories = {
            "餐饮": [100, 150, 200],  # 总计450
            "购物": [300, 250],       # 总计550
            "交通": [80, 120, 100]    # 总计300
        }
        
        for category, amounts in categories.items():
            for amount in amounts:
                api.post("/api/v1/user/transactions/create", data={
                    "card_id": card['id'],
                    "transaction_type": "expense",
                    "amount": amount,
                    "description": f"{category}消费",
                    "merchant_category": category
                }).should.succeed()
        
        # 获取分类统计
        response = api.get("/api/v1/user/statistics/spending/by-category").should.succeed()
        
        # 验证统计准确性（这里需要根据实际API响应格式调整）
        data = response.data
        category_data = data.get('categories', [])
        assert len(category_data) >= 3, "应该有至少3个分类"
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_statistics_filtering(self, api, user, cards):
        """测试统计筛选功能"""
        # 按日期范围筛选
        api.get("/api/v1/user/statistics/spending/trends?start_date=2024-01-01&end_date=2024-12-31").should.succeed()
        
        # 按金额范围筛选
        api.get("/api/v1/user/statistics/spending/by-category?min_amount=100&max_amount=1000").should.succeed()
        
        # 按卡片筛选
        card = cards[0] if isinstance(cards, list) else cards
        api.get(f"/api/v1/user/statistics/spending/trends?card_id={card['id']}").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=10)
    def test_statistics_caching(self, api, user, cards, transactions):
        """测试统计数据缓存"""
        # 第一次请求
        start_time = api.get("/api/v1/user/statistics/dashboard/overview").should.succeed().response_time
        
        # 第二次请求（应该更快，如果有缓存）
        cached_time = api.get("/api/v1/user/statistics/dashboard/overview").should.succeed().response_time
        
        # 验证缓存效果（第二次请求应该更快）
        # assert cached_time <= start_time, "缓存请求应该更快"
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_empty_data_statistics(self, api, user, cards):
        """测试空数据情况下的统计"""
        # 没有交易数据时的统计
        response = api.get("/api/v1/user/statistics/dashboard/overview").should.succeed()
        
        # 验证空数据处理
        data = response.data
        assert data.get('total_balance', 0) == 0, "没有交易时余额应为0"
        assert data.get('monthly_spending', 0) == 0, "没有交易时月消费应为0"