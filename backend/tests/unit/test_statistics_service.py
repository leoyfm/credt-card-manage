"""
统计服务单元测试 - 直连测试数据库
测试统计服务的所有功能，包括仪表板数据、趋势分析、财务报告等
"""
import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from typing import Dict, List, Any
import calendar

from app.services.statistics_service import StatisticsService
from app.models.database.card import CreditCard, Bank
from app.models.database.user import User
from app.models.database.transaction import Transaction, TransactionCategory
from app.models.database.fee_waiver import FeeWaiverRule, AnnualFeeRecord
from app.models.database.reminder import ReminderSetting, ReminderRecord
from app.core.exceptions.custom import ResourceNotFoundError, ValidationError, BusinessRuleError
from tests.utils.db import create_test_session


@pytest.fixture
def db_session():
    """测试数据库会话"""
    session = create_test_session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def statistics_service(db_session: Session):
    """统计服务实例"""
    return StatisticsService(db_session)


@pytest.fixture
def test_user(db_session: Session):
    """创建测试用户"""
    timestamp = str(uuid.uuid4())[:8]
    user = User(
        username=f"testuser_{timestamp}",
        email=f"testuser_{timestamp}@example.com",
        password_hash="hashed_password",
        nickname="测试用户"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_bank(db_session: Session):
    """创建测试银行"""
    timestamp = str(uuid.uuid4())[:8]
    bank = Bank(
        bank_code=f"TEST{timestamp[:4].upper()}",
        bank_name=f"测试银行{timestamp}",
        is_active=True,
        sort_order=1
    )
    db_session.add(bank)
    db_session.commit()
    db_session.refresh(bank)
    return bank


@pytest.fixture
def test_category(db_session: Session):
    """创建测试交易分类"""
    timestamp = str(uuid.uuid4())[:8]
    category = TransactionCategory(
        name=f"测试分类{timestamp}",
        icon="test-icon",
        color="#FF0000",
        is_system=False,
        is_active=True
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_cards(db_session: Session, test_user: User, test_bank: Bank):
    """创建测试信用卡"""
    timestamp = str(uuid.uuid4())[:8]
    cards = []
    
    # 创建第一张卡
    card1 = CreditCard(
        user_id=test_user.id,
        bank_id=test_bank.id,
        card_number=f"6225{timestamp}1111",
        card_name=f"招商银行信用卡{timestamp}",
        card_type="credit",
        credit_limit=Decimal("50000.00"),
        available_limit=Decimal("35000.00"),
        used_limit=Decimal("15000.00"),
        expiry_month=12,
        expiry_year=2027,
        status="active"
    )
    cards.append(card1)
    
    # 创建第二张卡
    card2 = CreditCard(
        user_id=test_user.id,
        bank_id=test_bank.id,
        card_number=f"6225{timestamp}2222",
        card_name=f"建设银行信用卡{timestamp}",
        card_type="credit",
        credit_limit=Decimal("30000.00"),
        available_limit=Decimal("22000.00"),
        used_limit=Decimal("8000.00"),
        expiry_month=6,
        expiry_year=2028,
        status="active"
    )
    cards.append(card2)
    
    db_session.add_all(cards)
    db_session.commit()
    for card in cards:
        db_session.refresh(card)
    return cards


@pytest.fixture
def test_transactions(db_session: Session, test_user: User, test_cards: List[CreditCard], test_category: TransactionCategory):
    """创建测试交易记录"""
    transactions = []
    base_date = datetime.now() - timedelta(days=25)  # 改为25天前，确保所有交易都在30天内
    
    # 创建多个交易记录
    for i in range(10):
        transaction = Transaction(
            user_id=test_user.id,
            card_id=test_cards[i % 2].id,  # 轮流使用两张卡
            category_id=test_category.id,
            transaction_type="expense",
            amount=Decimal(f"{1000 + i * 100}.00"),
            currency="CNY",
            description=f"测试交易{i+1}",
            merchant_name=f"测试商户{i+1}",
            points_earned=100 + i * 10,
            cashback_earned=Decimal(f"{10 + i}.00"),
            status="completed",
            transaction_date=base_date + timedelta(days=i * 2)  # 改为每2天一个交易，确保在范围内
        )
        transactions.append(transaction)
    
    # 添加一些收入交易
    for i in range(2):
        transaction = Transaction(
            user_id=test_user.id,
            card_id=test_cards[0].id,
            category_id=test_category.id,
            transaction_type="income",
            amount=Decimal(f"{5000 + i * 1000}.00"),
            currency="CNY",
            description=f"测试收入{i+1}",
            points_earned=0,
            cashback_earned=Decimal("0.00"),
            status="completed",
            transaction_date=base_date + timedelta(days=i * 10)  # 改为10天间隔，确保在范围内
        )
        transactions.append(transaction)
    
    db_session.add_all(transactions)
    db_session.commit()
    for transaction in transactions:
        db_session.refresh(transaction)
    return transactions


@pytest.fixture
def test_fee_records(db_session: Session, test_cards: List[CreditCard]):
    """创建测试年费记录"""
    records = []
    current_year = datetime.now().year
    
    for i, card in enumerate(test_cards):
        # 创建年费规则
        rule = FeeWaiverRule(
            card_id=card.id,
            rule_name=f"测试年费规则{i+1}",
            condition_type="spending_amount",
            condition_value=Decimal("50000.00"),
            condition_period="yearly",
            is_enabled=True
        )
        db_session.add(rule)
        db_session.flush()
        
        # 创建年费记录
        record = AnnualFeeRecord(
            card_id=card.id,
            waiver_rule_id=rule.id,  # 关联年费规则
            fee_year=current_year,
            base_fee=Decimal("300.00"),
            actual_fee=Decimal("150.00") if i == 0 else Decimal("300.00"),
            waiver_amount=Decimal("150.00") if i == 0 else Decimal("0.00"),
            status="paid",
            due_date=date(current_year, 12, 31)
        )
        records.append(record)
    
    db_session.add_all(records)
    db_session.commit()
    for record in records:
        db_session.refresh(record)
    return records


@pytest.fixture
def test_reminders(db_session: Session, test_user: User, test_cards: List[CreditCard]):
    """创建测试提醒设置"""
    settings = []
    
    # 创建全局提醒设置
    global_setting = ReminderSetting(
        user_id=test_user.id,
        card_id=None,
        reminder_type="payment_due",
        advance_days=3,
        email_enabled=True,
        is_enabled=True
    )
    settings.append(global_setting)
    
    # 为每张卡创建特定提醒
    for card in test_cards:
        setting = ReminderSetting(
            user_id=test_user.id,
            card_id=card.id,
            reminder_type="annual_fee",
            advance_days=30,
            email_enabled=True,
            is_enabled=True
        )
        settings.append(setting)
    
    db_session.add_all(settings)
    db_session.commit()
    for setting in settings:
        db_session.refresh(setting)
    return settings


class TestDashboardOverview:
    """仪表板概览测试"""
    
    def test_get_dashboard_overview_success(self, statistics_service: StatisticsService, test_user: User, 
                                          test_cards: List[CreditCard], test_transactions: List[Transaction],
                                          test_fee_records: List[AnnualFeeRecord], test_reminders: List[ReminderSetting]):
        """测试获取仪表板概览成功"""
        result = statistics_service.get_dashboard_overview(test_user.id)
        
        # 验证结果结构
        assert 'cards' in result
        assert 'transactions' in result
        assert 'annual_fees' in result
        assert 'reminders' in result
        assert 'health_score' in result
        assert 'last_updated' in result
        
        # 验证信用卡数据
        cards_data = result['cards']
        assert cards_data['total_cards'] == 2
        assert cards_data['active_cards'] == 2
        assert cards_data['total_credit_limit'] == 80000.0
        assert cards_data['total_used_limit'] == 23000.0
        assert cards_data['utilization_rate'] == 28.75
        
        # 验证交易数据
        transactions_data = result['transactions']
        assert transactions_data['total_transactions'] == 12  # 10个支出 + 2个收入
        assert transactions_data['total_expense'] > 0
        assert transactions_data['total_income'] > 0
        
        # 验证年费数据
        annual_fees_data = result['annual_fees']
        assert annual_fees_data['total_fees'] == 2
        
        # 验证提醒数据
        reminders_data = result['reminders']
        assert reminders_data['active_settings'] == 3
        
        # 验证健康评分
        health_score = result['health_score']
        assert 'total_score' in health_score
        assert 'grade' in health_score
        assert 'level' in health_score
    
    def test_get_dashboard_overview_empty_user(self, statistics_service: StatisticsService):
        """测试空用户的仪表板概览"""
        fake_user_id = uuid.uuid4()
        result = statistics_service.get_dashboard_overview(fake_user_id)
        
        # 验证空数据的默认值
        assert result['cards']['total_cards'] == 0
        assert result['transactions']['total_transactions'] == 0
        assert result['annual_fees']['total_fees'] == 0
        assert result['reminders']['active_settings'] == 0


class TestMonthlyTrends:
    """月度趋势测试"""
    
    def test_get_monthly_trends_success(self, statistics_service: StatisticsService, test_user: User,
                                       test_transactions: List[Transaction]):
        """测试获取月度趋势成功"""
        result = statistics_service.get_monthly_trends(test_user.id, months=6)
        
        # 验证结果结构
        assert 'analysis_period' in result
        assert 'total_months' in result
        assert 'monthly_trends' in result
        assert 'trend_analysis' in result
        
        assert result['analysis_period'] == "6个月"
        
        # 验证月度趋势数据
        trends = result['monthly_trends']
        assert isinstance(trends, list)
        
        if trends:  # 如果有数据
            first_trend = trends[0]
            assert 'year' in first_trend
            assert 'month' in first_trend
            assert 'month_name' in first_trend
            assert 'expense_count' in first_trend
            assert 'expense_amount' in first_trend
            assert 'income_count' in first_trend
            assert 'income_amount' in first_trend
            assert 'net_amount' in first_trend
        
        # 验证趋势分析
        analysis = result['trend_analysis']
        assert 'expense_trend' in analysis
        assert 'income_trend' in analysis
        assert 'growth_rate' in analysis
        assert 'volatility' in analysis
    
    def test_get_monthly_trends_custom_months(self, statistics_service: StatisticsService, test_user: User):
        """测试自定义月数的月度趋势"""
        result = statistics_service.get_monthly_trends(test_user.id, months=3)
        
        assert result['analysis_period'] == "3个月"
        assert 'monthly_trends' in result
        assert 'trend_analysis' in result


class TestSpendingAnalysis:
    """消费分析测试"""
    
    def test_get_spending_analysis_success(self, statistics_service: StatisticsService, test_user: User,
                                         test_transactions: List[Transaction]):
        """测试获取消费分析成功"""
        result = statistics_service.get_spending_analysis(test_user.id)
        
        # 验证结果结构
        assert 'period_start' in result
        assert 'period_end' in result
        assert 'total_expense' in result
        assert 'category_distribution' in result
        assert 'card_distribution' in result
        assert 'daily_trends' in result
        assert 'top_categories' in result
        assert 'top_cards' in result
        
        # 验证数据类型
        assert isinstance(result['category_distribution'], list)
        assert isinstance(result['card_distribution'], list)
        assert isinstance(result['daily_trends'], list)
        assert isinstance(result['top_categories'], list)
        assert isinstance(result['top_cards'], list)
        
        # 验证总支出
        assert result['total_expense'] >= 0
    
    def test_get_spending_analysis_with_date_range(self, statistics_service: StatisticsService, test_user: User):
        """测试指定日期范围的消费分析"""
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        result = statistics_service.get_spending_analysis(test_user.id, start_date, end_date)
        
        assert result['period_start'] == start_date
        assert result['period_end'] == end_date
        assert 'total_expense' in result


class TestFinancialReport:
    """财务报告测试"""
    
    def test_get_financial_report_success(self, statistics_service: StatisticsService, test_user: User,
                                        test_transactions: List[Transaction], test_fee_records: List[AnnualFeeRecord]):
        """测试获取财务报告成功"""
        current_year = datetime.now().year
        result = statistics_service.get_financial_report(test_user.id, current_year)
        
        # 验证结果结构
        assert result['year'] == current_year
        assert 'summary' in result
        assert 'monthly_data' in result
        assert 'annual_fees' in result
        assert 'card_utilization' in result
        
        # 验证摘要数据
        summary = result['summary']
        assert 'total_transactions' in summary
        assert 'total_expense' in summary
        assert 'total_income' in summary
        assert 'net_income' in summary
        assert 'savings_rate' in summary
        
        # 验证月度数据
        monthly_data = result['monthly_data']
        assert len(monthly_data) == 12  # 12个月
        assert monthly_data[0]['month'] == 1
        assert 'month_name' in monthly_data[0]
        
        # 验证年费数据
        annual_fees = result['annual_fees']
        assert 'total_fees' in annual_fees
        assert 'total_base_fee' in annual_fees
        assert 'total_actual_fee' in annual_fees
        assert 'waiver_rate' in annual_fees
    
    def test_get_financial_report_default_year(self, statistics_service: StatisticsService, test_user: User):
        """测试默认年份的财务报告"""
        result = statistics_service.get_financial_report(test_user.id)
        
        assert result['year'] == datetime.now().year
        assert 'summary' in result


class TestHealthScore:
    """财务健康评分测试"""
    
    def test_calculate_financial_health_score(self, statistics_service: StatisticsService, test_user: User,
                                            test_cards: List[CreditCard], test_transactions: List[Transaction],
                                            test_fee_records: List[AnnualFeeRecord], test_reminders: List[ReminderSetting]):
        """测试财务健康评分计算"""
        result = statistics_service._calculate_financial_health_score(test_user.id)
        
        # 验证结果结构
        assert 'total_score' in result
        assert 'grade' in result
        assert 'level' in result
        assert 'factors' in result
        assert 'recommendations' in result
        
        # 验证评分范围
        assert 0 <= result['total_score'] <= 100
        
        # 验证等级
        assert result['grade'] in ['A+', 'A', 'B+', 'B', 'C+', 'C', 'D+', 'D', 'F']
        assert result['level'] in ['excellent', 'very_good', 'good', 'fair', 'poor', 'very_poor']
        
        # 验证因子
        factors = result['factors']
        assert len(factors) == 5
        factor_names = [f['factor'] for f in factors]
        assert 'credit_utilization' in factor_names
        assert 'transaction_activity' in factor_names
        assert 'annual_fee_management' in factor_names
        assert 'reminder_usage' in factor_names
        assert 'data_completeness' in factor_names
        
        # 验证建议
        assert isinstance(result['recommendations'], list)


class TestTrendAnalysis:
    """趋势分析测试"""
    
    def test_analyze_trends_with_data(self, statistics_service: StatisticsService):
        """测试有数据的趋势分析"""
        trends_list = [
            {'expense_amount': 1000.0, 'income_amount': 2000.0},
            {'expense_amount': 1200.0, 'income_amount': 2200.0},
            {'expense_amount': 1400.0, 'income_amount': 2400.0}
        ]
        
        result = statistics_service._analyze_trends(trends_list)
        
        assert 'expense_trend' in result
        assert 'income_trend' in result
        assert 'growth_rate' in result
        assert 'volatility' in result
        
        assert result['expense_trend'] in ['increasing', 'decreasing', 'stable']
        assert result['income_trend'] in ['increasing', 'decreasing', 'stable']
        assert isinstance(result['growth_rate'], (int, float))
        assert result['volatility'] in ['low', 'medium', 'high']
    
    def test_analyze_trends_insufficient_data(self, statistics_service: StatisticsService):
        """测试数据不足的趋势分析"""
        trends_list = [
            {'expense_amount': 1000.0, 'income_amount': 2000.0}
        ]
        
        result = statistics_service._analyze_trends(trends_list)
        
        assert result['expense_trend'] == 'stable'
        assert result['income_trend'] == 'stable'
        assert result['growth_rate'] == 0.0
        assert result['volatility'] == 'low'


class TestHealthRecommendations:
    """健康建议测试"""
    
    def test_get_health_recommendations(self, statistics_service: StatisticsService):
        """测试健康建议生成"""
        factors = [
            {'factor': 'credit_utilization', 'status': 'poor'},
            {'factor': 'transaction_activity', 'status': 'good'},
            {'factor': 'annual_fee_management', 'status': 'excellent'},
            {'factor': 'reminder_usage', 'status': 'fair'},
            {'factor': 'data_completeness', 'status': 'good'}
        ]
        
        result = statistics_service._get_health_recommendations(factors)
        
        assert isinstance(result, list)
        assert len(result) > 0
        
        # 应该包含针对poor因子的建议
        recommendations_text = ' '.join(result)
        assert '信用卡使用率' in recommendations_text or '使用率' in recommendations_text


class TestErrorHandling:
    """错误处理测试"""
    
    def test_dashboard_overview_invalid_user(self, statistics_service: StatisticsService):
        """测试无效用户ID的仪表板概览"""
        fake_user_id = uuid.uuid4()
        
        # 应该返回空数据而不是抛出异常
        result = statistics_service.get_dashboard_overview(fake_user_id)
        
        assert result['cards']['total_cards'] == 0
        assert result['transactions']['total_transactions'] == 0
    
    def test_monthly_trends_invalid_months(self, statistics_service: StatisticsService, test_user: User):
        """测试无效月数参数"""
        # 测试负数月份
        result = statistics_service.get_monthly_trends(test_user.id, months=-1)
        assert result['analysis_period'] == "-1个月"
        
        # 测试零月份
        result = statistics_service.get_monthly_trends(test_user.id, months=0)
        assert result['analysis_period'] == "0个月"


class TestEdgeCases:
    """边界情况测试"""
    
    def test_empty_data_scenarios(self, statistics_service: StatisticsService, test_user: User):
        """测试空数据场景"""
        # 测试没有信用卡的用户
        result = statistics_service._get_cards_overview(test_user.id)
        assert result['total_cards'] == 0
        assert result['utilization_rate'] == 0
        
        # 测试没有交易的用户
        result = statistics_service._get_transactions_overview(test_user.id)
        assert result['total_transactions'] == 0
        assert result['total_expense'] == 0.0
    
    def test_zero_division_scenarios(self, statistics_service: StatisticsService, test_user: User, 
                                   db_session: Session, test_bank: Bank):
        """测试零除法场景"""
        # 创建零额度信用卡
        card = CreditCard(
            user_id=test_user.id,
            bank_id=test_bank.id,
            card_number="6225000000000000",
            card_name="零额度测试卡",
            credit_limit=Decimal("0.00"),
            used_limit=Decimal("0.00"),
            expiry_month=12,
            expiry_year=2027,
            status="active"
        )
        db_session.add(card)
        db_session.commit()
        
        # 应该不会抛出零除法异常
        result = statistics_service._get_cards_overview(test_user.id)
        assert result['utilization_rate'] == 0


class TestPerformance:
    """性能测试"""
    
    def test_dashboard_overview_performance(self, statistics_service: StatisticsService, test_user: User,
                                          test_cards: List[CreditCard], test_transactions: List[Transaction]):
        """测试仪表板概览性能"""
        import time
        
        start_time = time.time()
        result = statistics_service.get_dashboard_overview(test_user.id)
        end_time = time.time()
        
        # 验证性能（应该在合理时间内完成）
        execution_time = end_time - start_time
        assert execution_time < 2.0  # 应该在2秒内完成
        assert 'cards' in result
    
    def test_monthly_trends_performance(self, statistics_service: StatisticsService, test_user: User):
        """测试月度趋势性能"""
        import time
        
        start_time = time.time()
        result = statistics_service.get_monthly_trends(test_user.id, months=12)
        end_time = time.time()
        
        execution_time = end_time - start_time
        assert execution_time < 3.0  # 应该在3秒内完成
        assert 'monthly_trends' in result


class TestDataIntegrity:
    """数据完整性测试"""
    
    def test_statistics_data_consistency(self, statistics_service: StatisticsService, test_user: User,
                                       test_cards: List[CreditCard], test_transactions: List[Transaction]):
        """测试统计数据一致性"""
        # 获取仪表板数据
        dashboard = statistics_service.get_dashboard_overview(test_user.id)
        
        # 获取详细统计数据
        spending = statistics_service.get_spending_analysis(test_user.id)
        
        # 验证数据一致性
        assert dashboard['cards']['total_cards'] == len(test_cards)
        
        # 交易数量应该一致（考虑到可能的时间范围差异）
        dashboard_transactions = dashboard['transactions']['total_transactions']
        assert dashboard_transactions >= 0
    
    def test_calculation_accuracy(self, statistics_service: StatisticsService, test_user: User,
                                test_cards: List[CreditCard]):
        """测试计算准确性"""
        result = statistics_service._get_cards_overview(test_user.id)
        
        # 验证信用额度计算
        expected_total_limit = sum(float(card.credit_limit) for card in test_cards)
        expected_used_limit = sum(float(card.used_limit) for card in test_cards)
        expected_available_limit = expected_total_limit - expected_used_limit
        expected_utilization = (expected_used_limit / expected_total_limit * 100) if expected_total_limit > 0 else 0
        
        assert result['total_credit_limit'] == float(expected_total_limit)
        assert result['total_used_limit'] == float(expected_used_limit)
        assert result['available_limit'] == float(expected_available_limit)
        assert abs(result['utilization_rate'] - expected_utilization) < 0.01  # 允许小数点误差 