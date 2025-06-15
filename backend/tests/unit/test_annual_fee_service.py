#!/usr/bin/env python3
"""
年费服务单元测试 - 直连测试数据库

测试年费规则和年费记录的CRUD操作、减免评估、统计分析等功能
"""

import pytest
import uuid
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.services.annual_fee_service import AnnualFeeService
from app.models.database.user import User
from app.models.database.card import Bank, CreditCard
from app.models.database.transaction import TransactionCategory, Transaction
from app.models.database.fee_waiver import FeeWaiverRule, AnnualFeeRecord
from app.models.schemas.fee_waiver import (
    FeeWaiverRuleCreate, FeeWaiverRuleUpdate, 
    AnnualFeeRecordCreate, AnnualFeeRecordUpdate
)
from app.core.exceptions.custom import ResourceNotFoundError, BusinessRuleError
from tests.utils.db import create_test_session


# ========== 测试Fixtures ==========

@pytest.fixture
def db_session():
    """测试数据库会话"""
    session = create_test_session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def annual_fee_service(db_session: Session):
    """年费服务实例"""
    return AnnualFeeService(db_session)


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
def test_card(db_session: Session, test_user: User, test_bank: Bank):
    """创建测试信用卡"""
    timestamp = str(uuid.uuid4())[:8]
    card = CreditCard(
        user_id=test_user.id,
        bank_id=test_bank.id,
        card_number=f"6225{timestamp}1234",
        card_name=f"测试信用卡{timestamp}",
        card_type="credit",
        credit_limit=Decimal("50000.00"),
        available_limit=Decimal("50000.00"),
        used_limit=Decimal("0.00"),
        expiry_month=12,
        expiry_year=2027,
        status="active"
    )
    db_session.add(card)
    db_session.commit()
    db_session.refresh(card)
    return card


@pytest.fixture
def test_category(db_session: Session):
    """创建测试消费类别"""
    timestamp = str(uuid.uuid4())[:8]
    category = TransactionCategory(
        name=f"餐饮{timestamp}",
        icon="restaurant",
        color="#FF6B6B",
        is_active=True
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_rule(db_session: Session, test_card: CreditCard):
    """创建测试年费规则"""
    timestamp = str(uuid.uuid4())[:8]
    rule = FeeWaiverRule(
        card_id=test_card.id,
        rule_name=f"年消费满5万免年费{timestamp}",
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
    db_session.add(rule)
    db_session.commit()
    db_session.refresh(rule)
    return rule


@pytest.fixture
def test_record(db_session: Session, test_rule: FeeWaiverRule):
    """创建测试年费记录"""
    record = AnnualFeeRecord(
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
    db_session.add(record)
    db_session.commit()
    db_session.refresh(record)
    return record


# ========== 年费规则CRUD测试 ==========

class TestFeeWaiverRuleCRUD:
    """年费规则CRUD操作测试"""

    def test_create_annual_fee_rule_success(self, annual_fee_service: AnnualFeeService, 
                                          test_user: User, test_card: CreditCard):
        """测试创建年费规则成功"""
        timestamp = str(uuid.uuid4())[:8]
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            rule_name=f"年消费满5万免年费{timestamp}",
            condition_type="spending_amount",
            condition_value=Decimal("50000.00"),
            condition_period="yearly",
            is_enabled=True,
            effective_from=date(2024, 1, 1),
            effective_to=date(2024, 12, 31),
            description="年消费满5万免年费"
        )
        
        result = annual_fee_service.create_fee_waiver_rule(test_user.id, rule_data)
        
        assert result is not None
        assert result.rule_name == rule_data.rule_name
        assert result.condition_type == "spending_amount"
        assert result.condition_value == Decimal("50000.00")

    def test_create_annual_fee_rule_card_not_found(self, annual_fee_service: AnnualFeeService, 
                                                  test_user: User):
        """测试创建年费规则时信用卡不存在"""
        rule_data = FeeWaiverRuleCreate(
            card_id=uuid.uuid4(),
            rule_name="年消费满5万免年费",
            condition_type="spending_amount",
            condition_value=Decimal("50000.00")
        )
        
        with pytest.raises(ResourceNotFoundError, match="信用卡不存在或不属于当前用户"):
            annual_fee_service.create_fee_waiver_rule(test_user.id, rule_data)

    def test_create_annual_fee_rule_duplicate_name(self, annual_fee_service: AnnualFeeService, 
                                                  test_user: User, test_card: CreditCard, 
                                                  test_rule: FeeWaiverRule):
        """测试创建年费规则时规则名重复"""
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            rule_name=test_rule.rule_name,  # 使用相同的规则名
            condition_type="spending_amount",
            condition_value=Decimal("50000.00")
        )
        
        with pytest.raises(BusinessRuleError, match="年费规则已存在"):
            annual_fee_service.create_fee_waiver_rule(test_user.id, rule_data)

    def test_get_annual_fee_rule_success(self, annual_fee_service: AnnualFeeService, 
                                        test_user: User, test_rule: FeeWaiverRule):
        """测试获取年费规则成功"""
        result = annual_fee_service.get_annual_fee_rule(test_user.id, test_rule.id)
        
        assert result is not None
        assert result.id == test_rule.id
        assert result.rule_name == test_rule.rule_name

    def test_get_annual_fee_rule_not_found(self, annual_fee_service: AnnualFeeService, 
                                          test_user: User):
        """测试获取不存在的年费规则"""
        with pytest.raises(ResourceNotFoundError, match="年费规则不存在"):
            annual_fee_service.get_annual_fee_rule(test_user.id, uuid.uuid4())

    def test_update_annual_fee_rule_success(self, annual_fee_service: AnnualFeeService, 
                                           test_user: User, test_rule: FeeWaiverRule):
        """测试更新年费规则成功"""
        update_data = FeeWaiverRuleUpdate(
            condition_value=Decimal("60000.00"),
            description="调整为年消费满6万免年费"
        )
        
        result = annual_fee_service.update_annual_fee_rule(test_user.id, test_rule.id, update_data)
        
        assert result is not None
        assert result.condition_value == Decimal("60000.00")
        assert result.description == "调整为年消费满6万免年费"

    def test_delete_annual_fee_rule_success(self, annual_fee_service: AnnualFeeService, 
                                           test_user: User, test_rule: FeeWaiverRule):
        """测试删除年费规则成功"""
        result = annual_fee_service.delete_annual_fee_rule(test_user.id, test_rule.id)
        
        assert result is True

    def test_delete_annual_fee_rule_with_records(self, annual_fee_service: AnnualFeeService, 
                                                test_user: User, test_rule: FeeWaiverRule, 
                                                test_record: AnnualFeeRecord):
        """测试删除有关联记录的年费规则"""
        with pytest.raises(BusinessRuleError, match="存在关联的年费记录"):
            annual_fee_service.delete_annual_fee_rule(test_user.id, test_rule.id)


# ========== 年费记录CRUD测试 ==========

class TestAnnualFeeRecordCRUD:
    """年费记录CRUD操作测试"""

    def test_create_annual_fee_record_success(self, annual_fee_service: AnnualFeeService, 
                                             test_user: User, test_rule: FeeWaiverRule):
        """测试创建年费记录成功"""
        record_data = AnnualFeeRecordCreate(
            waiver_rule_id=test_rule.id,
            fee_year=2025,  # 使用不同年份避免冲突
            base_fee=Decimal("300.00"),
            actual_fee=Decimal("0.00"),
            waiver_amount=Decimal("300.00"),
            waiver_reason="测试减免",
            status="waived"
        )
        
        result = annual_fee_service.create_annual_fee_record(test_user.id, record_data)
        
        assert result is not None
        assert result.fee_year == 2025
        assert result.base_fee == Decimal("300.00")
        assert result.status == "waived"

    def test_get_annual_fee_record_success(self, annual_fee_service: AnnualFeeService, 
                                          test_user: User, test_record: AnnualFeeRecord):
        """测试获取年费记录成功"""
        result = annual_fee_service.get_annual_fee_record(test_user.id, test_record.id)
        
        assert result is not None
        assert result.id == test_record.id
        assert result.fee_year == test_record.fee_year

    def test_update_annual_fee_record_success(self, annual_fee_service: AnnualFeeService, 
                                             test_user: User, test_record: AnnualFeeRecord):
        """测试更新年费记录成功"""
        update_data = AnnualFeeRecordUpdate(
            actual_fee=Decimal("300.00"),
            status="paid",
            paid_date=date(2024, 1, 15),
            notes="已缴费"
        )
        
        result = annual_fee_service.update_annual_fee_record(test_user.id, test_record.id, update_data)
        
        assert result is not None
        assert result.actual_fee == Decimal("300.00")
        assert result.status == "paid"
        assert result.notes == "已缴费"


# ========== 年费减免评估测试 ==========

class TestWaiverEvaluation:
    """年费减免评估测试"""

    def test_evaluate_spending_amount_waiver_eligible(self, annual_fee_service: AnnualFeeService, 
                                                     test_user: User, test_rule: FeeWaiverRule, 
                                                     test_card: CreditCard, test_category: TransactionCategory,
                                                     db_session: Session):
        """测试消费金额减免评估 - 符合条件"""
        # 创建足够的交易记录
        transactions = [
            Transaction(
                user_id=test_user.id,
                card_id=test_card.id,
                category_id=test_category.id,
                transaction_type="expense",
                amount=Decimal("30000.00"),
                description="大额消费1",
                transaction_date=datetime(2024, 6, 1)
            ),
            Transaction(
                user_id=test_user.id,
                card_id=test_card.id,
                category_id=test_category.id,
                transaction_type="expense",
                amount=Decimal("25000.00"),
                description="大额消费2",
                transaction_date=datetime(2024, 8, 1)
            )
        ]
        
        for transaction in transactions:
            db_session.add(transaction)
        db_session.commit()
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, test_rule.id)
        
        assert result.is_eligible is True
        assert result.current_progress == 55000.00
        assert result.required_target == 50000.00
        assert result.completion_percentage == 110.0

    def test_evaluate_spending_amount_waiver_not_eligible(self, annual_fee_service: AnnualFeeService, 
                                                         test_user: User, test_rule: FeeWaiverRule,
                                                         test_card: CreditCard, test_category: TransactionCategory,
                                                         db_session: Session):
        """测试消费金额减免评估 - 不符合条件"""
        # 创建不足的交易记录
        transactions = [
            Transaction(
                user_id=test_user.id,
                card_id=test_card.id,
                category_id=test_category.id,
                transaction_type="expense",
                amount=Decimal("20000.00"),
                description="消费1",
                transaction_date=datetime(2024, 6, 1)
            ),
            Transaction(
                user_id=test_user.id,
                card_id=test_card.id,
                category_id=test_category.id,
                transaction_type="expense",
                amount=Decimal("15000.00"),
                description="消费2",
                transaction_date=datetime(2024, 8, 1)
            )
        ]
        
        for transaction in transactions:
            db_session.add(transaction)
        db_session.commit()
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, test_rule.id)
        
        assert result.is_eligible is False
        assert result.current_progress == 35000.00
        assert result.required_target == 50000.00
        assert result.completion_percentage == 70.0

    def test_evaluate_transaction_count_waiver(self, annual_fee_service: AnnualFeeService, 
                                              test_user: User, test_card: CreditCard, 
                                              test_category: TransactionCategory, db_session: Session):
        """测试交易次数减免评估"""
        # 创建交易次数类型的规则
        timestamp = str(uuid.uuid4())[:8]
        rule = FeeWaiverRule(
            card_id=test_card.id,
            rule_name=f"年交易12次免年费{timestamp}",
            condition_type="transaction_count",
            condition_value=None,
            condition_count=12,
            condition_period="yearly",
            logical_operator=None,
            priority=1,
            is_enabled=True,
            effective_from=date(2024, 1, 1),
            effective_to=date(2024, 12, 31),
            description="年交易12次免年费"
        )
        db_session.add(rule)
        db_session.commit()
        db_session.refresh(rule)
        
        # 创建15笔交易
        for i in range(15):
            transaction = Transaction(
                user_id=test_user.id,
                card_id=test_card.id,
                category_id=test_category.id,
                transaction_type="expense",
                amount=Decimal("100.00"),
                description=f"交易{i+1}",
                transaction_date=datetime(2024, 6, i+1)
            )
            db_session.add(transaction)
        db_session.commit()
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, rule.id)
        
        assert result.is_eligible is True
        assert result.current_progress == 15
        assert result.required_target == 12

    def test_evaluate_rigid_waiver(self, annual_fee_service: AnnualFeeService, 
                                  test_user: User, test_card: CreditCard, db_session: Session):
        """测试刚性年费评估"""
        # 创建刚性年费规则
        timestamp = str(uuid.uuid4())[:8]
        rule = FeeWaiverRule(
            card_id=test_card.id,
            rule_name=f"刚性年费{timestamp}",
            condition_type="rigid",
            condition_value=None,
            condition_count=None,
            condition_period="yearly",
            logical_operator=None,
            priority=1,
            is_enabled=True,
            effective_from=date(2024, 1, 1),
            effective_to=date(2024, 12, 31),
            description="刚性年费，无法减免"
        )
        db_session.add(rule)
        db_session.commit()
        db_session.refresh(rule)
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, rule.id)
        
        assert result.is_eligible is False
        assert result.current_progress == 0
        assert result.required_target == 0
        assert result.completion_percentage == 0.0
        assert "刚性年费，无法减免" in result.evaluation_message


# ========== 年费统计测试 ==========

class TestAnnualFeeStatistics:
    """年费统计测试"""

    def test_get_annual_fee_statistics_success(self, annual_fee_service: AnnualFeeService, 
                                              test_user: User, test_record: AnnualFeeRecord):
        """测试获取年费统计成功"""
        result = annual_fee_service.get_annual_fee_statistics(test_user.id, 2024)
        
        assert result is not None
        assert result.year == 2024
        assert result.total_cards_with_fee >= 1
        assert result.total_base_fee >= Decimal("300.00")

    def test_get_user_annual_fee_rules_pagination(self, annual_fee_service: AnnualFeeService, 
                                                 test_user: User, test_rule: FeeWaiverRule):
        """测试获取用户年费规则分页"""
        rules, total = annual_fee_service.get_user_annual_fee_rules(test_user.id, page=1, page_size=10)
        
        assert isinstance(rules, list)
        assert total >= 1
        assert len(rules) >= 1


# ========== 错误处理测试 ==========

class TestAnnualFeeServiceErrorHandling:
    """年费服务错误处理测试"""

    def test_get_rule_not_found(self, annual_fee_service: AnnualFeeService, test_user: User):
        """测试获取不存在的规则"""
        with pytest.raises(ResourceNotFoundError):
            annual_fee_service.get_annual_fee_rule(test_user.id, uuid.uuid4())

    def test_get_record_not_found(self, annual_fee_service: AnnualFeeService, test_user: User):
        """测试获取不存在的记录"""
        with pytest.raises(ResourceNotFoundError):
            annual_fee_service.get_annual_fee_record(test_user.id, uuid.uuid4())

    def test_evaluate_rule_not_found(self, annual_fee_service: AnnualFeeService, test_user: User):
        """测试评估不存在的规则"""
        with pytest.raises(ResourceNotFoundError):
            annual_fee_service.evaluate_waiver_eligibility(test_user.id, uuid.uuid4())


# ========== 边界情况测试 ==========

class TestAnnualFeeServiceEdgeCases:
    """年费服务边界情况测试"""

    def test_zero_base_fee_rule(self, annual_fee_service: AnnualFeeService, 
                               test_user: User, test_card: CreditCard):
        """测试零年费规则"""
        timestamp = str(uuid.uuid4())[:8]
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            rule_name=f"免年费卡{timestamp}",
            condition_type="rigid",
            condition_value=Decimal("0.00")
        )
        
        result = annual_fee_service.create_fee_waiver_rule(test_user.id, rule_data)
        assert result is not None
        assert result.condition_value == Decimal("0.00")

    def test_future_year_rule(self, annual_fee_service: AnnualFeeService, 
                             test_user: User, test_card: CreditCard):
        """测试未来年份规则"""
        future_year = datetime.now().year + 1
        timestamp = str(uuid.uuid4())[:8]
        
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            rule_name=f"未来年费规则{timestamp}",
            condition_type="spending_amount",
            condition_value=Decimal("50000.00"),
            effective_from=date(future_year, 1, 1),
            effective_to=date(future_year, 12, 31)
        )
        
        result = annual_fee_service.create_fee_waiver_rule(test_user.id, rule_data)
        assert result is not None
        assert result.effective_from.year == future_year

    def test_large_waiver_condition_value(self, annual_fee_service: AnnualFeeService, 
                                         test_user: User, test_card: CreditCard):
        """测试大额减免条件值"""
        timestamp = str(uuid.uuid4())[:8]
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            rule_name=f"高额消费减免{timestamp}",
            condition_type="spending_amount",
            condition_value=Decimal("1000000.00")
        )
        
        result = annual_fee_service.create_fee_waiver_rule(test_user.id, rule_data)
        assert result is not None
        assert result.condition_value == Decimal("1000000.00")

    def test_empty_user_rules_list(self, annual_fee_service: AnnualFeeService, db_session: Session):
        """测试用户无年费规则的情况"""
        # 创建一个新用户，没有任何规则
        timestamp = str(uuid.uuid4())[:8]
        user = User(
            username=f"emptyuser_{timestamp}",
            email=f"emptyuser_{timestamp}@example.com",
            password_hash="hashed_password",
            nickname="空用户"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        rules, total = annual_fee_service.get_user_annual_fee_rules(user.id)
        
        assert rules == []
        assert total == 0


# ========== 数据完整性测试 ==========

class TestAnnualFeeServiceDataIntegrity:
    """年费服务数据完整性测试"""

    def test_rule_record_relationship_integrity(self, annual_fee_service: AnnualFeeService, 
                                               test_user: User, test_rule: FeeWaiverRule):
        """测试规则和记录关系完整性"""
        record_data = AnnualFeeRecordCreate(
            waiver_rule_id=test_rule.id,
            fee_year=2025,
            base_fee=Decimal("300.00"),
            actual_fee=Decimal("0.00"),
            waiver_amount=Decimal("300.00")
        )
        
        result = annual_fee_service.create_annual_fee_record(test_user.id, record_data)
        
        assert result.waiver_rule_id == test_rule.id
        assert result.card_id == test_rule.card_id

    def test_waiver_calculation_accuracy(self, annual_fee_service: AnnualFeeService, 
                                        test_user: User, test_rule: FeeWaiverRule,
                                        test_card: CreditCard, test_category: TransactionCategory,
                                        db_session: Session):
        """测试减免计算准确性"""
        # 创建精确的交易金额
        transactions = [
            Transaction(
                user_id=test_user.id,
                card_id=test_card.id,
                category_id=test_category.id,
                transaction_type="expense",
                amount=Decimal("25000.00"),
                description="精确消费1",
                transaction_date=datetime(2024, 6, 1)
            ),
            Transaction(
                user_id=test_user.id,
                card_id=test_card.id,
                category_id=test_category.id,
                transaction_type="expense",
                amount=Decimal("25000.01"),  # 刚好超过减免条件
                description="精确消费2",
                transaction_date=datetime(2024, 8, 1)
            )
        ]
        
        for transaction in transactions:
            db_session.add(transaction)
        db_session.commit()
        
        result = annual_fee_service.evaluate_waiver_eligibility(test_user.id, test_rule.id)
        
        # 验证计算精度
        assert result.current_progress == 50000.01
        assert result.is_eligible is True
        assert result.completion_percentage > 100.0

    def test_decimal_precision_handling(self, annual_fee_service: AnnualFeeService,
                                       test_user: User, test_card: CreditCard):
        """测试Decimal精度处理"""
        timestamp = str(uuid.uuid4())[:8]
        # 使用高精度Decimal值，但期望值应该匹配数据库的Numeric(15,2)精度
        rule_data = FeeWaiverRuleCreate(
            card_id=test_card.id,
            rule_name=f"高精度减免规则{timestamp}",
            condition_type="spending_amount",
            condition_value=Decimal("50000.123456")
        )

        result = annual_fee_service.create_fee_waiver_rule(test_user.id, rule_data)
        assert result is not None
        # 数据库字段定义为Numeric(15,2)，所以只保留2位小数
        assert result.condition_value == Decimal("50000.12") 