"""
统计服务单元测试
测试统计服务的所有功能，包括仪表板数据、趋势分析、财务报告等
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta, date
from decimal import Decimal
from uuid import uuid4, UUID
from typing import Dict, List, Any
import calendar

from app.services.statistics_service import StatisticsService
from app.models.database.card import CreditCard
from app.models.database.transaction import Transaction, TransactionCategory
from app.models.database.annual_fee import AnnualFeeRecord
from app.models.database.reminder import ReminderSetting, ReminderRecord
from app.core.exceptions.custom import ResourceNotFoundError, ValidationError, BusinessRuleError


class TestStatisticsService:
    """统计服务基础测试类"""
    
    @pytest.fixture
    def mock_db(self):
        """模拟数据库会话"""
        return Mock()
    
    @pytest.fixture
    def statistics_service(self, mock_db):
        """创建统计服务实例"""
        return StatisticsService(mock_db)
    
    @pytest.fixture
    def sample_user_id(self):
        """示例用户ID"""
        return uuid4()
    
    @pytest.fixture
    def sample_card_data(self, sample_user_id):
        """示例信用卡数据"""
        return [
            Mock(
                id=uuid4(),
                user_id=sample_user_id,
                card_name="招商银行信用卡",
                credit_limit=Decimal("50000.00"),
                used_limit=Decimal("15000.00"),
                status="active"
            ),
            Mock(
                id=uuid4(),
                user_id=sample_user_id,
                card_name="建设银行信用卡",
                credit_limit=Decimal("30000.00"),
                used_limit=Decimal("8000.00"),
                status="active"
            )
        ]
    
    @pytest.fixture
    def sample_transaction_data(self, sample_user_id):
        """示例交易数据"""
        base_date = datetime.now() - timedelta(days=15)
        return [
            Mock(
                id=uuid4(),
                user_id=sample_user_id,
                transaction_type="expense",
                amount=Decimal("1500.00"),
                points_earned=150,
                cashback_earned=Decimal("15.00"),
                transaction_date=base_date,
                category=Mock(name="餐饮")
            ),
            Mock(
                id=uuid4(),
                user_id=sample_user_id,
                transaction_type="expense",
                amount=Decimal("800.00"),
                points_earned=80,
                cashback_earned=Decimal("8.00"),
                transaction_date=base_date + timedelta(days=5),
                category=Mock(name="购物")
            ),
            Mock(
                id=uuid4(),
                user_id=sample_user_id,
                transaction_type="income",
                amount=Decimal("5000.00"),
                points_earned=0,
                cashback_earned=Decimal("0.00"),
                transaction_date=base_date + timedelta(days=10),
                category=Mock(name="收入")
            )
        ]


class TestDashboardOverview(TestStatisticsService):
    """仪表板概览测试"""
    
    def test_get_dashboard_overview_success(self, statistics_service, mock_db, sample_user_id):
        """测试获取仪表板概览成功"""
        # 模拟各个子方法的返回值
        with patch.object(statistics_service, '_get_cards_overview') as mock_cards, \
             patch.object(statistics_service, '_get_transactions_overview') as mock_transactions, \
             patch.object(statistics_service, '_get_annual_fee_overview') as mock_annual_fee, \
             patch.object(statistics_service, '_get_reminders_overview') as mock_reminders, \
             patch.object(statistics_service, '_calculate_financial_health_score') as mock_health:
            
            # 设置返回值
            mock_cards.return_value = {
                'total_cards': 2,
                'active_cards': 2,
                'total_credit_limit': 80000.0,
                'utilization_rate': 28.75
            }
            mock_transactions.return_value = {
                'total_transactions': 15,
                'total_expense': 2300.0,
                'total_income': 5000.0
            }
            mock_annual_fee.return_value = {
                'total_fees': 2,
                'total_actual_fee': 600.0,
                'waiver_rate': 50.0
            }
            mock_reminders.return_value = {
                'active_settings': 3,
                'pending_reminders': 1
            }
            mock_health.return_value = {
                'total_score': 85,
                'grade': 'A',
                'level': 'very_good'
            }
            
            # 执行测试
            result = statistics_service.get_dashboard_overview(sample_user_id)
            
            # 验证结果
            assert 'cards' in result
            assert 'transactions' in result
            assert 'annual_fees' in result
            assert 'reminders' in result
            assert 'health_score' in result
            assert 'last_updated' in result
            
            assert result['cards']['total_cards'] == 2
            assert result['transactions']['total_expense'] == 2300.0
            assert result['health_score']['grade'] == 'A'
            
            # 验证方法调用
            mock_cards.assert_called_once_with(sample_user_id)
            mock_transactions.assert_called_once_with(sample_user_id)
            mock_annual_fee.assert_called_once_with(sample_user_id)
            mock_reminders.assert_called_once_with(sample_user_id)
            mock_health.assert_called_once_with(sample_user_id)
    
    def test_get_cards_overview_success(self, statistics_service, mock_db, sample_user_id):
        """测试获取信用卡概览成功"""
        # 模拟查询结果
        mock_result = Mock()
        mock_result.total_cards = 2
        mock_result.active_cards = 2
        mock_result.total_credit_limit = Decimal("80000.00")
        mock_result.total_used_limit = Decimal("23000.00")
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_result
        mock_db.query.return_value = mock_query
        
        # 执行测试
        result = statistics_service._get_cards_overview(sample_user_id)
        
        # 验证结果
        assert result['total_cards'] == 2
        assert result['active_cards'] == 2
        assert result['total_credit_limit'] == 80000.0
        assert result['total_used_limit'] == 23000.0
        assert result['available_limit'] == 57000.0
        assert result['utilization_rate'] == 28.75
    
    def test_get_transactions_overview_success(self, statistics_service, mock_db, sample_user_id):
        """测试获取交易概览成功"""
        # 模拟查询结果
        mock_result = Mock()
        mock_result.total_transactions = 15
        mock_result.total_expense = Decimal("2300.00")
        mock_result.total_income = Decimal("5000.00")
        mock_result.total_points = 230
        mock_result.total_cashback = Decimal("23.00")
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_result
        mock_db.query.return_value = mock_query
        
        # 执行测试
        result = statistics_service._get_transactions_overview(sample_user_id)
        
        # 验证结果
        assert result['total_transactions'] == 15
        assert result['total_expense'] == 2300.0
        assert result['total_income'] == 5000.0
        assert result['net_amount'] == 2700.0
        assert result['total_points'] == 230
        assert result['total_cashback'] == 23.0
        assert result['avg_daily_expense'] == round(2300.0 / 30, 2)


class TestMonthlyTrends(TestStatisticsService):
    """月度趋势测试"""
    
    def test_get_monthly_trends_success(self, statistics_service, mock_db, sample_user_id):
        """测试获取月度趋势成功"""
        # 模拟查询结果
        mock_data = [
            Mock(year=2024, month=11, transaction_type='expense', count=10, 
                 total_amount=Decimal("1500.00"), total_points=150, total_cashback=Decimal("15.00")),
            Mock(year=2024, month=11, transaction_type='income', count=2, 
                 total_amount=Decimal("3000.00"), total_points=0, total_cashback=Decimal("0.00")),
            Mock(year=2024, month=12, transaction_type='expense', count=8, 
                 total_amount=Decimal("1200.00"), total_points=120, total_cashback=Decimal("12.00"))
        ]
        
        mock_query = Mock()
        mock_query.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = mock_data
        mock_db.query.return_value = mock_query
        
        with patch.object(statistics_service, '_analyze_trends') as mock_analyze:
            mock_analyze.return_value = {
                'expense_trend': 'decreasing',
                'income_trend': 'stable',
                'growth_rate': -20.0,
                'volatility': 'low'
            }
            
            # 执行测试
            result = statistics_service.get_monthly_trends(sample_user_id, months=6)
            
            # 验证结果
            assert result['analysis_period'] == "6个月"
            assert 'monthly_trends' in result
            assert 'trend_analysis' in result
            assert result['trend_analysis']['expense_trend'] == 'decreasing'
            
            # 验证月度数据结构
            trends = result['monthly_trends']
            assert len(trends) >= 1
            
            # 检查第一个月度数据
            first_trend = trends[0]
            assert 'year' in first_trend
            assert 'month' in first_trend
            assert 'month_name' in first_trend
            assert 'expense_count' in first_trend
            assert 'expense_amount' in first_trend
            assert 'income_count' in first_trend
            assert 'income_amount' in first_trend
            assert 'net_amount' in first_trend
    
    def test_get_monthly_trends_with_custom_months(self, statistics_service, mock_db, sample_user_id):
        """测试自定义月数的月度趋势"""
        mock_query = Mock()
        mock_query.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = []
        mock_db.query.return_value = mock_query
        
        with patch.object(statistics_service, '_analyze_trends') as mock_analyze:
            mock_analyze.return_value = {'expense_trend': 'stable'}
            
            # 执行测试
            result = statistics_service.get_monthly_trends(sample_user_id, months=3)
            
            # 验证结果
            assert result['analysis_period'] == "3个月"
            assert result['total_months'] == 0  # 无数据时


class TestSpendingAnalysis(TestStatisticsService):
    """消费分析测试"""
    
    def test_get_spending_analysis_success(self, statistics_service, mock_db, sample_user_id):
        """测试获取消费分析成功"""
        # 模拟分类统计查询
        mock_category_stats = [
            Mock(category_name="餐饮", transaction_count=5, total_amount=800.0, average_amount=160.0),
            Mock(category_name="购物", transaction_count=3, total_amount=600.0, average_amount=200.0)
        ]
        
        # 模拟信用卡统计查询
        mock_card_stats = [
            Mock(card_name="招商银行信用卡", transaction_count=4, total_amount=900.0, 
                 total_points=90, total_cashback=9.0),
            Mock(card_name="建设银行信用卡", transaction_count=4, total_amount=500.0, 
                 total_points=50, total_cashback=5.0)
        ]
        
        # 模拟每日统计查询
        mock_daily_stats = [
            Mock(date=date.today() - timedelta(days=2), transaction_count=2, total_amount=300.0),
            Mock(date=date.today() - timedelta(days=1), transaction_count=3, total_amount=450.0)
        ]
        
        # 设置查询返回值
        call_count = 0
        def mock_query_side_effect(*args):
            nonlocal call_count
            call_count += 1
            mock_query = Mock()
            if call_count == 1:  # 第一次调用：分类统计
                mock_query.filter.return_value.group_by.return_value.all.return_value = mock_category_stats
            elif call_count == 2:  # 第二次调用：信用卡统计
                mock_query.join.return_value.filter.return_value.group_by.return_value.all.return_value = mock_card_stats
            else:  # 第三次调用：每日统计
                mock_query.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = mock_daily_stats
            return mock_query
        
        mock_db.query.side_effect = mock_query_side_effect
        
        # 执行测试
        result = statistics_service.get_spending_analysis(sample_user_id)
        
        # 验证结果
        assert 'period_start' in result
        assert 'period_end' in result
        assert 'total_expense' in result
        assert 'category_distribution' in result
        assert 'card_distribution' in result
        assert 'daily_trends' in result
        assert 'top_categories' in result
        assert 'top_cards' in result
        
        # 验证分类分布
        categories = result['category_distribution']
        assert len(categories) == 2
        assert categories[0]['category_name'] in ["餐饮", "购物"]
        assert 'percentage' in categories[0]
        
        # 验证信用卡分布
        cards = result['card_distribution']
        assert len(cards) == 2
        assert 'percentage' in cards[0]
    
    def test_get_spending_analysis_with_date_range(self, statistics_service, mock_db, sample_user_id):
        """测试指定日期范围的消费分析"""
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        # 模拟空查询结果
        mock_query = Mock()
        mock_query.filter.return_value.group_by.return_value.all.return_value = []
        mock_query.join.return_value.filter.return_value.group_by.return_value.all.return_value = []
        mock_query.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = []
        mock_db.query.return_value = mock_query
        
        # 执行测试
        result = statistics_service.get_spending_analysis(sample_user_id, start_date, end_date)
        
        # 验证结果
        assert result['period_start'] == start_date
        assert result['period_end'] == end_date
        assert result['total_expense'] == 0.0
        assert result['category_distribution'] == []
        assert result['card_distribution'] == []


class TestFinancialReport(TestStatisticsService):
    """财务报告测试"""
    
    def test_get_financial_report_success(self, statistics_service, mock_db, sample_user_id):
        """测试获取财务报告成功"""
        current_year = datetime.now().year
        
        # 模拟总体统计查询
        mock_total_stats = Mock()
        mock_total_stats.total_transactions = 50
        mock_total_stats.total_expense = Decimal("15000.00")
        mock_total_stats.total_income = Decimal("20000.00")
        mock_total_stats.total_points = 1500
        mock_total_stats.total_cashback = Decimal("150.00")
        
        # 模拟月度统计查询
        mock_monthly_stats = [
            Mock(month=1, expense=Decimal("1200.00"), income=Decimal("1800.00"), transaction_count=8),
            Mock(month=2, expense=Decimal("1100.00"), income=Decimal("1700.00"), transaction_count=7)
        ]
        
        # 模拟年费统计查询
        mock_annual_fee_stats = Mock()
        mock_annual_fee_stats.total_fees = 2
        mock_annual_fee_stats.total_base_fee = Decimal("600.00")
        mock_annual_fee_stats.total_actual_fee = Decimal("300.00")
        mock_annual_fee_stats.total_waived = Decimal("300.00")
        
        # 模拟信用卡利用率查询
        mock_card_utilization = [
            Mock(card_name="招商银行信用卡", credit_limit=Decimal("50000.00"), 
                 used_limit=Decimal("15000.00"), utilization_rate=30.0),
            Mock(card_name="建设银行信用卡", credit_limit=Decimal("30000.00"), 
                 used_limit=Decimal("9000.00"), utilization_rate=30.0)
        ]
        
        # 设置查询返回值
        call_count = 0
        def mock_query_side_effect(*args):
            nonlocal call_count
            call_count += 1
            mock_query = Mock()
            if call_count == 1:  # 第一次调用：总体统计
                mock_query.filter.return_value.first.return_value = mock_total_stats
            elif call_count == 2:  # 第二次调用：月度统计
                mock_query.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = mock_monthly_stats
            elif call_count == 3:  # 第三次调用：年费统计
                mock_query.join.return_value.join.return_value.filter.return_value.first.return_value = mock_annual_fee_stats
            else:  # 第四次调用：信用卡利用率
                mock_query.filter.return_value.all.return_value = mock_card_utilization
            return mock_query
        
        mock_db.query.side_effect = mock_query_side_effect
        
        # 执行测试
        result = statistics_service.get_financial_report(sample_user_id, current_year)
        
        # 验证结果
        assert result['year'] == current_year
        assert 'summary' in result
        assert 'monthly_data' in result
        assert 'annual_fees' in result
        assert 'card_utilization' in result
        
        # 验证摘要数据
        summary = result['summary']
        assert summary['total_transactions'] == 50
        assert summary['total_expense'] == 15000.0
        assert summary['total_income'] == 20000.0
        assert summary['net_income'] == 5000.0
        assert summary['savings_rate'] == 25.0
        
        # 验证月度数据
        monthly_data = result['monthly_data']
        assert len(monthly_data) == 12  # 12个月
        assert monthly_data[0]['month'] == 1
        assert monthly_data[0]['month_name'] == 'January'
        
        # 验证年费数据
        annual_fees = result['annual_fees']
        assert annual_fees['total_fees'] == 2
        assert annual_fees['waiver_rate'] == 50.0
        
        # 验证信用卡利用率
        utilization = result['card_utilization']
        assert len(utilization) == 2
        assert utilization[0]['utilization_rate'] == 30.0
    
    def test_get_financial_report_default_year(self, statistics_service, mock_db, sample_user_id):
        """测试默认年份的财务报告"""
        # 模拟空查询结果
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = Mock(
            total_transactions=0, total_expense=None, total_income=None, 
            total_points=None, total_cashback=None
        )
        mock_query.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = []
        mock_query.join.return_value.join.return_value.filter.return_value.first.return_value = None
        mock_query.filter.return_value.all.return_value = []
        mock_db.query.return_value = mock_query
        
        # 执行测试（不指定年份）
        result = statistics_service.get_financial_report(sample_user_id)
        
        # 验证结果
        assert result['year'] == datetime.now().year
        assert result['summary']['total_expense'] == 0.0
        assert result['summary']['total_income'] == 0.0


class TestHealthScore(TestStatisticsService):
    """财务健康评分测试"""
    
    def test_calculate_financial_health_score_excellent(self, statistics_service, mock_db, sample_user_id):
        """测试优秀的财务健康评分"""
        # 模拟信用卡数据（低利用率）
        mock_cards = [
            Mock(credit_limit=Decimal("50000.00"), used_limit=Decimal("10000.00")),  # 20%利用率
            Mock(credit_limit=Decimal("30000.00"), used_limit=Decimal("6000.00"))    # 20%利用率
        ]
        
        # 模拟交易数据（高活跃度）
        mock_transaction_count = 25
        
        # 模拟年费记录（高减免率）
        mock_fee_records = [
            Mock(base_fee=Decimal("300.00"), waiver_amount=Decimal("300.00")),  # 100%减免
            Mock(base_fee=Decimal("200.00"), waiver_amount=Decimal("200.00"))   # 100%减免
        ]
        
        # 模拟提醒设置（多个启用）
        mock_active_reminders = 4
        
        # 模拟完整信息的信用卡
        mock_complete_cards = 2
        mock_total_cards = 2
        
        # 设置查询返回值
        call_count = 0
        def mock_query_side_effect(*args):
            nonlocal call_count
            call_count += 1
            mock_query = Mock()
            if call_count == 1:  # 第一次调用：信用卡数据
                mock_query.filter.return_value.all.return_value = mock_cards
            elif call_count == 2:  # 第二次调用：交易数量
                mock_query.filter.return_value.count.return_value = mock_transaction_count
            elif call_count == 3:  # 第三次调用：年费记录
                mock_query.join.return_value.join.return_value.filter.return_value.all.return_value = mock_fee_records
            elif call_count == 4:  # 第四次调用：提醒设置
                mock_query.filter.return_value.count.return_value = mock_active_reminders
            elif call_count == 5:  # 第五次调用：完整信息卡片
                mock_query.filter.return_value.count.return_value = mock_complete_cards
            else:  # 第六次调用：总卡片数
                mock_query.filter.return_value.count.return_value = mock_total_cards
            return mock_query
        
        mock_db.query.side_effect = mock_query_side_effect
        
        with patch.object(statistics_service, '_get_health_recommendations') as mock_recommendations:
            mock_recommendations.return_value = ["您的财务管理状况良好，继续保持！"]
            
            # 执行测试
            result = statistics_service._calculate_financial_health_score(sample_user_id)
            
            # 验证结果
            assert result['total_score'] >= 90  # 优秀评分
            assert result['grade'] in ['A+', 'A']
            assert result['level'] in ['excellent', 'very_good']
            assert len(result['factors']) == 5
            assert 'recommendations' in result
            
            # 验证各个因子
            factors = {f['factor']: f for f in result['factors']}
            assert 'credit_utilization' in factors
            assert 'transaction_activity' in factors
            assert 'annual_fee_management' in factors
            assert 'reminder_usage' in factors
            assert 'data_completeness' in factors
    
    def test_calculate_financial_health_score_poor(self, statistics_service, mock_db, sample_user_id):
        """测试较差的财务健康评分"""
        # 模拟信用卡数据（高利用率）
        mock_cards = [
            Mock(credit_limit=Decimal("50000.00"), used_limit=Decimal("45000.00")),  # 90%利用率
        ]
        
        # 模拟交易数据（低活跃度）
        mock_transaction_count = 2
        
        # 模拟年费记录（低减免率）
        mock_fee_records = [
            Mock(base_fee=Decimal("300.00"), waiver_amount=Decimal("0.00")),  # 0%减免
        ]
        
        # 模拟提醒设置（无启用）
        mock_active_reminders = 0
        
        # 模拟不完整信息的信用卡
        mock_complete_cards = 0
        mock_total_cards = 1
        
        # 设置查询返回值
        call_count = 0
        def mock_query_side_effect(*args):
            nonlocal call_count
            call_count += 1
            mock_query = Mock()
            if call_count == 1:  # 第一次调用：信用卡数据
                mock_query.filter.return_value.all.return_value = mock_cards
            elif call_count == 2:  # 第二次调用：交易数量
                mock_query.filter.return_value.count.return_value = mock_transaction_count
            elif call_count == 3:  # 第三次调用：年费记录
                mock_query.join.return_value.join.return_value.filter.return_value.all.return_value = mock_fee_records
            elif call_count == 4:  # 第四次调用：提醒设置
                mock_query.filter.return_value.count.return_value = mock_active_reminders
            elif call_count == 5:  # 第五次调用：完整信息卡片
                mock_query.filter.return_value.count.return_value = mock_complete_cards
            else:  # 第六次调用：总卡片数
                mock_query.filter.return_value.count.return_value = mock_total_cards
            return mock_query
        
        mock_db.query.side_effect = mock_query_side_effect
        
        with patch.object(statistics_service, '_get_health_recommendations') as mock_recommendations:
            mock_recommendations.return_value = [
                "建议降低信用卡使用率至30%以下",
                "建议增加信用卡使用频率",
                "建议设置还款提醒和年费提醒"
            ]
            
            # 执行测试
            result = statistics_service._calculate_financial_health_score(sample_user_id)
            
            # 验证结果
            assert result['total_score'] < 60  # 较差评分
            assert result['grade'] in ['C+', 'C']
            assert result['level'] in ['poor', 'very_poor']
            assert len(result['recommendations']) > 1


class TestTrendAnalysis(TestStatisticsService):
    """趋势分析测试"""
    
    def test_analyze_trends_increasing(self, statistics_service):
        """测试上升趋势分析"""
        trends_list = [
            {'expense_amount': 1000.0, 'income_amount': 2000.0},
            {'expense_amount': 1200.0, 'income_amount': 2200.0},
            {'expense_amount': 1400.0, 'income_amount': 2400.0}
        ]
        
        result = statistics_service._analyze_trends(trends_list)
        
        assert result['expense_trend'] == 'increasing'
        assert result['growth_rate'] > 0
        assert result['volatility'] in ['low', 'medium', 'high']
    
    def test_analyze_trends_decreasing(self, statistics_service):
        """测试下降趋势分析"""
        trends_list = [
            {'expense_amount': 1400.0, 'income_amount': 2400.0},
            {'expense_amount': 1200.0, 'income_amount': 2200.0},
            {'expense_amount': 1000.0, 'income_amount': 2000.0}
        ]
        
        result = statistics_service._analyze_trends(trends_list)
        
        assert result['expense_trend'] == 'decreasing'
        assert result['growth_rate'] < 0
        assert result['volatility'] in ['low', 'medium', 'high']
    
    def test_analyze_trends_stable(self, statistics_service):
        """测试稳定趋势分析"""
        trends_list = [
            {'expense_amount': 1000.0, 'income_amount': 2000.0},
            {'expense_amount': 1050.0, 'income_amount': 2050.0}
        ]
        
        result = statistics_service._analyze_trends(trends_list)
        
        assert result['expense_trend'] == 'stable'
        assert result['income_trend'] == 'stable'
        assert result['growth_rate'] == 5.0
        assert result['volatility'] in ['low', 'medium', 'high']
    
    def test_analyze_trends_insufficient_data(self, statistics_service):
        """测试数据不足的趋势分析"""
        trends_list = [
            {'expense_amount': 1000.0, 'income_amount': 2000.0}
        ]
        
        result = statistics_service._analyze_trends(trends_list)
        
        assert result['expense_trend'] == 'stable'
        assert result['income_trend'] == 'stable'
        assert result['growth_rate'] == 0.0
        assert result['volatility'] == 'low'


class TestHealthRecommendations(TestStatisticsService):
    """健康建议测试"""
    
    def test_get_health_recommendations_poor_factors(self, statistics_service):
        """测试较差因子的健康建议"""
        factors = [
            {'factor': 'credit_utilization', 'status': 'poor'},
            {'factor': 'transaction_activity', 'status': 'poor'},
            {'factor': 'annual_fee_management', 'status': 'fair'},
            {'factor': 'reminder_usage', 'status': 'poor'},
            {'factor': 'data_completeness', 'status': 'poor'}
        ]
        
        result = statistics_service._get_health_recommendations(factors)
        
        assert len(result) >= 4  # 应该有多个建议
        assert any("信用卡使用率" in rec for rec in result)
        assert any("使用频率" in rec for rec in result)
        assert any("提醒" in rec for rec in result)
        assert any("信息" in rec for rec in result)
    
    def test_get_health_recommendations_good_factors(self, statistics_service):
        """测试良好因子的健康建议"""
        factors = [
            {'factor': 'credit_utilization', 'status': 'excellent'},
            {'factor': 'transaction_activity', 'status': 'good'},
            {'factor': 'annual_fee_management', 'status': 'excellent'},
            {'factor': 'reminder_usage', 'status': 'good'},
            {'factor': 'data_completeness', 'status': 'excellent'}
        ]
        
        result = statistics_service._get_health_recommendations(factors)
        
        assert len(result) == 1
        assert "财务管理状况良好" in result[0]


class TestErrorHandling(TestStatisticsService):
    """错误处理测试"""
    
    def test_dashboard_overview_with_db_error(self, statistics_service, mock_db, sample_user_id):
        """测试数据库错误时的仪表板概览"""
        # 模拟数据库错误
        mock_db.query.side_effect = Exception("数据库连接错误")
        
        # 验证异常抛出
        with pytest.raises(Exception) as exc_info:
            statistics_service.get_dashboard_overview(sample_user_id)
        
        assert "数据库连接错误" in str(exc_info.value)
    
    def test_monthly_trends_with_invalid_months(self, statistics_service, mock_db, sample_user_id):
        """测试无效月数参数的月度趋势"""
        mock_query = Mock()
        mock_query.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = []
        mock_db.query.return_value = mock_query
        
        with patch.object(statistics_service, '_analyze_trends') as mock_analyze:
            mock_analyze.return_value = {'expense_trend': 'stable'}
            
            # 测试负数月份
            result = statistics_service.get_monthly_trends(sample_user_id, months=-1)
            assert result['analysis_period'] == "-1个月"
            
            # 测试零月份
            result = statistics_service.get_monthly_trends(sample_user_id, months=0)
            assert result['analysis_period'] == "0个月"


class TestEdgeCases(TestStatisticsService):
    """边界情况测试"""
    
    def test_empty_data_scenarios(self, statistics_service, mock_db, sample_user_id):
        """测试空数据场景"""
        # 模拟空查询结果
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = Mock(
            total_cards=0, active_cards=0, total_credit_limit=None, total_used_limit=None
        )
        mock_query.filter.return_value.all.return_value = []
        mock_query.filter.return_value.count.return_value = 0
        mock_db.query.return_value = mock_query
        
        # 测试信用卡概览
        result = statistics_service._get_cards_overview(sample_user_id)
        assert result['total_cards'] == 0
        assert result['utilization_rate'] == 0
        
        # 测试交易概览
        mock_query.filter.return_value.first.return_value = Mock(
            total_transactions=0, total_expense=None, total_income=None,
            total_points=None, total_cashback=None
        )
        result = statistics_service._get_transactions_overview(sample_user_id)
        assert result['total_transactions'] == 0
        assert result['total_expense'] == 0.0
    
    def test_zero_division_scenarios(self, statistics_service, mock_db, sample_user_id):
        """测试零除法场景"""
        # 模拟零信用额度的查询结果
        mock_result = Mock()
        mock_result.total_cards = 1
        mock_result.active_cards = 1
        mock_result.total_credit_limit = Decimal("0.00")
        mock_result.total_used_limit = Decimal("0.00")
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_result
        mock_db.query.return_value = mock_query
        
        # 执行测试，应该不会抛出零除法异常
        result = statistics_service._get_cards_overview(sample_user_id)
        assert result['utilization_rate'] == 0
    
    def test_large_numbers_handling(self, statistics_service, mock_db, sample_user_id):
        """测试大数值处理"""
        # 模拟大额度信用卡
        mock_result = Mock()
        mock_result.total_cards = 1
        mock_result.active_cards = 1
        mock_result.total_credit_limit = Decimal("999999999.99")
        mock_result.total_used_limit = Decimal("500000000.00")
        
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = mock_result
        mock_db.query.return_value = mock_query
        
        # 执行测试
        result = statistics_service._get_cards_overview(sample_user_id)
        
        # 验证大数值正确处理
        assert result['total_credit_limit'] == 999999999.99
        assert result['utilization_rate'] == 50.0  # 500M/1000M = 50%


class TestPerformance(TestStatisticsService):
    """性能测试"""
    
    def test_dashboard_overview_performance(self, statistics_service, mock_db, sample_user_id):
        """测试仪表板概览性能"""
        import time
        
        # 模拟快速查询
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = Mock(
            total_cards=2, active_cards=2, total_credit_limit=Decimal("80000.00"), total_used_limit=Decimal("20000.00")
        )
        mock_db.query.return_value = mock_query
        
        with patch.object(statistics_service, '_get_transactions_overview') as mock_trans, \
             patch.object(statistics_service, '_get_annual_fee_overview') as mock_fee, \
             patch.object(statistics_service, '_get_reminders_overview') as mock_remind, \
             patch.object(statistics_service, '_calculate_financial_health_score') as mock_health:
            
            mock_trans.return_value = {'total_transactions': 10}
            mock_fee.return_value = {'total_fees': 1}
            mock_remind.return_value = {'active_settings': 2}
            mock_health.return_value = {'total_score': 80}
            
            # 测量执行时间
            start_time = time.time()
            result = statistics_service.get_dashboard_overview(sample_user_id)
            end_time = time.time()
            
            # 验证性能（应该在合理时间内完成）
            execution_time = end_time - start_time
            assert execution_time < 1.0  # 应该在1秒内完成
            assert 'cards' in result
    
    def test_monthly_trends_large_dataset(self, statistics_service, mock_db, sample_user_id):
        """测试大数据集的月度趋势性能"""
        # 模拟大量月度数据
        mock_data = []
        for year in range(2020, 2025):
            for month in range(1, 13):
                mock_data.append(
                    Mock(year=year, month=month, transaction_type='expense', 
                         count=50, total_amount=Decimal("5000.00"), 
                         total_points=500, total_cashback=Decimal("50.00"))
                )
        
        mock_query = Mock()
        mock_query.filter.return_value.group_by.return_value.order_by.return_value.all.return_value = mock_data
        mock_db.query.return_value = mock_query
        
        with patch.object(statistics_service, '_analyze_trends') as mock_analyze:
            mock_analyze.return_value = {'expense_trend': 'stable'}
            
            # 执行测试
            import time
            start_time = time.time()
            result = statistics_service.get_monthly_trends(sample_user_id, months=60)
            end_time = time.time()
            
            # 验证性能和结果
            execution_time = end_time - start_time
            assert execution_time < 2.0  # 应该在2秒内完成
            assert len(result['monthly_trends']) > 0 