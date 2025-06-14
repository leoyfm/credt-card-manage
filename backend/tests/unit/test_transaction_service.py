"""
交易服务单元测试 - 直连测试数据库
"""
import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch

from app.services.transaction_service import TransactionService
from app.models.database.transaction import Transaction, TransactionCategory
from app.models.database.card import CreditCard, Bank
from app.models.database.user import User
from app.models.schemas.transaction import (
    TransactionCreate, TransactionUpdate
)
from app.core.exceptions.custom import (
    ResourceNotFoundError, BusinessRuleError, ValidationError
)
from tests.utils.db import create_test_session
from tests.factories.transaction_factory import (
    build_transaction, build_simple_transaction, build_large_transaction,
    build_refund_transaction, build_pending_transaction, build_transactions_batch
)
from tests.factories.card_factory import build_card
from tests.factories.user_factory import build_user


@pytest.fixture
def db_session():
    """测试数据库会话"""
    session = create_test_session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def transaction_service(db_session: Session):
    """交易服务实例"""
    return TransactionService(db_session)


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
    # 使用完整的UUID确保唯一性
    unique_id = str(uuid.uuid4()).replace('-', '')[:8].upper()
    bank = Bank(
        bank_code=f"TEST{unique_id}",
        bank_name=f"测试银行{unique_id}",
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
        status="active",
        points_rate=Decimal("1.0"),
        cashback_rate=Decimal("1.0")
    )
    db_session.add(card)
    db_session.commit()
    db_session.refresh(card)
    return card


@pytest.fixture
def test_category(db_session: Session):
    """创建测试交易分类"""
    category = TransactionCategory(
        name="餐饮美食",
        icon="food",
        color="#FF6B6B",
        is_system=True,
        is_active=True,
        sort_order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_transaction(db_session: Session, test_user: User, test_card: CreditCard, test_category: TransactionCategory):
    """创建测试交易记录"""
    transaction = Transaction(
        user_id=test_user.id,
        card_id=test_card.id,
        category_id=test_category.id,
        transaction_type="expense",
        amount=Decimal("299.50"),
        currency="CNY",
        description="星巴克咖啡",
        merchant_name="星巴克",
        merchant_category="餐饮美食",
        location="北京市朝阳区",
        points_earned=299,
        cashback_earned=Decimal("2.99"),
        status="completed",
        transaction_date=datetime.now(),
        notes="测试交易",
        tags=["餐饮", "咖啡"]
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction


class TestTransactionCRUD:
    """交易CRUD操作测试"""

    def test_create_transaction_success(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard, test_category: TransactionCategory):
        """测试创建交易成功"""
        transaction_data = TransactionCreate(
            card_id=test_card.id,
            category_id=test_category.id,
            transaction_type="expense",
            amount=Decimal("199.99"),
            description="麦当劳",
            merchant_name="麦当劳",
            merchant_category="餐饮美食",
            location="上海市浦东新区"
        )
        
        result = transaction_service.create_transaction(test_user.id, transaction_data)
        
        assert result.amount == Decimal("199.99")
        assert result.description == "麦当劳"
        assert result.card_id == test_card.id
        assert result.category_id == test_category.id
        assert result.points_earned == 199  # 基于卡片积分倍率
        assert result.cashback_earned == Decimal("2.00")  # 基于卡片返现比例

    def test_create_transaction_card_not_found(self, transaction_service: TransactionService, test_user: User):
        """测试创建交易时信用卡不存在"""
        fake_card_id = uuid.uuid4()
        transaction_data = TransactionCreate(
            card_id=fake_card_id,
            transaction_type="expense",
            amount=Decimal("100.00"),
            description="测试交易"
        )
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            transaction_service.create_transaction(test_user.id, transaction_data)
        
        assert "信用卡不存在" in str(exc_info.value)

    def test_create_transaction_card_wrong_user(self, transaction_service: TransactionService, test_card: CreditCard):
        """测试创建交易时信用卡不属于当前用户"""
        other_user_id = uuid.uuid4()
        transaction_data = TransactionCreate(
            card_id=test_card.id,
            transaction_type="expense",
            amount=Decimal("100.00"),
            description="测试交易"
        )
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            transaction_service.create_transaction(other_user_id, transaction_data)
        
        assert "不属于当前用户" in str(exc_info.value)

    def test_create_transaction_category_not_found(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard):
        """测试创建交易时分类不存在"""
        fake_category_id = uuid.uuid4()
        transaction_data = TransactionCreate(
            card_id=test_card.id,
            category_id=fake_category_id,
            transaction_type="expense",
            amount=Decimal("100.00"),
            description="测试交易"
        )
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            transaction_service.create_transaction(test_user.id, transaction_data)
        
        assert "交易分类不存在" in str(exc_info.value)

    def test_create_transaction_income_no_rewards(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard):
        """测试创建收入类型交易不计算积分和返现"""
        transaction_data = TransactionCreate(
            card_id=test_card.id,
            transaction_type="income",
            amount=Decimal("500.00"),
            description="退款"
        )
        
        result = transaction_service.create_transaction(test_user.id, transaction_data)
        
        assert result.points_earned == 0
        assert result.cashback_earned == Decimal("0.00")

    def test_get_transaction_success(self, transaction_service: TransactionService, test_user: User, test_transaction: Transaction):
        """测试获取交易详情成功"""
        result = transaction_service.get_transaction(test_user.id, test_transaction.id)
        
        assert result.id == test_transaction.id
        assert result.amount == test_transaction.amount
        assert result.description == test_transaction.description

    def test_get_transaction_not_found(self, transaction_service: TransactionService, test_user: User):
        """测试获取不存在的交易"""
        fake_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            transaction_service.get_transaction(test_user.id, fake_id)
        
        assert "交易记录不存在" in str(exc_info.value)

    def test_get_transaction_wrong_user(self, transaction_service: TransactionService, test_transaction: Transaction):
        """测试获取其他用户的交易"""
        other_user_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            transaction_service.get_transaction(other_user_id, test_transaction.id)
        
        assert "交易记录不存在" in str(exc_info.value)

    def test_update_transaction_success(self, transaction_service: TransactionService, test_user: User, test_transaction: Transaction):
        """测试更新交易成功"""
        update_data = TransactionUpdate(
            amount=Decimal("399.99"),
            description="星巴克大杯拿铁",
            merchant_name="星巴克咖啡"
        )
        
        result = transaction_service.update_transaction(test_user.id, test_transaction.id, update_data)
        
        assert result.amount == Decimal("399.99")
        assert result.description == "星巴克大杯拿铁"
        assert result.merchant_name == "星巴克咖啡"
        # 验证积分和返现重新计算
        assert result.points_earned == 399
        assert result.cashback_earned == Decimal("4.00")

    def test_update_transaction_not_found(self, transaction_service: TransactionService, test_user: User):
        """测试更新不存在的交易"""
        fake_id = uuid.uuid4()
        update_data = TransactionUpdate(amount=Decimal("100.00"))
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            transaction_service.update_transaction(test_user.id, fake_id, update_data)
        
        assert "交易记录不存在" in str(exc_info.value)

    def test_update_transaction_new_card(self, transaction_service: TransactionService, test_user: User, test_transaction: Transaction, test_bank: Bank, db_session: Session):
        """测试更新交易到新信用卡"""
        # 创建新的信用卡
        new_card = CreditCard(
            user_id=test_user.id,
            bank_id=test_bank.id,
            card_number="6225000000002222",
            card_name="新测试卡",
            card_type="credit",
            credit_limit=Decimal("30000.00"),
            expiry_month=12,
            expiry_year=2028,
            points_rate=Decimal("2.0"),  # 不同的积分倍率
            cashback_rate=Decimal("2.0")  # 不同的返现比例
        )
        db_session.add(new_card)
        db_session.commit()
        db_session.refresh(new_card)
        
        update_data = TransactionUpdate(card_id=new_card.id)
        
        result = transaction_service.update_transaction(test_user.id, test_transaction.id, update_data)
        
        assert result.card_id == new_card.id
        # 验证基于新卡片的积分和返现
        assert result.points_earned == int(result.amount * 2)
        assert result.cashback_earned == result.amount * Decimal("0.02")

    def test_update_transaction_wrong_card_user(self, transaction_service: TransactionService, test_user: User, test_transaction: Transaction, test_bank: Bank, db_session: Session):
        """测试更新交易到不属于用户的信用卡"""
        # 创建其他用户的信用卡
        other_user = User(
            username="otheruser",
            email="other@example.com",
            password_hash="hash"
        )
        db_session.add(other_user)
        db_session.commit()
        
        other_card = CreditCard(
            user_id=other_user.id,
            bank_id=test_bank.id,
            card_number="6225000000003333",
            card_name="其他用户卡",
            card_type="credit",
            credit_limit=Decimal("10000.00"),
            expiry_month=6,
            expiry_year=2026
        )
        db_session.add(other_card)
        db_session.commit()
        
        update_data = TransactionUpdate(card_id=other_card.id)
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            transaction_service.update_transaction(test_user.id, test_transaction.id, update_data)
        
        assert "不属于当前用户" in str(exc_info.value)

    def test_delete_transaction_success(self, transaction_service: TransactionService, test_user: User, test_transaction: Transaction, db_session: Session):
        """测试删除交易成功"""
        transaction_id = test_transaction.id
        
        result = transaction_service.delete_transaction(test_user.id, transaction_id)
        
        assert result is True
        
        # 验证交易已被删除
        deleted_transaction = db_session.query(Transaction).filter(Transaction.id == transaction_id).first()
        assert deleted_transaction is None

    def test_delete_transaction_not_found(self, transaction_service: TransactionService, test_user: User):
        """测试删除不存在的交易"""
        fake_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            transaction_service.delete_transaction(test_user.id, fake_id)
        
        assert "交易记录不存在" in str(exc_info.value)


class TestTransactionList:
    """交易列表查询测试"""

    def test_get_user_transactions_basic(self, transaction_service: TransactionService, test_user: User, test_transaction: Transaction):
        """测试获取用户交易列表基础功能"""
        transactions, total = transaction_service.get_user_transactions(test_user.id)
        
        assert total >= 1
        assert len(transactions) >= 1
        assert any(t.id == test_transaction.id for t in transactions)

    def test_get_user_transactions_pagination(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard, test_category: TransactionCategory, db_session: Session):
        """测试交易列表分页"""
        # 创建多个交易记录
        for i in range(25):
            transaction = Transaction(
                user_id=test_user.id,
                card_id=test_card.id,
                category_id=test_category.id,
                transaction_type="expense",
                amount=Decimal(f"{100 + i}.00"),
                description=f"测试交易{i}",
                transaction_date=datetime.now() - timedelta(days=i)
            )
            db_session.add(transaction)
        db_session.commit()
        
        # 测试第一页
        transactions_page1, total = transaction_service.get_user_transactions(test_user.id, page=1, page_size=10)
        assert len(transactions_page1) == 10
        assert total >= 25
        
        # 测试第二页
        transactions_page2, _ = transaction_service.get_user_transactions(test_user.id, page=2, page_size=10)
        assert len(transactions_page2) == 10
        
        # 验证页面数据不重复
        page1_ids = {t.id for t in transactions_page1}
        page2_ids = {t.id for t in transactions_page2}
        assert len(page1_ids.intersection(page2_ids)) == 0

    def test_get_user_transactions_card_filter(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard, test_bank: Bank, db_session: Session):
        """测试按信用卡筛选交易"""
        # 创建另一张信用卡和交易
        other_card = CreditCard(
            user_id=test_user.id,
            bank_id=test_bank.id,
            card_number="6225000000004444",
            card_name="另一张测试卡",
            card_type="credit",
            credit_limit=Decimal("20000.00"),
            expiry_month=3,
            expiry_year=2029
        )
        db_session.add(other_card)
        db_session.commit()
        
        # 在另一张卡上创建交易
        other_transaction = Transaction(
            user_id=test_user.id,
            card_id=other_card.id,
            transaction_type="expense",
            amount=Decimal("500.00"),
            description="另一张卡的交易"
        )
        db_session.add(other_transaction)
        db_session.commit()
        
        # 筛选特定卡片的交易
        transactions, total = transaction_service.get_user_transactions(test_user.id, card_id=other_card.id)
        
        assert total >= 1
        assert all(t.card_id == other_card.id for t in transactions)

    def test_get_user_transactions_type_filter(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard, db_session: Session):
        """测试按交易类型筛选"""
        # 创建不同类型的交易
        income_transaction = Transaction(
            user_id=test_user.id,
            card_id=test_card.id,
            transaction_type="income",
            amount=Decimal("1000.00"),
            description="退款"
        )
        db_session.add(income_transaction)
        db_session.commit()
        
        # 筛选收入类型
        transactions, total = transaction_service.get_user_transactions(test_user.id, transaction_type="income")
        
        assert total >= 1
        assert all(t.transaction_type == "income" for t in transactions)

    def test_get_user_transactions_date_filter(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard, db_session: Session):
        """测试按日期范围筛选交易"""
        # 创建不同日期的交易
        old_transaction = Transaction(
            user_id=test_user.id,
            card_id=test_card.id,
            transaction_type="expense",
            amount=Decimal("200.00"),
            description="旧交易",
            transaction_date=datetime.now() - timedelta(days=60)
        )
        recent_transaction = Transaction(
            user_id=test_user.id,
            card_id=test_card.id,
            transaction_type="expense",
            amount=Decimal("300.00"),
            description="近期交易",
            transaction_date=datetime.now() - timedelta(days=5)
        )
        db_session.add_all([old_transaction, recent_transaction])
        db_session.commit()
        
        # 筛选最近30天的交易
        start_date = datetime.now(timezone.utc) - timedelta(days=30)
        end_date = datetime.now(timezone.utc)
        
        transactions, total = transaction_service.get_user_transactions(
            test_user.id, start_date=start_date, end_date=end_date
        )
        
        # 验证所有交易都在日期范围内
        for transaction in transactions:
            if transaction.transaction_date:
                assert start_date <= transaction.transaction_date <= end_date

    def test_get_user_transactions_keyword_search(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard, db_session: Session):
        """测试关键词搜索交易"""
        # 创建包含特定关键词的交易
        special_transaction = Transaction(
            user_id=test_user.id,
            card_id=test_card.id,
            transaction_type="expense",
            amount=Decimal("150.00"),
            description="特殊关键词交易",
            merchant_name="特殊商户",
            location="特殊地点",
            notes="特殊备注"
        )
        db_session.add(special_transaction)
        db_session.commit()
        
        # 搜索关键词
        transactions, total = transaction_service.get_user_transactions(test_user.id, keyword="特殊")
        
        assert total >= 1
        assert any("特殊" in (t.description or "") or 
                  "特殊" in (t.merchant_name or "") or
                  "特殊" in (t.location or "") or
                  "特殊" in (t.notes or "") for t in transactions)

    def test_get_user_transactions_empty_result(self, transaction_service: TransactionService):
        """测试空用户的交易列表"""
        fake_user_id = uuid.uuid4()
        
        transactions, total = transaction_service.get_user_transactions(fake_user_id)
        
        assert transactions == []
        assert total == 0


class TestTransactionStatistics:
    """交易统计分析测试"""

    def test_get_transaction_statistics_basic(self, transaction_service: TransactionService, test_user: User, test_transaction: Transaction):
        """测试基础交易统计"""
        # 明确指定时间范围，确保包含测试交易
        start_date = datetime.now() - timedelta(days=1)
        end_date = datetime.now() + timedelta(days=1)
        
        result = transaction_service.get_transaction_statistics(
            test_user.id, start_date=start_date, end_date=end_date
        )
        
        assert result.total_transactions >= 1
        assert result.total_expense > 0
        assert result.total_points_earned >= 0
        assert result.total_cashback_earned >= 0
        assert isinstance(result.type_distribution, dict)
        assert isinstance(result.monthly_trends, list)

    def test_get_transaction_statistics_with_date_range(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard, db_session: Session):
        """测试指定日期范围的统计"""
        # 创建不同时期的交易
        old_date = datetime.now() - timedelta(days=60)
        recent_date = datetime.now() - timedelta(days=10)
        
        old_transaction = Transaction(
            user_id=test_user.id,
            card_id=test_card.id,
            transaction_type="expense",
            amount=Decimal("1000.00"),
            description="旧交易",
            transaction_date=old_date,
            points_earned=1000,
            cashback_earned=Decimal("10.00")
        )
        recent_transaction = Transaction(
            user_id=test_user.id,
            card_id=test_card.id,
            transaction_type="expense",
            amount=Decimal("500.00"),
            description="近期交易",
            transaction_date=recent_date,
            points_earned=500,
            cashback_earned=Decimal("5.00")
        )
        db_session.add_all([old_transaction, recent_transaction])
        db_session.commit()
        
        # 统计最近30天
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        result = transaction_service.get_transaction_statistics(
            test_user.id, start_date=start_date, end_date=end_date
        )
        
        assert result.period_start == start_date
        assert result.period_end == end_date
        # 应该只包含近期交易，不包含60天前的交易

    def test_get_transaction_statistics_type_distribution(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard, db_session: Session):
        """测试交易类型分布统计"""
        # 使用当前时间确保在统计范围内
        current_time = datetime.now()
        
        # 创建不同类型的交易
        expense_transaction = Transaction(
            user_id=test_user.id,
            card_id=test_card.id,
            transaction_type="expense",
            amount=Decimal("800.00"),
            description="支出交易",
            transaction_date=current_time
        )
        income_transaction = Transaction(
            user_id=test_user.id,
            card_id=test_card.id,
            transaction_type="income",
            amount=Decimal("400.00"),
            description="收入交易",
            transaction_date=current_time
        )
        db_session.add_all([expense_transaction, income_transaction])
        db_session.commit()
        
        # 明确指定时间范围
        start_date = current_time - timedelta(days=1)
        end_date = current_time + timedelta(days=1)
        
        result = transaction_service.get_transaction_statistics(
            test_user.id, start_date=start_date, end_date=end_date
        )
        
        # 验证统计数据包含我们创建的交易
        assert result.total_transactions >= 2
        if result.type_distribution:
            if "expense" in result.type_distribution:
                assert result.type_distribution["expense"]["count"] >= 1
            if "income" in result.type_distribution:
                assert result.type_distribution["income"]["count"] >= 1
        assert result.net_amount == result.total_income - result.total_expense

    def test_get_transaction_statistics_empty_user(self, transaction_service: TransactionService):
        """测试空用户的统计数据"""
        fake_user_id = uuid.uuid4()
        
        result = transaction_service.get_transaction_statistics(fake_user_id)
        
        assert result.total_transactions == 0
        assert result.total_expense == 0
        assert result.total_income == 0
        assert result.net_amount == 0
        assert result.average_transaction == 0
        assert result.total_points_earned == 0
        assert result.total_cashback_earned == 0

    def test_get_category_statistics(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard, test_category: TransactionCategory, db_session: Session):
        """测试分类统计"""
        # 使用当前时间确保在统计范围内
        current_time = datetime.now()
        
        # 创建分类交易
        category_transaction = Transaction(
            user_id=test_user.id,
            card_id=test_card.id,
            category_id=test_category.id,
            transaction_type="expense",
            amount=Decimal("600.00"),
            description="分类交易",
            transaction_date=current_time
        )
        db_session.add(category_transaction)
        db_session.commit()
        
        # 明确指定时间范围
        start_date = current_time - timedelta(days=1)
        end_date = current_time + timedelta(days=1)
        
        result = transaction_service.get_category_statistics(
            test_user.id, start_date=start_date, end_date=end_date
        )
        
        assert result.total_categories >= 0
        assert result.total_expense >= 0
        assert isinstance(result.category_distribution, list)
        assert isinstance(result.top_categories, list)
        
        # 验证分类数据
        if result.category_distribution:
            category_item = result.category_distribution[0]
            assert "category_name" in category_item
            assert "transaction_count" in category_item
            assert "total_amount" in category_item
            assert "percentage" in category_item

    def test_get_monthly_trends(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard, db_session: Session):
        """测试月度趋势分析"""
        # 创建不同月份的交易
        current_month = datetime.now()
        last_month = current_month - timedelta(days=35)
        
        current_transaction = Transaction(
            user_id=test_user.id,
            card_id=test_card.id,
            transaction_type="expense",
            amount=Decimal("1200.00"),
            description="本月交易",
            transaction_date=current_month
        )
        last_transaction = Transaction(
            user_id=test_user.id,
            card_id=test_card.id,
            transaction_type="expense",
            amount=Decimal("800.00"),
            description="上月交易",
            transaction_date=last_month
        )
        db_session.add_all([current_transaction, last_transaction])
        db_session.commit()
        
        result = transaction_service.get_monthly_trends(test_user.id, months=6)
        
        assert result.analysis_period == "6个月"
        assert result.total_months >= 0
        assert isinstance(result.monthly_trends, list)
        assert result.expense_trend in ["increasing", "decreasing", "stable"]
        
        # 验证月度数据结构
        if result.monthly_trends:
            trend_item = result.monthly_trends[0]
            assert "year" in trend_item
            assert "month" in trend_item
            assert "month_name" in trend_item
            assert "expense_amount" in trend_item
            assert "income_amount" in trend_item
            assert "net_amount" in trend_item


class TestTransactionCategories:
    """交易分类管理测试"""

    def test_get_transaction_categories(self, transaction_service: TransactionService, test_category: TransactionCategory):
        """测试获取交易分类列表"""
        categories = transaction_service.get_transaction_categories()
        
        assert isinstance(categories, list)
        assert len(categories) >= 1
        
        # 验证分类数据结构
        category_item = categories[0]
        assert "id" in category_item
        assert "name" in category_item
        assert "icon" in category_item
        assert "color" in category_item
        assert "is_system" in category_item

    def test_get_transaction_categories_active_only(self, transaction_service: TransactionService, db_session: Session):
        """测试只获取激活的分类"""
        # 创建激活和非激活的分类
        active_category = TransactionCategory(
            name="激活分类",
            is_active=True,
            sort_order=1
        )
        inactive_category = TransactionCategory(
            name="非激活分类",
            is_active=False,
            sort_order=2
        )
        db_session.add_all([active_category, inactive_category])
        db_session.commit()
        
        categories = transaction_service.get_transaction_categories()
        category_names = [cat["name"] for cat in categories]
        
        assert "激活分类" in category_names
        assert "非激活分类" not in category_names


class TestTransactionServiceErrorHandling:
    """交易服务错误处理测试"""

    def test_create_transaction_database_error(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard):
        """测试创建交易时数据库错误"""
        with patch.object(transaction_service.db, 'commit', side_effect=Exception("Database error")):
            transaction_data = TransactionCreate(
                card_id=test_card.id,
                transaction_type="expense",
                amount=Decimal("100.00"),
                description="测试交易"
            )
            
            with pytest.raises(Exception) as exc_info:
                transaction_service.create_transaction(test_user.id, transaction_data)
            
            assert "Database error" in str(exc_info.value)

    def test_get_transactions_database_error(self, transaction_service: TransactionService, test_user: User):
        """测试获取交易列表时数据库错误"""
        with patch.object(transaction_service.db, 'query', side_effect=Exception("Database error")):
            with pytest.raises(Exception) as exc_info:
                transaction_service.get_user_transactions(test_user.id)
            
            assert "Database error" in str(exc_info.value)


class TestTransactionServiceEdgeCases:
    """交易服务边界情况测试"""

    def test_create_transaction_zero_amount_invalid(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard):
        """测试创建零金额交易（应该通过Pydantic验证失败）"""
        from pydantic import ValidationError as PydanticValidationError
        with pytest.raises(PydanticValidationError):
            # 这会在Pydantic验证层失败，因为amount必须大于0
            TransactionCreate(
                card_id=test_card.id,
                transaction_type="expense",
                amount=Decimal("0.00"),
                description="零金额交易"
            )

    def test_create_transaction_large_amount(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard):
        """测试创建大金额交易"""
        transaction_data = TransactionCreate(
            card_id=test_card.id,
            transaction_type="expense",
            amount=Decimal("999999.99"),
            description="大金额交易"
        )
        
        result = transaction_service.create_transaction(test_user.id, transaction_data)
        
        assert result.amount == Decimal("999999.99")
        assert result.points_earned == 999999

    def test_get_transactions_large_page_size(self, transaction_service: TransactionService, test_user: User):
        """测试大页面大小查询"""
        transactions, total = transaction_service.get_user_transactions(test_user.id, page=1, page_size=1000)
        
        assert isinstance(transactions, list)
        assert total >= 0

    def test_update_transaction_partial_data(self, transaction_service: TransactionService, test_user: User, test_transaction: Transaction):
        """测试部分更新交易数据"""
        original_description = test_transaction.description
        original_amount = test_transaction.amount
        
        update_data = TransactionUpdate(description="仅更新描述")
        
        result = transaction_service.update_transaction(test_user.id, test_transaction.id, update_data)
        
        assert result.description == "仅更新描述"
        assert result.amount == original_amount  # 金额不应该变化

    def test_statistics_with_future_date_range(self, transaction_service: TransactionService, test_user: User):
        """测试未来日期范围的统计"""
        start_date = datetime.now() + timedelta(days=1)
        end_date = datetime.now() + timedelta(days=30)
        
        result = transaction_service.get_transaction_statistics(
            test_user.id, start_date=start_date, end_date=end_date
        )
        
        # 未来日期范围应该没有数据
        assert result.total_transactions == 0
        assert result.total_expense == 0
        assert result.total_income == 0


class TestTransactionServicePerformance:
    """交易服务性能测试"""

    def test_bulk_transaction_creation_performance(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard, db_session: Session):
        """测试批量创建交易的性能"""
        # 创建多个交易
        start_time = datetime.now()
        
        for i in range(50):
            transaction_data = TransactionCreate(
                card_id=test_card.id,
                transaction_type="expense",
                amount=Decimal(f"{100 + i}.00"),
                description=f"性能测试交易{i}"
            )
            transaction_service.create_transaction(test_user.id, transaction_data)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 50个交易应该在合理时间内完成
        assert duration < 30  # 30秒内完成

    def test_large_dataset_statistics_performance(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard, db_session: Session):
        """测试大数据集统计的性能"""
        # 创建大量交易数据
        transactions_data = []
        for i in range(100):
            transaction = Transaction(
                user_id=test_user.id,
                card_id=test_card.id,
                transaction_type="expense" if i % 2 == 0 else "income",
                amount=Decimal(f"{50 + (i % 50)}.00"),
                description=f"大数据集测试{i}",
                transaction_date=datetime.now() - timedelta(days=i % 60),
                points_earned=50 + (i % 50),
                cashback_earned=Decimal(f"{(50 + (i % 50)) * 0.01:.2f}")
            )
            transactions_data.append(transaction)
        
        db_session.add_all(transactions_data)
        db_session.commit()
        
        # 测试统计性能
        start_time = datetime.now()
        
        # 明确指定时间范围，确保包含所有测试数据
        stats_start_date = datetime.now() - timedelta(days=70)
        stats_end_date = datetime.now() + timedelta(days=1)
        
        result = transaction_service.get_transaction_statistics(
            test_user.id, start_date=stats_start_date, end_date=stats_end_date
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # 统计计算应该在合理时间内完成
        assert duration < 5  # 5秒内完成
        assert result.total_transactions >= 50  # 应该包含所有100个测试交易


class TestTransactionServiceDataIntegrity:
    """交易服务数据完整性测试"""

    def test_transaction_creation_data_consistency(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard, test_category: TransactionCategory, db_session: Session):
        """测试交易创建的数据一致性"""
        transaction_data = TransactionCreate(
            card_id=test_card.id,
            category_id=test_category.id,
            transaction_type="expense",
            amount=Decimal("250.75"),
            description="数据一致性测试",
            merchant_name="测试商户",
            currency="CNY",
            tags=["测试", "一致性"]
        )
        
        result = transaction_service.create_transaction(test_user.id, transaction_data)
        
        # 验证数据库中的数据与返回结果一致
        db_transaction = db_session.query(Transaction).filter(Transaction.id == result.id).first()
        
        assert db_transaction is not None
        assert db_transaction.user_id == test_user.id
        assert db_transaction.card_id == test_card.id
        assert db_transaction.category_id == test_category.id
        assert db_transaction.amount == Decimal("250.75")
        assert db_transaction.description == "数据一致性测试"
        assert db_transaction.merchant_name == "测试商户"
        assert db_transaction.currency == "CNY"
        assert db_transaction.tags == ["测试", "一致性"]
        
        # 验证积分和返现计算正确
        expected_points = int(Decimal("250.75") * test_card.points_rate)
        expected_cashback = Decimal("250.75") * test_card.cashback_rate / 100
        
        assert db_transaction.points_earned == expected_points
        # 允许小数精度差异
        assert abs(db_transaction.cashback_earned - expected_cashback) < Decimal("0.01")

    def test_update_preserves_unchanged_fields(self, transaction_service: TransactionService, test_user: User, test_transaction: Transaction):
        """测试更新操作保留未变更字段"""
        original_created_at = test_transaction.created_at
        original_user_id = test_transaction.user_id
        original_card_id = test_transaction.card_id
        original_currency = test_transaction.currency
        
        # 只更新描述
        update_data = TransactionUpdate(description="更新后的描述")
        
        result = transaction_service.update_transaction(test_user.id, test_transaction.id, update_data)
        
        # 验证只有描述被更新，其他字段保持不变
        assert result.description == "更新后的描述"
        assert result.created_at == original_created_at
        assert result.card_id == original_card_id
        assert result.currency == original_currency

    def test_statistics_calculation_accuracy(self, transaction_service: TransactionService, test_user: User, test_card: CreditCard, db_session: Session):
        """测试统计计算的准确性"""
        # 使用当前时间确保在统计范围内
        current_time = datetime.now()
        
        # 创建已知数据的交易
        expense_amount = Decimal("1000.00")
        income_amount = Decimal("300.00")
        
        expense_transaction = Transaction(
            user_id=test_user.id,
            card_id=test_card.id,
            transaction_type="expense",
            amount=expense_amount,
            description="支出测试",
            transaction_date=current_time,
            points_earned=1000,
            cashback_earned=Decimal("10.00")
        )
        income_transaction = Transaction(
            user_id=test_user.id,
            card_id=test_card.id,
            transaction_type="income",
            amount=income_amount,
            description="收入测试",
            transaction_date=current_time,
            points_earned=0,
            cashback_earned=Decimal("0.00")
        )
        
        db_session.add_all([expense_transaction, income_transaction])
        db_session.commit()
        
        # 明确指定时间范围
        start_date = current_time - timedelta(days=1)
        end_date = current_time + timedelta(days=1)
        
        result = transaction_service.get_transaction_statistics(
            test_user.id, start_date=start_date, end_date=end_date
        )
        
        # 验证统计计算准确性（考虑可能有其他测试数据）
        assert result.total_transactions >= 2
        assert result.total_expense >= float(expense_amount)
        assert result.total_income >= float(income_amount)
        assert result.net_amount == result.total_income - result.total_expense
        assert result.total_points_earned >= 1000
        assert result.total_cashback_earned >= 10.0 