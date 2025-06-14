#!/usr/bin/env python3
"""
年费服务单元测试

测试年费规则和年费记录的CRUD操作、减免评估、统计分析等功能
"""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4, UUID
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.services.annual_fee_service import AnnualFeeService
from app.models.database.user import User
from app.models.database.card import Bank, CreditCard
from app.models.database.transaction import TransactionCategory
from app.models.database.fee_waiver import FeeWaiverRule, AnnualFeeRecord
from app.models.schemas.fee_waiver import (
    FeeWaiverRuleCreate, FeeWaiverRuleUpdate, 
    AnnualFeeRecordCreate, AnnualFeeRecordUpdate
)
from app.core.exceptions.custom import ResourceNotFoundError, BusinessRuleError


# ========== 测试Fixtures ==========

@pytest.fixture
def db_session():
    """模拟数据库会话"""
    return Mock(spec=Session)


@pytest.fixture
def annual_fee_service(db_session: Session):
    """年费服务fixture"""
    return AnnualFeeService(db_session)


@pytest.fixture
def test_user():
    """测试用户fixture"""
    return User(
        id=uuid4(),
        username="testuser",
        email="test@example.com",
        nickname="测试用户",
        is_active=True,
        is_verified=True
    )


@pytest.fixture
def test_bank(db_session: Session):
    """测试银行fixture"""
    return Bank(
        id=uuid4(),
        bank_name="测试银行",
        bank_code="TEST",
        bank_logo="https://example.com/logo.png",
        is_active=True,
        sort_order=1
    )


@pytest.fixture
def test_card(test_user: User, test_bank: Bank):
    """测试信用卡fixture"""
    return CreditCard(
        id=uuid4(),
        user_id=test_user.id,
        bank_id=test_bank.id,
        card_name="测试信用卡",
        card_number="1234****5678",
        card_type="credit",
        credit_limit=Decimal("50000.00"),
        available_limit=Decimal("45000.00"),
        expiry_month=12,
        expiry_year=2027,
        status="active"
    )


@pytest.fixture
def test_category():
    """测试消费类别fixture"""
    return TransactionCategory(
        id=uuid4(),
        name="餐饮",
        icon="restaurant",
        color="#FF6B6B",
        is_active=True
    )


@pytest.fixture
def test_rule(test_card: CreditCard):
    """测试年费规则fixture"""
    return FeeWaiverRule(
        id=uuid4(),
        card_id=test_card.id,
        rule_name="年消费满5万免年费",
        condition_type="spending_amount",
        condition_value=Decimal("50000.00"),
        condition_count=None,
        condition_period="yearly",
        logical_operator=None,
        priority=1,
        is_enabled=True,
        effective_from=date(2024, 1, 1),
        effective_to=date(2024, 12, 31),
        description="年消费满5万免年费"
    )


@pytest.fixture
def test_record(test_rule: FeeWaiverRule):
    """测试年费记录fixture"""
    return AnnualFeeRecord(
        id=uuid4(),
        waiver_rule_id=test_rule.id,
        card_id=test_rule.card_id,
        fee_year=2024,
        base_fee=Decimal("300.00"),
        actual_fee=Decimal("0.00"),
        waiver_amount=Decimal("300.00"),
        waiver_reason="年消费满5万，符合减免条件",
        status="waived",
        due_date=date(2024, 12, 31),
        notes="自动减免"
    )


# ========== 年费规则CRUD测试 ==========

class TestFeeWaiverRuleCRUD:
    """年费规则CRUD操作测试"""

    def test_create_annual_fee_rule_success(self, annual_fee_service: AnnualFeeService, 
                                          test_user: User, test_card: CreditCard, db_session: Session):
        """测试创建年费规则成功"""
        # 模拟数据库查询
        db_session.query.return_value.filter.return_value.first.return_value = test_card
        db_session.query.return_value.filter.return_value.first.side_effect = [test_card, None]
        
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            rule_name="年消费满5万免年费",
            condition_type="spending_amount",
            condition_value=Decimal("50000.00"),
            condition_period="yearly",
            is_enabled=True,
            effective_from=date(2024, 1, 1),
            effective_to=date(2024, 12, 31),
            description="年消费满5万免年费"
        )
        
        # 模拟创建的规则
        created_rule = FeeWaiverRule(**rule_data.model_dump())
        created_rule.id = uuid4()
        created_rule.created_at = datetime.now()
        created_rule.updated_at = datetime.now()
        
        db_session.add.return_value = None
        db_session.commit.return_value = None
        db_session.refresh.return_value = None
        
        # 模拟_to_rule_response方法
        with patch.object(annual_fee_service, '_to_rule_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.create_fee_waiver_rule(test_user.id, rule_data)
            
            assert result is not None
            db_session.add.assert_called_once()
            db_session.commit.assert_called_once()

    def test_create_annual_fee_rule_card_not_found(self, annual_fee_service: AnnualFeeService, 
                                                  test_user: User, db_session: Session):
        """测试创建年费规则时信用卡不存在"""
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        rule_data = FeeWaiverRuleCreate(
            card_id=uuid4(),
            rule_name="年消费满5万免年费",
            condition_type="spending_amount",
            condition_value=Decimal("50000.00")
        )
        
        with pytest.raises(ResourceNotFoundError, match="信用卡不存在或不属于当前用户"):
            annual_fee_service.create_fee_waiver_rule(test_user.id, rule_data)

    def test_create_annual_fee_rule_duplicate_year(self, annual_fee_service: AnnualFeeService, 
                                                  test_user: User, test_card: CreditCard, 
                                                  test_rule: FeeWaiverRule, db_session: Session):
        """测试创建年费规则时年份重复"""
        db_session.query.return_value.filter.return_value.first.side_effect = [test_card, test_rule]
        
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            rule_name="年消费满5万免年费",
            condition_type="spending_amount",
            condition_value=Decimal("50000.00")
        )
        
        with pytest.raises(BusinessRuleError, match="年费规则已存在"):
            annual_fee_service.create_fee_waiver_rule(test_user.id, rule_data)

    def test_get_annual_fee_rule_success(self, annual_fee_service: AnnualFeeService, 
                                        test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试获取年费规则成功"""
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        
        with patch.object(annual_fee_service, '_to_rule_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.get_annual_fee_rule(test_user.id, test_rule.id)
            
            assert result is not None
            mock_response.assert_called_once_with(test_rule)

    def test_get_annual_fee_rule_not_found(self, annual_fee_service: AnnualFeeService, 
                                          test_user: User, db_session: Session):
        """测试获取不存在的年费规则"""
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ResourceNotFoundError, match="年费规则不存在"):
            annual_fee_service.get_annual_fee_rule(test_user.id, uuid4())

    def test_update_annual_fee_rule_success(self, annual_fee_service: AnnualFeeService, 
                                           test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试更新年费规则成功"""
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        
        update_data = FeeWaiverRuleUpdate(
            condition_value=Decimal("60000.00"),
            description="调整为年消费满6万免年费"
        )
        
        with patch.object(annual_fee_service, '_to_rule_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.update_annual_fee_rule(test_user.id, test_rule.id, update_data)
            
            assert result is not None
            assert test_rule.condition_value == Decimal("60000.00")
            assert test_rule.description == "调整为年消费满6万免年费"
            db_session.commit.assert_called_once()

    def test_delete_annual_fee_rule_success(self, annual_fee_service: AnnualFeeService, 
                                           test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试删除年费规则成功"""
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        db_session.query.return_value.filter.return_value.count.return_value = 0
        
        result = annual_fee_service.delete_annual_fee_rule(test_user.id, test_rule.id)
        
        assert result is True
        db_session.delete.assert_called_once_with(test_rule)
        db_session.commit.assert_called_once()

    def test_delete_annual_fee_rule_with_records(self, annual_fee_service: AnnualFeeService, 
                                                test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试删除有关联记录的年费规则"""
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        db_session.query.return_value.filter.return_value.count.return_value = 1
        
        with pytest.raises(BusinessRuleError, match="存在关联的年费记录"):
            annual_fee_service.delete_annual_fee_rule(test_user.id, test_rule.id)


# ========== 年费记录CRUD测试 ==========

class TestAnnualFeeRecordCRUD:
    """年费记录CRUD操作测试"""

    def test_create_annual_fee_record_success(self, annual_fee_service: AnnualFeeService, 
                                             test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试创建年费记录成功"""
        # 配置数据库查询模拟 - 第一次查询返回规则，第二次查询返回None（没有现有记录）
        mock_query = Mock()
        mock_join = Mock()
        mock_filter = Mock()
        
        # 第一次查询：获取规则
        mock_filter.first.side_effect = [test_rule, None]
        mock_join.filter.return_value = mock_filter
        mock_query.join.return_value = mock_join
        mock_query.filter.return_value = mock_filter
        db_session.query.return_value = mock_query
        
        # 创建年费记录
        record_data = AnnualFeeRecordCreate(
            waiver_rule_id=test_rule.id,
            fee_year=2024,
            base_fee=Decimal("300.00"),
            actual_fee=Decimal("0.00"),
            waiver_amount=Decimal("300.00"),
            waiver_reason="测试减免",
            status="waived"
        )
        
        # 模拟创建的记录
        created_record = AnnualFeeRecord(**record_data.model_dump())
        created_record.id = uuid4()
        created_record.created_at = datetime.now()
        created_record.updated_at = datetime.now()
        
        db_session.add.return_value = None
        db_session.commit.return_value = None
        db_session.refresh.return_value = None
        
        # 模拟_to_record_response方法
        with patch.object(annual_fee_service, '_to_record_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.create_annual_fee_record(test_user.id, record_data)
            
            assert result is not None
            db_session.add.assert_called_once()
            db_session.commit.assert_called_once()

    def test_get_annual_fee_record_success(self, annual_fee_service: AnnualFeeService, 
                                          test_user: User, test_record: AnnualFeeRecord, db_session: Session):
        """测试获取年费记录成功"""
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_record
        
        with patch.object(annual_fee_service, '_to_record_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.get_annual_fee_record(test_user.id, test_record.id)
            
            assert result is not None
            mock_response.assert_called_once_with(test_record)

    def test_update_annual_fee_record_success(self, annual_fee_service: AnnualFeeService, 
                                             test_user: User, test_record: AnnualFeeRecord, db_session: Session):
        """测试更新年费记录成功"""
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_record
        
        update_data = AnnualFeeRecordUpdate(
            actual_fee=Decimal("300.00"),
            status="paid",
            paid_date=date(2024, 1, 15),
            notes="已缴费"
        )
        
        with patch.object(annual_fee_service, '_to_record_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.update_annual_fee_record(test_user.id, test_record.id, update_data)
            
            assert result is not None
            assert test_record.actual_fee == Decimal("300.00")
            assert test_record.status == "paid"
            assert test_record.notes == "已缴费"
            db_session.commit.assert_called_once()


# ========== 年费减免评估测试 ==========

class TestWaiverEvaluation:
    """年费减免评估测试"""

    def test_evaluate_spending_amount_waiver_eligible(self, annual_fee_service: AnnualFeeService, 
                                                     test_user: User, test_rule: FeeWaiverRule, 
                                                     test_card: CreditCard, db_session: Session):
        """测试消费金额减免评估 - 符合条件"""
        # 模拟查询规则
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        
        # 模拟交易查询 - 返回足够的消费金额
        mock_transactions = [Mock(amount=Decimal("30000.00")), Mock(amount=Decimal("25000.00"))]
        db_session.query.return_value.filter.return_value.all.return_value = mock_transactions
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, test_rule.id)
        
        assert result.is_eligible is True
        assert result.current_progress == 55000.00
        assert result.required_target == 50000.00
        assert result.completion_percentage == 110.0

    def test_evaluate_spending_amount_waiver_not_eligible(self, annual_fee_service: AnnualFeeService, 
                                                         test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试消费金额减免评估 - 不符合条件"""
        # 模拟查询规则
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        
        # 模拟交易查询 - 返回不足的消费金额
        mock_transactions = [Mock(amount=Decimal("20000.00")), Mock(amount=Decimal("15000.00"))]
        db_session.query.return_value.filter.return_value.all.return_value = mock_transactions
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, test_rule.id)
        
        assert result.is_eligible is False
        assert result.current_progress == 35000.00
        assert result.required_target == 50000.00
        assert result.completion_percentage == 70.0

    def test_evaluate_transaction_count_waiver(self, annual_fee_service: AnnualFeeService, 
                                              test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试交易次数减免评估"""
        # 修改规则为交易次数类型
        test_rule.condition_type = "transaction_count"
        test_rule.condition_count = 12
        
        # 模拟查询规则
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        
        # 模拟交易查询 - 返回足够的交易次数
        mock_transactions = [Mock() for _ in range(15)]
        db_session.query.return_value.filter.return_value.all.return_value = mock_transactions
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, test_rule.id)
        
        assert result.is_eligible is True
        assert result.current_progress == 15
        assert result.required_target == 12

    def test_evaluate_rigid_waiver(self, annual_fee_service: AnnualFeeService, 
                                  test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试刚性年费评估"""
        # 修改规则为刚性年费
        test_rule.condition_type = "rigid"
        
        # 模拟查询规则
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, test_rule.id)
        
        assert result.is_eligible is False
        assert result.current_progress == 0
        assert result.required_target == 0
        assert result.completion_percentage == 0.0
        assert "刚性年费，无法减免" in result.evaluation_message


# ========== 年费统计测试 ==========

class TestAnnualFeeStatistics:
    """年费统计测试"""

    def test_get_annual_fee_statistics_success(self, annual_fee_service: AnnualFeeService, 
                                              test_user: User, db_session: Session):
        """测试获取年费统计成功"""
        # 模拟统计查询结果
        mock_stats = Mock()
        mock_stats.total_cards_with_fee = 3
        mock_stats.total_base_fee = Decimal("900.00")
        mock_stats.total_actual_fee = Decimal("300.00")
        mock_stats.total_waived_amount = Decimal("600.00")
        
        # 模拟状态分布查询
        mock_status_dist = [
            Mock(status="paid", count=1),
            Mock(status="waived", count=2)
        ]
        
        # 模拟减免类型分布查询
        mock_waiver_dist = [
            Mock(waiver_type="spending_amount", count=2),
            Mock(waiver_type="transaction_count", count=1)
        ]
        
        # 模拟即将到期的年费
        mock_upcoming = [
            Mock(id=uuid4(), card_name="测试卡1", base_fee=Decimal("300.00"), due_date=date(2024, 12, 31))
        ]
        
        # 配置数据库查询模拟
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = mock_stats
        db_session.query.return_value.join.return_value.filter.return_value.group_by.return_value.all.side_effect = [
            mock_status_dist, mock_waiver_dist, mock_upcoming
        ]
        
        result = annual_fee_service.get_annual_fee_statistics(test_user.id, 2024)
        
        assert result.year == 2024
        assert result.total_cards_with_fee == 3
        assert result.total_base_fee == Decimal("900.00")
        assert result.total_actual_fee == Decimal("300.00")
        assert result.total_waived_amount == Decimal("600.00")


# ========== 错误处理测试 ==========

class TestAnnualFeeServiceErrorHandling:
    """年费服务错误处理测试"""

    def test_database_error_handling(self, annual_fee_service: AnnualFeeService, 
                                    test_user: User, db_session: Session):
        """测试数据库错误处理"""
        db_session.query.side_effect = Exception("数据库连接错误")
        
        with pytest.raises(Exception, match="数据库连接错误"):
            annual_fee_service.get_user_annual_fee_rules(test_user.id)

    def test_invalid_waiver_type_validation(self):
        """测试无效减免类型验证"""
        with pytest.raises(ValueError):
            rule_data = FeeWaiverRuleCreate(
                card_id=uuid4(),
                rule_name="测试规则",
                condition_type="invalid_type",
                condition_value=Decimal("50000.00")
            )


# ========== 边界情况测试 ==========

class TestAnnualFeeServiceEdgeCases:
    """年费服务边界情况测试"""

    def test_zero_base_fee_rule(self, annual_fee_service: AnnualFeeService, 
                               test_user: User, test_card: CreditCard, db_session: Session):
        """测试零年费规则"""
        db_session.query.return_value.filter.return_value.first.return_value = test_card
        db_session.query.return_value.filter.return_value.first.side_effect = [test_card, None]
        
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            rule_name="免年费卡",
            condition_type="rigid",
            condition_value=Decimal("0.00")
        )
        
        with patch.object(annual_fee_service, '_to_rule_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.create_fee_waiver_rule(test_user.id, rule_data)
            assert result is not None

    def test_future_year_rule(self, annual_fee_service: AnnualFeeService, 
                             test_user: User, test_card: CreditCard, db_session: Session):
        """测试未来年份规则"""
        future_year = datetime.now().year + 1
        
        db_session.query.return_value.filter.return_value.first.return_value = test_card
        db_session.query.return_value.filter.return_value.first.side_effect = [test_card, None]
        
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            rule_name="未来年费规则",
            condition_type="spending_amount",
            condition_value=Decimal("50000.00"),
            effective_from=date(future_year, 1, 1),
            effective_to=date(future_year, 12, 31)
        )
        
        with patch.object(annual_fee_service, '_to_rule_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.create_fee_waiver_rule(test_user.id, rule_data)
            assert result is not None

    def test_large_waiver_condition_value(self, annual_fee_service: AnnualFeeService, 
                                         test_user: User, test_card: CreditCard, db_session: Session):
        """测试大额减免条件值"""
        db_session.query.return_value.filter.return_value.first.return_value = test_card
        db_session.query.return_value.filter.return_value.first.side_effect = [test_card, None]
        
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            rule_name="高额消费减免",
            condition_type="spending_amount",
            condition_value=Decimal("1000000.00")
        )
        
        with patch.object(annual_fee_service, '_to_rule_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.create_fee_waiver_rule(test_user.id, rule_data)
            assert result is not None

    def test_empty_user_rules_list(self, annual_fee_service: AnnualFeeService, 
                                  test_user: User, db_session: Session):
        """测试用户无年费规则的情况"""
        db_session.query.return_value.join.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        db_session.query.return_value.join.return_value.filter.return_value.count.return_value = 0
        
        rules, total = annual_fee_service.get_user_annual_fee_rules(test_user.id)
        
        assert rules == []
        assert total == 0

    def test_pagination_edge_cases(self, annual_fee_service: AnnualFeeService, 
                                  test_user: User, db_session: Session):
        """测试分页边界情况"""
        # 测试页码为0的情况
        db_session.query.return_value.join.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []
        db_session.query.return_value.join.return_value.filter.return_value.count.return_value = 0
        
        rules, total = annual_fee_service.get_user_annual_fee_rules(test_user.id, page=0, page_size=10)
        
        assert rules == []
        assert total == 0


# ========== 性能测试 ==========

class TestAnnualFeeServicePerformance:
    """年费服务性能测试"""

    def test_large_rules_list_performance(self, annual_fee_service: AnnualFeeService, 
                                         test_user: User, db_session: Session):
        """测试大量规则列表性能"""
        # 模拟大量规则
        mock_rules = [Mock(id=uuid4()) for _ in range(1000)]
        
        db_session.query.return_value.join.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = mock_rules[:20]
        db_session.query.return_value.join.return_value.filter.return_value.count.return_value = 1000
        
        with patch.object(annual_fee_service, '_to_rule_response') as mock_response:
            mock_response.return_value = Mock()
            
            rules, total = annual_fee_service.get_user_annual_fee_rules(test_user.id, page=1, page_size=20)
            
            assert len(rules) == 20
            assert total == 1000

    def test_statistics_calculation_performance(self, annual_fee_service: AnnualFeeService, 
                                               test_user: User, db_session: Session):
        """测试统计计算性能"""
        # 模拟复杂统计查询
        mock_stats = Mock()
        mock_stats.total_cards_with_fee = 100
        mock_stats.total_base_fee = Decimal("30000.00")
        mock_stats.total_actual_fee = Decimal("15000.00")
        mock_stats.total_waived_amount = Decimal("15000.00")
        
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = mock_stats
        db_session.query.return_value.join.return_value.filter.return_value.group_by.return_value.all.return_value = []
        
        result = annual_fee_service.get_annual_fee_statistics(test_user.id, 2024)
        
        assert result.total_cards_with_fee == 100
        assert result.total_base_fee == Decimal("30000.00")


# ========== 数据完整性测试 ==========

class TestAnnualFeeServiceDataIntegrity:
    """年费服务数据完整性测试"""

    def test_rule_record_relationship_integrity(self, annual_fee_service: AnnualFeeService, 
                                               test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试规则和记录关系完整性"""
        # 确保规则和记录的关联关系正确
        assert test_rule.id is not None
        
        record_data = AnnualFeeRecordCreate(
            waiver_rule_id=test_rule.id,
            fee_year=2024,
            base_fee=Decimal("300.00"),
            actual_fee=Decimal("0.00"),
            waiver_amount=Decimal("300.00")
        )
        
        assert record_data.waiver_rule_id == test_rule.id

    def test_waiver_calculation_accuracy(self, annual_fee_service: AnnualFeeService, 
                                        test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试减免计算准确性"""
        # 模拟查询规则
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        
        # 模拟精确的交易金额
        mock_transactions = [
            Mock(amount=Decimal("25000.00")),
            Mock(amount=Decimal("25000.01"))  # 刚好超过减免条件
        ]
        db_session.query.return_value.filter.return_value.all.return_value = mock_transactions
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, test_rule.id)
        
        # 验证计算精度
        assert result.current_progress == 50000.01
        assert result.is_eligible is True
        assert result.completion_percentage > 100.0

    def test_decimal_precision_handling(self, annual_fee_service: AnnualFeeService, 
                                       test_user: User, test_card: CreditCard, db_session: Session):
        """测试Decimal精度处理"""
        db_session.query.return_value.filter.return_value.first.return_value = test_card
        db_session.query.return_value.filter.return_value.first.side_effect = [test_card, None]
        
        # 使用高精度Decimal值
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            rule_name="高精度减免规则",
            condition_type="spending_amount",
            condition_value=Decimal("50000.123456")
        )
        
        with patch.object(annual_fee_service, '_to_rule_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.create_fee_waiver_rule(test_user.id, rule_data)
            assert result is not None 