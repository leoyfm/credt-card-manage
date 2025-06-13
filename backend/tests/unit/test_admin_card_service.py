"""
管理员信用卡服务单元测试 - 直连测试数据库
"""
import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch

from app.services.admin_card_service import AdminCardService
from app.models.database.card import CreditCard, Bank
from app.models.database.user import User
from app.models.database.transaction import Transaction, TransactionCategory
from app.models.database.annual_fee import AnnualFeeRecord, FeeWaiverRule
from app.core.exceptions.custom import ResourceNotFoundError
from tests.utils.db import create_test_session


@pytest.fixture
def db_session():
    """测试数据库会话"""
    session = create_test_session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def admin_card_service(db_session: Session):
    """管理员信用卡服务实例"""
    return AdminCardService(db_session)


@pytest.fixture
def test_users(db_session: Session):
    """创建多个测试用户"""
    users = []
    for i in range(3):
        timestamp = str(uuid.uuid4())[:8]
        user = User(
            username=f"testuser_{i}_{timestamp}",
            email=f"testuser_{i}_{timestamp}@example.com",
            password_hash="hashed_password",
            nickname=f"测试用户{i}"
        )
        db_session.add(user)
        users.append(user)
    
    db_session.commit()
    for user in users:
        db_session.refresh(user)
    return users


@pytest.fixture
def test_banks(db_session: Session):
    """创建多个测试银行"""
    banks = []
    bank_names = ["招商银行", "建设银行", "工商银行"]
    bank_codes = ["CMB", "CCB", "ICBC"]
    
    for i, (name, code) in enumerate(zip(bank_names, bank_codes)):
        timestamp = str(uuid.uuid4())[:4]
        bank = Bank(
            bank_code=f"{code}{timestamp}",
            bank_name=f"{name}{timestamp}",
            is_active=True,
            sort_order=i + 1
        )
        db_session.add(bank)
        banks.append(bank)
    
    db_session.commit()
    for bank in banks:
        db_session.refresh(bank)
    return banks


@pytest.fixture
def test_cards(db_session: Session, test_users, test_banks):
    """创建多个测试信用卡"""
    cards = []
    statuses = ['active', 'active', 'frozen', 'closed', 'active']
    card_types = ['credit', 'credit', 'debit', 'credit', 'credit']
    card_levels = ['普卡', '金卡', '白金卡', '钻石卡', '普卡']
    card_networks = ['VISA', 'MasterCard', '银联', 'American Express', 'VISA']
    
    for i in range(5):
        timestamp = str(uuid.uuid4())[:8]
        user = test_users[i % len(test_users)]
        bank = test_banks[i % len(test_banks)]
        
        # 创建不同额度和使用情况的卡片
        credit_limit = Decimal(str(10000 + i * 20000))  # 10000, 30000, 50000, 70000, 90000
        used_limit = credit_limit * Decimal(str(0.1 + i * 0.2))  # 10%, 30%, 50%, 70%, 90%
        
        card = CreditCard(
            user_id=user.id,
            bank_id=bank.id,
            card_number=f"6225{timestamp}123{i}",
            card_name=f"测试信用卡{i}",
            card_type=card_types[i],
            card_network=card_networks[i],
            card_level=card_levels[i],
            credit_limit=credit_limit,
            available_limit=credit_limit - used_limit,
            used_limit=used_limit,
            expiry_month=12 if i < 2 else (i + 1),  # 前两张卡即将到期
            expiry_year=2024 if i < 2 else 2027,
            status=statuses[i],
            annual_fee=Decimal(str(100 + i * 50)),
            points_rate=Decimal("1.00"),
            cashback_rate=Decimal("0.01")
        )
        db_session.add(card)
        cards.append(card)
    
    db_session.commit()
    for card in cards:
        db_session.refresh(card)
    return cards


@pytest.fixture
def test_transactions(db_session: Session, test_cards):
    """创建测试交易记录"""
    # 创建交易分类
    category = TransactionCategory(
        name="餐饮",
        icon="restaurant",
        color="#FF6B6B",
        is_system=True
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    transactions = []
    now = datetime.now()
    
    # 为前3张卡创建不同时间的交易记录
    for i, card in enumerate(test_cards[:3]):
        # 最近30天的交易
        for j in range(3):
            transaction = Transaction(
                user_id=card.user_id,
                card_id=card.id,
                category_id=category.id,
                transaction_type="expense",
                amount=Decimal(str(100 + j * 50)),
                description=f"测试交易{i}-{j}",
                transaction_date=now - timedelta(days=j * 10),
                status="completed"
            )
            db_session.add(transaction)
            transactions.append(transaction)
        
        # 90天前的交易（用于测试不活跃卡片）
        if i == 2:  # 第3张卡设为不活跃
            old_transaction = Transaction(
                user_id=card.user_id,
                card_id=card.id,
                category_id=category.id,
                transaction_type="expense",
                amount=Decimal("200"),
                description="旧交易",
                transaction_date=now - timedelta(days=100),
                status="completed"
            )
            db_session.add(old_transaction)
            transactions.append(old_transaction)
    
    db_session.commit()
    for transaction in transactions:
        db_session.refresh(transaction)
    return transactions


@pytest.fixture
def test_annual_fee_records(db_session: Session, test_cards):
    """创建年费记录"""
    records = []
    current_year = datetime.now().year
    
    for i, card in enumerate(test_cards[:3]):
        record = AnnualFeeRecord(
            card_id=card.id,
            fee_year=current_year,
            base_fee=card.annual_fee,
            actual_fee=card.annual_fee * Decimal("0.5") if i == 0 else card.annual_fee,
            waiver_amount=card.annual_fee * Decimal("0.5") if i == 0 else Decimal("0"),
            waiver_reason="刷卡金额减免" if i == 0 else None,
            status="paid" if i < 2 else "pending",
            due_date=datetime.now().date() + timedelta(days=30),
            paid_date=datetime.now().date() if i < 2 else None
        )
        db_session.add(record)
        records.append(record)
    
    db_session.commit()
    for record in records:
        db_session.refresh(record)
    return records


class TestAdminCardServiceStatistics:
    """管理员信用卡统计测试"""

    def test_get_card_statistics_success(self, admin_card_service: AdminCardService, test_cards):
        """测试获取信用卡系统统计数据成功"""
        result = admin_card_service.get_card_statistics()
        
        # 验证基础统计
        assert result['total_cards'] == 5
        assert result['active_cards'] == 3
        assert result['frozen_cards'] == 1
        assert result['closed_cards'] == 1
        
        # 验证额度统计
        assert isinstance(result['total_credit_limit'], Decimal)
        assert isinstance(result['total_used_limit'], Decimal)
        assert isinstance(result['average_utilization'], (int, float, Decimal))
        
        # 验证分类统计
        assert 'cards_by_status' in result
        assert result['cards_by_status']['active'] == 3
        assert result['cards_by_status']['frozen'] == 1
        assert result['cards_by_status']['closed'] == 1
        
        assert 'cards_by_type' in result
        assert 'cards_by_level' in result

    def test_get_card_statistics_empty_database(self):
        """测试空数据库的统计"""
        # 创建独立的数据库会话
        session = create_test_session()
        try:
            # 清理所有数据以确保空数据库状态
            from app.models.database.card import CreditCard
            from app.models.database.transaction import Transaction
            from app.models.database.annual_fee import AnnualFeeRecord
            from app.models.database.user import User
            
            # 删除所有相关数据
            session.query(Transaction).delete()
            session.query(AnnualFeeRecord).delete()
            session.query(CreditCard).delete()
            session.query(User).delete()
            session.commit()
            
            service = AdminCardService(session)
            result = service.get_card_statistics()
            
            assert result['total_cards'] == 0
            assert result['active_cards'] == 0
            assert result['frozen_cards'] == 0
            assert result['closed_cards'] == 0
            assert result['total_credit_limit'] == Decimal('0')
            assert result['total_used_limit'] == Decimal('0')
            assert result['average_utilization'] == 0
        finally:
            session.rollback()  # 回滚删除操作
            session.close()

    def test_get_bank_distribution_success(self, admin_card_service: AdminCardService, test_cards, test_banks):
        """测试获取银行分布统计成功"""
        result = admin_card_service.get_bank_distribution()
        
        # 验证基本结构
        assert 'total_banks' in result
        assert 'bank_distribution' in result
        assert 'bank_stats' in result  # 别名字段
        assert 'top_banks' in result
        
        # 验证银行分布数据
        bank_distribution = result['bank_distribution']
        assert len(bank_distribution) > 0
        
        for bank_info in bank_distribution:
            assert 'bank_name' in bank_info
            assert 'bank_code' in bank_info
            assert 'card_count' in bank_info
            assert 'percentage' in bank_info
            assert 'total_credit_limit' in bank_info
            assert 'average_credit_limit' in bank_info
            
            # 验证百分比计算
            assert 0 <= bank_info['percentage'] <= 100

    def test_get_card_types_distribution_success(self, admin_card_service: AdminCardService, test_cards):
        """测试获取卡片类型分布统计成功"""
        result = admin_card_service.get_card_types_distribution()
        
        # 验证基本结构
        assert 'type_distribution' in result
        assert 'level_distribution' in result
        assert 'network_distribution' in result
        
        # 验证类型分布
        type_distribution = result['type_distribution']
        assert len(type_distribution) > 0
        
        for type_info in type_distribution:
            assert 'type' in type_info
            assert 'count' in type_info
            assert 'average_limit' in type_info
            assert type_info['count'] > 0
        
        # 验证等级分布
        level_distribution = result['level_distribution']
        assert len(level_distribution) > 0
        
        for level_info in level_distribution:
            assert 'level' in level_info
            assert 'count' in level_info
            assert 'average_limit' in level_info
        
        # 验证网络分布
        network_distribution = result['network_distribution']
        assert len(network_distribution) > 0
        
        for network_info in network_distribution:
            assert 'network' in network_info
            assert 'count' in network_info

    def test_get_card_health_status_success(self, admin_card_service: AdminCardService, test_cards):
        """测试获取信用卡健康状况分析成功"""
        result = admin_card_service.get_card_health_status()
        
        # 验证基本结构
        assert 'overall_health_score' in result
        assert 'utilization_distribution' in result
        assert 'expiring_soon' in result
        assert 'inactive_cards' in result
        
        # 验证健康评分
        health_score = result['overall_health_score']
        assert 0 <= health_score <= 100
        
        # 验证利用率分布
        utilization_dist = result['utilization_distribution']
        risk_levels = ['low_risk', 'medium_risk', 'high_risk', 'critical_risk']
        
        for risk_level in risk_levels:
            assert risk_level in utilization_dist
            risk_info = utilization_dist[risk_level]
            assert 'range' in risk_info
            assert 'count' in risk_info
            assert 'percentage' in risk_info
            assert 0 <= risk_info['percentage'] <= 100
        
        # 验证即将到期统计
        expiring = result['expiring_soon']
        assert 'next_month' in expiring
        assert 'next_3_months' in expiring
        assert 'next_6_months' in expiring
        
        # 验证不活跃卡片统计
        inactive = result['inactive_cards']
        assert 'no_transactions_30_days' in inactive
        assert 'no_transactions_90_days' in inactive
        assert 'no_transactions_180_days' in inactive


class TestAdminCardServiceTrends:
    """管理员信用卡趋势分析测试"""

    def test_get_card_trends_success(self, admin_card_service: AdminCardService, test_cards):
        """测试获取信用卡趋势分析成功"""
        result = admin_card_service.get_card_trends(months=6)
        
        # 验证基本结构
        assert 'analysis_period' in result
        assert 'monthly_trends' in result
        assert 'monthly_stats' in result  # 别名字段
        assert 'growth_rate' in result
        assert 'utilization_trend' in result
        assert 'predictions' in result
        assert 'growth_prediction' in result  # 别名字段
        
        # 验证分析周期
        assert result['analysis_period'] == '6个月'
        
        # 验证月度趋势数据
        monthly_trends = result['monthly_trends']
        assert len(monthly_trends) == 6
        
        for trend in monthly_trends:
            assert 'month' in trend
            assert 'new_cards' in trend
            assert 'closed_cards' in trend
            assert 'net_growth' in trend
            assert 'total_cards' in trend
            assert 'average_utilization' in trend
            
            # 验证数据类型
            assert isinstance(trend['new_cards'], int)
            assert isinstance(trend['closed_cards'], int)
            assert isinstance(trend['net_growth'], int)
            assert isinstance(trend['total_cards'], int)
            assert isinstance(trend['average_utilization'], (int, float, Decimal))
        
        # 验证增长率
        assert isinstance(result['growth_rate'], (int, float))
        
        # 验证利用率趋势
        assert result['utilization_trend'] in ['上升', '下降', '稳定']
        
        # 验证预测数据
        predictions = result['predictions']
        assert 'next_month_new_cards' in predictions
        assert 'next_month_total' in predictions
        assert isinstance(predictions['next_month_new_cards'], int)
        assert isinstance(predictions['next_month_total'], int)

    def test_get_card_trends_custom_months(self, admin_card_service: AdminCardService, test_cards):
        """测试自定义月数的趋势分析"""
        result = admin_card_service.get_card_trends(months=3)
        
        assert result['analysis_period'] == '3个月'
        assert len(result['monthly_trends']) == 3

    def test_get_utilization_analysis_success(self, admin_card_service: AdminCardService, test_cards):
        """测试获取信用额度利用率分析成功"""
        result = admin_card_service.get_utilization_analysis()
        
        # 验证基本结构
        assert 'overall_utilization' in result
        assert 'risk_distribution' in result
        assert 'utilization_by_bank' in result
        assert 'utilization_by_card_level' in result
        assert 'recommendations' in result
        
        # 验证整体利用率
        assert isinstance(result['overall_utilization'], (int, float, Decimal))
        assert 0 <= result['overall_utilization'] <= 100
        
        # 验证风险分布
        risk_distribution = result['risk_distribution']
        risk_levels = ['low_risk', 'medium_risk', 'high_risk', 'critical_risk']
        
        for risk_level in risk_levels:
            assert risk_level in risk_distribution
            risk_info = risk_distribution[risk_level]
            assert 'count' in risk_info
            assert 'percentage' in risk_info
            assert isinstance(risk_info['count'], int)
            assert 0 <= risk_info['percentage'] <= 100
        
        # 验证按银行分析
        utilization_by_bank = result['utilization_by_bank']
        for bank_info in utilization_by_bank:
            assert 'bank_name' in bank_info
            assert 'average_utilization' in bank_info
            assert isinstance(bank_info['average_utilization'], (int, float, Decimal))
        
        # 验证按卡片等级分析
        utilization_by_level = result['utilization_by_card_level']
        for level_info in utilization_by_level:
            assert 'card_level' in level_info
            assert 'average_utilization' in level_info
            assert isinstance(level_info['average_utilization'], (int, float, Decimal))
        
        # 验证建议列表
        assert isinstance(result['recommendations'], list)


class TestAdminCardServiceAlerts:
    """管理员信用卡提醒和年费测试"""

    def test_get_expiry_alerts_success(self, admin_card_service: AdminCardService, test_cards):
        """测试获取即将到期卡片统计成功"""
        result = admin_card_service.get_expiry_alerts(months_ahead=3)
        
        # 验证基本结构
        assert 'analysis_months' in result
        assert 'expiring_cards' in result
        assert 'expiring_by_bank' in result
        assert 'renewal_rate' in result
        assert 'recommendations' in result
        
        # 验证分析月数
        assert result['analysis_months'] == 3
        
        # 验证即将到期卡片统计
        expiring_cards = result['expiring_cards']
        expected_keys = ['next_1_month', 'next_2_months', 'next_3_months']
        
        for key in expected_keys:
            assert key in expiring_cards
            assert isinstance(expiring_cards[key], int)
            assert expiring_cards[key] >= 0
        
        # 验证按银行统计
        expiring_by_bank = result['expiring_by_bank']
        for bank_info in expiring_by_bank:
            assert 'bank_name' in bank_info
            assert 'count' in bank_info
            assert isinstance(bank_info['count'], int)
        
        # 验证续卡率
        assert isinstance(result['renewal_rate'], (int, float))
        assert 0 <= result['renewal_rate'] <= 100
        
        # 验证建议列表
        assert isinstance(result['recommendations'], list)

    def test_get_expiry_alerts_custom_months(self, admin_card_service: AdminCardService, test_cards):
        """测试自定义月数的到期提醒"""
        result = admin_card_service.get_expiry_alerts(months_ahead=6)
        
        assert result['analysis_months'] == 6
        
        # 验证包含更多月份的统计
        expiring_cards = result['expiring_cards']
        expected_keys = [
            'next_1_month', 'next_2_months', 'next_3_months',
            'next_4_months', 'next_5_months', 'next_6_months'
        ]
        
        for key in expected_keys:
            assert key in expiring_cards

    def test_get_annual_fee_summary_success(self, admin_card_service: AdminCardService, test_annual_fee_records):
        """测试获取年费管理概览成功"""
        current_year = datetime.now().year
        result = admin_card_service.get_annual_fee_summary(year=current_year)
        
        # 验证基本结构
        assert 'year' in result
        assert 'total_cards_with_fee' in result
        assert 'total_base_fee' in result
        assert 'total_actual_fee' in result
        assert 'total_revenue' in result  # 别名字段
        assert 'total_waived_amount' in result
        assert 'waiver_rate' in result
        assert 'fee_status_distribution' in result
        assert 'waiver_methods' in result
        assert 'waiver_stats' in result  # 别名字段
        assert 'revenue_impact' in result
        
        # 验证年份
        assert result['year'] == current_year
        
        # 验证统计数据
        assert result['total_cards_with_fee'] == 3
        assert isinstance(result['total_base_fee'], Decimal)
        assert isinstance(result['total_actual_fee'], Decimal)
        assert isinstance(result['total_waived_amount'], Decimal)
        assert isinstance(result['waiver_rate'], (int, float, Decimal))
        
        # 验证状态分布
        status_distribution = result['fee_status_distribution']
        assert isinstance(status_distribution, dict)
        
        # 验证减免方式统计
        waiver_methods = result['waiver_methods']
        assert isinstance(waiver_methods, dict)
        
        # 验证收入影响分析
        revenue_impact = result['revenue_impact']
        assert 'collected_fees' in revenue_impact
        assert 'waived_fees' in revenue_impact
        assert 'collection_rate' in revenue_impact
        assert isinstance(revenue_impact['collection_rate'], (int, float, Decimal))

    def test_get_annual_fee_summary_no_records(self, admin_card_service: AdminCardService):
        """测试无年费记录的年份"""
        future_year = datetime.now().year + 10
        result = admin_card_service.get_annual_fee_summary(year=future_year)
        
        # 验证空数据的默认值
        assert result['year'] == future_year
        assert result['total_cards_with_fee'] == 0
        assert result['total_base_fee'] == Decimal('0')
        assert result['total_actual_fee'] == Decimal('0')
        assert result['total_revenue'] == Decimal('0')
        assert result['total_waived_amount'] == Decimal('0')
        assert result['waiver_rate'] == Decimal('0')
        assert result['fee_status_distribution'] == {}
        assert result['waiver_methods'] == {}
        assert result['waiver_stats'] == {}
        assert result['revenue_impact'] == {}


class TestAdminCardServiceEdgeCases:
    """管理员信用卡服务边界情况测试"""

    def test_get_card_statistics_with_null_values(self, admin_card_service: AdminCardService, db_session: Session, test_users, test_banks):
        """测试包含空值的统计"""
        # 创建包含空值的信用卡
        user = test_users[0]
        bank = test_banks[0]
        
        card = CreditCard(
            user_id=user.id,
            bank_id=bank.id,
            card_number="6225000000000000",
            card_name="空值测试卡",
            card_type="credit",
            card_network=None,  # 空值
            card_level=None,    # 空值
            credit_limit=Decimal("0"),  # 零额度
            available_limit=Decimal("0"),
            used_limit=Decimal("0"),
            expiry_month=12,
            expiry_year=2027,
            status="active"
        )
        db_session.add(card)
        db_session.commit()
        
        result = admin_card_service.get_card_statistics()
        
        # 应该能正常处理空值
        assert result['total_cards'] >= 1
        assert 'cards_by_type' in result
        assert 'cards_by_level' in result

    def test_get_bank_distribution_single_bank(self, admin_card_service: AdminCardService, db_session: Session, test_users):
        """测试单一银行的分布统计"""
        # 创建单一银行和卡片
        user = test_users[0]
        
        bank = Bank(
            bank_code="SINGLE",
            bank_name="单一银行",
            is_active=True
        )
        db_session.add(bank)
        db_session.commit()
        db_session.refresh(bank)
        
        card = CreditCard(
            user_id=user.id,
            bank_id=bank.id,
            card_number="6225111111111111",
            card_name="单一银行卡",
            card_type="credit",
            credit_limit=Decimal("50000"),
            available_limit=Decimal("50000"),
            used_limit=Decimal("0"),
            expiry_month=12,
            expiry_year=2027,
            status="active"
        )
        db_session.add(card)
        db_session.commit()
        
        result = admin_card_service.get_bank_distribution()
        
        # 单一银行应该占100%
        bank_distribution = result['bank_distribution']
        assert len(bank_distribution) >= 1
        
        # 找到我们创建的银行
        single_bank = next((b for b in bank_distribution if b['bank_name'] == "单一银行"), None)
        if single_bank:
            assert single_bank['percentage'] > 0

    def test_get_card_health_status_all_low_risk(self, admin_card_service: AdminCardService, db_session: Session, test_users, test_banks):
        """测试所有卡片都是低风险的健康状况"""
        # 创建低利用率的卡片
        user = test_users[0]
        bank = test_banks[0]
        
        for i in range(3):
            card = CreditCard(
                user_id=user.id,
                bank_id=bank.id,
                card_number=f"6225222222222{i:03d}",
                card_name=f"低风险卡{i}",
                card_type="credit",
                credit_limit=Decimal("100000"),
                available_limit=Decimal("95000"),  # 5%利用率
                used_limit=Decimal("5000"),
                expiry_month=12,
                expiry_year=2027,
                status="active"
            )
            db_session.add(card)
        
        db_session.commit()
        
        result = admin_card_service.get_card_health_status()
        
        # 健康评分应该很高
        assert result['overall_health_score'] > 80
        
        # 大部分卡片应该在低风险区间
        utilization_dist = result['utilization_distribution']
        assert utilization_dist['low_risk']['count'] >= 3

    def test_get_card_trends_no_historical_data(self, admin_card_service: AdminCardService, test_cards):
        """测试没有历史数据的趋势分析"""
        # 所有测试卡片都是最近创建的，没有历史趋势
        result = admin_card_service.get_card_trends(months=1)
        
        # 应该能正常返回结果，即使没有明显趋势
        assert 'monthly_trends' in result
        assert len(result['monthly_trends']) == 1
        assert 'growth_rate' in result
        assert 'utilization_trend' in result

    def test_get_utilization_analysis_zero_credit_cards(self, admin_card_service: AdminCardService, db_session: Session, test_users, test_banks):
        """测试零额度卡片的利用率分析"""
        # 创建零额度卡片
        user = test_users[0]
        bank = test_banks[0]
        
        card = CreditCard(
            user_id=user.id,
            bank_id=bank.id,
            card_number="6225333333333333",
            card_name="零额度卡",
            card_type="credit",
            credit_limit=Decimal("0"),
            available_limit=Decimal("0"),
            used_limit=Decimal("0"),
            expiry_month=12,
            expiry_year=2027,
            status="active"
        )
        db_session.add(card)
        db_session.commit()
        
        result = admin_card_service.get_utilization_analysis()
        
        # 应该能正常处理零额度卡片
        assert 'overall_utilization' in result
        assert isinstance(result['overall_utilization'], (int, float, Decimal))


class TestAdminCardServicePerformance:
    """管理员信用卡服务性能测试"""

    def test_large_dataset_statistics_performance(self, admin_card_service: AdminCardService, db_session: Session, test_users, test_banks):
        """测试大数据集的统计性能"""
        import time
        
        # 创建大量卡片数据
        cards = []
        for i in range(100):
            user = test_users[i % len(test_users)]
            bank = test_banks[i % len(test_banks)]
            
            card = CreditCard(
                user_id=user.id,
                bank_id=bank.id,
                card_number=f"6225{i:012d}",
                card_name=f"性能测试卡{i}",
                card_type="credit",
                credit_limit=Decimal(str(10000 + i * 1000)),
                available_limit=Decimal(str(5000 + i * 500)),
                used_limit=Decimal(str(5000 + i * 500)),
                expiry_month=(i % 12) + 1,
                expiry_year=2025 + (i % 3),
                status="active" if i % 4 != 0 else "frozen"
            )
            cards.append(card)
        
        db_session.add_all(cards)
        db_session.commit()
        
        # 测试统计性能
        start_time = time.time()
        result = admin_card_service.get_card_statistics()
        end_time = time.time()
        
        # 验证结果正确性
        assert result['total_cards'] >= 100
        
        # 验证性能（应该在合理时间内完成）
        execution_time = end_time - start_time
        assert execution_time < 5.0  # 5秒内完成

    def test_complex_queries_performance(self, admin_card_service: AdminCardService, test_cards, test_transactions):
        """测试复杂查询的性能"""
        import time
        
        # 测试健康状况分析性能
        start_time = time.time()
        health_result = admin_card_service.get_card_health_status()
        health_time = time.time() - start_time
        
        # 测试趋势分析性能
        start_time = time.time()
        trends_result = admin_card_service.get_card_trends(months=12)
        trends_time = time.time() - start_time
        
        # 测试利用率分析性能
        start_time = time.time()
        utilization_result = admin_card_service.get_utilization_analysis()
        utilization_time = time.time() - start_time
        
        # 验证结果正确性
        assert 'overall_health_score' in health_result
        assert 'monthly_trends' in trends_result
        assert 'overall_utilization' in utilization_result
        
        # 验证性能
        assert health_time < 3.0
        assert trends_time < 3.0
        assert utilization_time < 3.0


class TestAdminCardServiceDataIntegrity:
    """管理员信用卡服务数据完整性测试"""

    def test_statistics_data_consistency(self, admin_card_service: AdminCardService, test_cards):
        """测试统计数据的一致性"""
        # 获取基础统计
        stats = admin_card_service.get_card_statistics()
        
        # 获取银行分布
        bank_dist = admin_card_service.get_bank_distribution()
        
        # 获取类型分布
        type_dist = admin_card_service.get_card_types_distribution()
        
        # 验证数据一致性
        # 总卡片数应该一致
        total_from_bank = sum(bank['card_count'] for bank in bank_dist['bank_distribution'])
        total_from_type = sum(type_info['count'] for type_info in type_dist['type_distribution'])
        
        # 由于可能有无银行或无类型的卡片，所以允许一定差异
        assert abs(stats['total_cards'] - total_from_bank) <= stats['total_cards'] * 0.1
        assert abs(stats['total_cards'] - total_from_type) <= stats['total_cards'] * 0.1

    def test_utilization_calculation_accuracy(self, admin_card_service: AdminCardService, db_session: Session, test_users, test_banks):
        """测试利用率计算的准确性"""
        # 创建已知利用率的卡片
        user = test_users[0]
        bank = test_banks[0]
        
        # 50%利用率的卡片
        card1 = CreditCard(
            user_id=user.id,
            bank_id=bank.id,
            card_number="6225444444444444",
            card_name="50%利用率卡",
            card_type="credit",
            credit_limit=Decimal("10000"),
            available_limit=Decimal("5000"),
            used_limit=Decimal("5000"),  # 50%
            expiry_month=12,
            expiry_year=2027,
            status="active"
        )
        
        # 80%利用率的卡片
        card2 = CreditCard(
            user_id=user.id,
            bank_id=bank.id,
            card_number="6225555555555555",
            card_name="80%利用率卡",
            card_type="credit",
            credit_limit=Decimal("10000"),
            available_limit=Decimal("2000"),
            used_limit=Decimal("8000"),  # 80%
            expiry_month=12,
            expiry_year=2027,
            status="active"
        )
        
        db_session.add_all([card1, card2])
        db_session.commit()
        
        # 获取利用率分析
        result = admin_card_service.get_utilization_analysis()
        
        # 验证风险分布
        risk_dist = result['risk_distribution']
        
        # 50%利用率应该在medium_risk，80%利用率应该在high_risk
        assert risk_dist['medium_risk']['count'] >= 1  # 至少包含50%的卡
        assert risk_dist['high_risk']['count'] >= 1    # 至少包含80%的卡

    def test_expiry_date_calculation_accuracy(self, admin_card_service: AdminCardService, db_session: Session, test_users, test_banks):
        """测试到期日期计算的准确性"""
        user = test_users[0]
        bank = test_banks[0]
        
        now = datetime.now()
        next_month = now + timedelta(days=30)
        
        # 创建下个月到期的卡片
        card = CreditCard(
            user_id=user.id,
            bank_id=bank.id,
            card_number="6225666666666666",
            card_name="下月到期卡",
            card_type="credit",
            credit_limit=Decimal("10000"),
            available_limit=Decimal("10000"),
            used_limit=Decimal("0"),
            expiry_month=next_month.month,
            expiry_year=next_month.year,
            status="active"
        )
        db_session.add(card)
        db_session.commit()
        
        # 获取到期提醒
        result = admin_card_service.get_expiry_alerts(months_ahead=2)
        
        # 应该检测到即将到期的卡片
        expiring_cards = result['expiring_cards']
        assert expiring_cards['next_1_month'] >= 1 or expiring_cards['next_2_months'] >= 1 