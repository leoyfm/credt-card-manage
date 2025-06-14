"""
年费服务单元测试

测试年费规则和年费记录的管理功能，包括CRUD操作、减免评估、统计分析等
"""
import pytest
from decimal import Decimal
from datetime import datetime, date, timedelta
from uuid import UUID, uuid4
from unittest.mock import Mock, patch, call
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError as PydanticValidationError

from app.services.annual_fee_service import AnnualFeeService
from app.models.database.user import User
from app.models.database.card import CreditCard, Bank
from app.models.database.fee_waiver import FeeWaiverRule, AnnualFeeRecord
from app.models.database.transaction import Transaction, TransactionCategory
from app.models.schemas.fee_waiver import (
    FeeWaiverRuleCreate, FeeWaiverRuleUpdate, AnnualFeeRecordCreate, AnnualFeeRecordUpdate
)
from app.core.exceptions.custom import (
    ResourceNotFoundError, ValidationError, BusinessRuleError
)
from app.core.logging.logger import StructuredLogger


# ========== Fixtures ==========

@pytest.fixture
def db_session():
    """数据库会话fixture"""
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
        is_active=True
    )


@pytest.fixture
def test_bank(db_session: Session):
    """测试银行fixture"""
    unique_id = str(uuid4()).replace('-', '')[:8].upper()
    bank = Bank(
        bank_code=f"TEST{unique_id}",
        bank_name=f"测试银行{unique_id}",
        is_active=True,
        sort_order=1
    )
    return bank


@pytest.fixture
def test_card(test_user: User, test_bank: Bank):
    """测试信用卡fixture"""
    return CreditCard(
        id=uuid4(),
        user_id=test_user.id,
        bank_id=test_bank.id,
        card_name="测试信用卡",
        card_number="1234****5678",  # 修正字段名
        expiry_month=12,
        expiry_year=2027,
        credit_limit=Decimal("50000.00"),
        available_limit=Decimal("45000.00"),
        status="active"  # 修正字段名
    )


@pytest.fixture
def test_category():
    """测试交易分类fixture"""
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
        fee_year=2024,
        base_fee=Decimal("300.00"),
        waiver_type="spending_amount",
        waiver_condition_value=Decimal("50000.00"),
        waiver_condition_unit="元",
        points_per_yuan=Decimal("1.00"),
        is_active=True,
        notes="年消费满5万免年费"
    )


@pytest.fixture
def test_record(test_rule: FeeWaiverRule):
    """测试年费记录fixture"""
    return AnnualFeeRecord(
        id=uuid4(),
        waiver_rule_id=test_rule.id,
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
            fee_year=2024,
            base_fee=Decimal("300.00"),
            waiver_type="spending_amount",
            waiver_condition_value=Decimal("50000.00"),
            waiver_condition_unit="元",
            points_per_yuan=Decimal("1.00"),
            is_active=True,
            notes="年消费满5万免年费"
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
            
            result = annual_fee_service.create_annual_fee_rule(test_user.id, rule_data)
            
            assert result is not None
            db_session.add.assert_called_once()
            db_session.commit.assert_called_once()

    def test_create_annual_fee_rule_card_not_found(self, annual_fee_service: AnnualFeeService, 
                                                  test_user: User, db_session: Session):
        """测试创建年费规则时信用卡不存在"""
        db_session.query.return_value.filter.return_value.first.return_value = None
        
        rule_data = FeeWaiverRuleCreate(
            card_id=uuid4(),
            fee_year=2024,
            base_fee=Decimal("300.00"),
            waiver_type="spending_amount",
            waiver_condition_value=Decimal("50000.00")
        )
        
        with pytest.raises(ResourceNotFoundError, match="信用卡不存在或不属于当前用户"):
            annual_fee_service.create_annual_fee_rule(test_user.id, rule_data)

    def test_create_annual_fee_rule_duplicate_year(self, annual_fee_service: AnnualFeeService, 
                                                  test_user: User, test_card: CreditCard, 
                                                  test_rule: FeeWaiverRule, db_session: Session):
        """测试创建年费规则时年份重复"""
        db_session.query.return_value.filter.return_value.first.side_effect = [test_card, test_rule]
        
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            fee_year=2024,
            base_fee=Decimal("300.00"),
            waiver_type="spending_amount",
            waiver_condition_value=Decimal("50000.00")
        )
        
        with pytest.raises(BusinessRuleError, match="年费规则已存在"):
            annual_fee_service.create_annual_fee_rule(test_user.id, rule_data)

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
            base_fee=Decimal("400.00"),
            notes="调整年费金额"
        )
        
        with patch.object(annual_fee_service, '_to_rule_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.update_annual_fee_rule(test_user.id, test_rule.id, update_data)
            
            assert result is not None
            assert test_rule.base_fee == Decimal("400.00")
            assert test_rule.notes == "调整年费金额"
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
        
        created_record = AnnualFeeRecord(**record_data.model_dump())
        created_record.id = uuid4()
        created_record.created_at = datetime.now()
        created_record.updated_at = datetime.now()
        
        with patch.object(annual_fee_service, '_to_record_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.create_annual_fee_record(test_user.id, record_data)
            
            assert result is not None
            db_session.add.assert_called_once()
            db_session.commit.assert_called_once()

    def test_get_annual_fee_record_success(self, annual_fee_service: AnnualFeeService, 
                                          test_user: User, test_record: AnnualFeeRecord, db_session: Session):
        """测试获取年费记录成功"""
        db_session.query.return_value.join.return_value.join.return_value.filter.return_value.first.return_value = test_record
        
        with patch.object(annual_fee_service, '_to_record_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.get_annual_fee_record(test_user.id, test_record.id)
            
            assert result is not None
            mock_response.assert_called_once_with(test_record)

    def test_update_annual_fee_record_success(self, annual_fee_service: AnnualFeeService, 
                                             test_user: User, test_record: AnnualFeeRecord, db_session: Session):
        """测试更新年费记录成功"""
        db_session.query.return_value.join.return_value.join.return_value.filter.return_value.first.return_value = test_record
        
        update_data = AnnualFeeRecordUpdate(
            status="paid",
            paid_date=date(2024, 1, 15),
            notes="已缴费"
        )
        
        with patch.object(annual_fee_service, '_to_record_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.update_annual_fee_record(test_user.id, test_record.id, update_data)
            
            assert result is not None
            assert test_record.status == "paid"
            assert test_record.paid_date == date(2024, 1, 15)
            db_session.commit.assert_called_once()


# ========== 减免评估测试 ==========

class TestWaiverEvaluation:
    """年费减免评估测试"""

    def test_evaluate_spending_amount_waiver_eligible(self, annual_fee_service: AnnualFeeService, 
                                                     test_user: User, test_rule: FeeWaiverRule, 
                                                     test_card: CreditCard, db_session: Session):
        """测试消费金额减免评估 - 符合条件"""
        # 设置规则为消费金额减免
        test_rule.waiver_type = "spending_amount"
        test_rule.waiver_condition_value = Decimal("50000.00")
        
        # 创建模拟交易
        mock_transaction1 = Mock()
        mock_transaction1.amount = Decimal("30000.00")
        mock_transaction2 = Mock()
        mock_transaction2.amount = Decimal("25000.00")
        mock_transactions = [mock_transaction1, mock_transaction2]
        
        # 配置数据库查询模拟
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        db_session.query.return_value.filter.return_value.all.return_value = mock_transactions
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, test_rule.id)
        
        assert result.is_eligible is True
        assert result.current_progress == 55000.00
        assert result.required_target == 50000.00
        assert result.completion_percentage == 100.0  # 服务中限制最大为100%
        assert result.estimated_waiver_amount == test_rule.base_fee

    def test_evaluate_spending_amount_waiver_not_eligible(self, annual_fee_service: AnnualFeeService, 
                                                         test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试消费金额减免评估 - 不符合条件"""
        test_rule.waiver_type = "spending_amount"
        test_rule.waiver_condition_value = Decimal("50000.00")
        
        # 创建模拟交易 - 总额不足
        mock_transaction = Mock()
        mock_transaction.amount = Decimal("30000.00")
        mock_transactions = [mock_transaction]
        
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        db_session.query.return_value.filter.return_value.all.return_value = mock_transactions
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, test_rule.id)
        
        assert result.is_eligible is False
        assert result.current_progress == 30000.00
        assert result.completion_percentage == 60.0
        assert result.estimated_waiver_amount == Decimal("0")

    def test_evaluate_transaction_count_waiver(self, annual_fee_service: AnnualFeeService, 
                                              test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试交易次数减免评估"""
        test_rule.waiver_type = "transaction_count"
        test_rule.waiver_condition_value = Decimal("12")  # 12次交易
        
        # 创建15个模拟交易
        mock_transactions = [Mock() for _ in range(15)]
        
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        db_session.query.return_value.filter.return_value.all.return_value = mock_transactions
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, test_rule.id)
        
        assert result.is_eligible is True
        assert result.current_progress == 15.0
        assert result.required_target == 12.0
        assert result.completion_percentage == 100.0  # 服务中限制最大为100%

    def test_evaluate_rigid_waiver(self, annual_fee_service: AnnualFeeService, 
                                  test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试刚性年费评估"""
        test_rule.waiver_type = "rigid"
        
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, test_rule.id)
        
        assert result.is_eligible is False
        assert result.current_progress == 0.0
        assert result.completion_percentage == 0.0
        assert result.estimated_waiver_amount == Decimal("0")


# ========== 年费统计测试 ==========

class TestAnnualFeeStatistics:
    """年费统计测试"""

    def test_get_annual_fee_statistics_success(self, annual_fee_service: AnnualFeeService, 
                                              test_user: User, db_session: Session):
        """测试获取年费统计成功"""
        # 创建模拟年费记录
        mock_rule1 = Mock()
        mock_rule1.waiver_type = "spending_amount"
        
        mock_rule2 = Mock()
        mock_rule2.waiver_type = "rigid"
        
        mock_record1 = Mock()
        mock_record1.base_fee = Decimal("300.00")
        mock_record1.actual_fee = Decimal("0.00")
        mock_record1.waiver_amount = Decimal("300.00")
        mock_record1.status = "waived"
        mock_record1.rule = mock_rule1
        
        mock_record2 = Mock()
        mock_record2.base_fee = Decimal("500.00")
        mock_record2.actual_fee = Decimal("500.00")
        mock_record2.waiver_amount = Decimal("0.00")
        mock_record2.status = "paid"
        mock_record2.rule = mock_rule2
        
        mock_records = [mock_record1, mock_record2]
        
        # 配置数据库查询模拟
        db_session.query.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = mock_records
        
        result = annual_fee_service.get_annual_fee_statistics(test_user.id, 2024)
        
        assert result.year == 2024
        assert result.total_cards_with_fee == 2
        assert result.total_base_fee == Decimal("800.00")
        assert result.total_actual_fee == Decimal("500.00")
        assert result.total_waived_amount == Decimal("300.00")
        assert result.waiver_rate == Decimal("37.5")  # 300/800 * 100


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
        with pytest.raises(PydanticValidationError):
            FeeWaiverRuleCreate(
                card_id=uuid4(),
                fee_year=2024,
                base_fee=Decimal("300.00"),
                waiver_type="invalid_type",  # 无效的减免类型
                waiver_condition_value=Decimal("50000.00")
            )


# ========== 边界情况测试 ==========

class TestAnnualFeeServiceEdgeCases:
    """年费服务边界情况测试"""

    def test_zero_base_fee_rule(self, annual_fee_service: AnnualFeeService, 
                               test_user: User, test_card: CreditCard, db_session: Session):
        """测试零年费规则"""
        db_session.query.return_value.filter.return_value.first.side_effect = [test_card, None]
        
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            fee_year=2024,
            base_fee=Decimal("0.00"),  # 零年费
            waiver_type="rigid"
        )
        
        with patch.object(annual_fee_service, '_to_rule_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.create_annual_fee_rule(test_user.id, rule_data)
            
            assert result is not None

    def test_future_year_rule(self, annual_fee_service: AnnualFeeService, 
                             test_user: User, test_card: CreditCard, db_session: Session):
        """测试未来年份的年费规则"""
        db_session.query.return_value.filter.return_value.first.side_effect = [test_card, None]
        
        future_year = datetime.now().year + 2
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            fee_year=future_year,
            base_fee=Decimal("300.00"),
            waiver_type="spending_amount",
            waiver_condition_value=Decimal("50000.00")
        )
        
        with patch.object(annual_fee_service, '_to_rule_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.create_annual_fee_rule(test_user.id, rule_data)
            
            assert result is not None

    def test_large_waiver_condition_value(self, annual_fee_service: AnnualFeeService, 
                                         test_user: User, test_card: CreditCard, db_session: Session):
        """测试大额减免条件值"""
        db_session.query.return_value.filter.return_value.first.side_effect = [test_card, None]
        
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            fee_year=2024,
            base_fee=Decimal("300.00"),
            waiver_type="spending_amount",
            waiver_condition_value=Decimal("1000000.00")  # 100万
        )
        
        with patch.object(annual_fee_service, '_to_rule_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.create_annual_fee_rule(test_user.id, rule_data)
            
            assert result is not None

    def test_empty_user_rules_list(self, annual_fee_service: AnnualFeeService, 
                                  test_user: User, db_session: Session):
        """测试用户无年费规则的情况"""
        db_session.query.return_value.join.return_value.filter.return_value.count.return_value = 0
        db_session.query.return_value.join.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        
        rules, total = annual_fee_service.get_user_annual_fee_rules(test_user.id)
        
        assert rules == []
        assert total == 0

    def test_pagination_edge_cases(self, annual_fee_service: AnnualFeeService, 
                                  test_user: User, db_session: Session):
        """测试分页边界情况"""
        db_session.query.return_value.join.return_value.filter.return_value.count.return_value = 5
        db_session.query.return_value.join.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        
        # 测试超出范围的页码
        rules, total = annual_fee_service.get_user_annual_fee_rules(test_user.id, page=10, page_size=20)
        
        assert rules == []
        assert total == 5


# ========== 性能测试 ==========

class TestAnnualFeeServicePerformance:
    """年费服务性能测试"""

    def test_large_rules_list_performance(self, annual_fee_service: AnnualFeeService, 
                                         test_user: User, db_session: Session):
        """测试大量规则列表的性能"""
        # 模拟大量数据
        large_count = 1000
        db_session.query.return_value.join.return_value.filter.return_value.count.return_value = large_count
        db_session.query.return_value.join.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = []
        
        start_time = datetime.now()
        
        rules, total = annual_fee_service.get_user_annual_fee_rules(test_user.id, page=1, page_size=50)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 查询应该在合理时间内完成
        assert duration < 1  # 1秒内完成
        assert total == large_count

    def test_statistics_calculation_performance(self, annual_fee_service: AnnualFeeService, 
                                               test_user: User, db_session: Session):
        """测试统计计算性能"""
        # 模拟复杂统计查询
        db_session.query.return_value.join.return_value.join.return_value.filter.return_value.all.return_value = []
        
        start_time = datetime.now()
        
        result = annual_fee_service.get_annual_fee_statistics(test_user.id, 2024)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 统计计算应该在合理时间内完成
        assert duration < 2  # 2秒内完成
        assert result is not None


# ========== 数据完整性测试 ==========

class TestAnnualFeeServiceDataIntegrity:
    """年费服务数据完整性测试"""

    def test_rule_record_relationship_integrity(self, annual_fee_service: AnnualFeeService, 
                                               test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试规则和记录关系的完整性"""
        # 测试删除有关联记录的规则
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        db_session.query.return_value.filter.return_value.count.return_value = 1  # 有关联记录
        
        with pytest.raises(BusinessRuleError, match="存在关联的年费记录"):
            annual_fee_service.delete_annual_fee_rule(test_user.id, test_rule.id)

    def test_waiver_calculation_accuracy(self, annual_fee_service: AnnualFeeService, 
                                        test_user: User, test_rule: FeeWaiverRule, db_session: Session):
        """测试减免计算的准确性"""
        test_rule.waiver_type = "spending_amount"
        test_rule.waiver_condition_value = Decimal("50000.00")
        test_rule.base_fee = Decimal("300.00")
        
        # 创建模拟交易 - 总额60000
        mock_transaction1 = Mock()
        mock_transaction1.amount = Decimal("35000.00")
        mock_transaction2 = Mock()
        mock_transaction2.amount = Decimal("25000.00")
        mock_transactions = [mock_transaction1, mock_transaction2]
        
        db_session.query.return_value.join.return_value.filter.return_value.first.return_value = test_rule
        db_session.query.return_value.filter.return_value.all.return_value = mock_transactions
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, test_rule.id)
        
        # 验证计算准确性
        assert result.current_progress == 60000.00
        assert result.required_target == 50000.00
        assert result.completion_percentage == 100.0  # 服务中限制最大为100%
        assert result.estimated_waiver_amount == Decimal("300.00")
        assert result.is_eligible is True

    def test_decimal_precision_handling(self, annual_fee_service: AnnualFeeService, 
                                       test_user: User, test_card: CreditCard, db_session: Session):
        """测试小数精度处理"""
        db_session.query.return_value.filter.return_value.first.side_effect = [test_card, None]
        
        # 测试高精度小数
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            fee_year=2024,
            base_fee=Decimal("299.99"),
            waiver_type="spending_amount",
            waiver_condition_value=Decimal("49999.99"),
            points_per_yuan=Decimal("1.25")
        )
        
        with patch.object(annual_fee_service, '_to_rule_response') as mock_response:
            mock_response.return_value = Mock()
            
            result = annual_fee_service.create_annual_fee_rule(test_user.id, rule_data)
            
            assert result is not None
            # 验证精度保持
            call_args = db_session.add.call_args[0][0]
            assert call_args.base_fee == Decimal("299.99")
            assert call_args.waiver_condition_value == Decimal("49999.99")
            assert call_args.points_per_yuan == Decimal("1.25") 