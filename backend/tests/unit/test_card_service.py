"""
信用卡服务单元测试 - 直连测试数据库
"""
import pytest
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch

from app.services.card_service import CardService
from app.models.database.card import CreditCard, Bank
from app.models.database.user import User
from app.models.schemas.card import (
    CreditCardCreate, CreditCardUpdate, CreditCardQueryParams,
    BankCreate, BankUpdate
)
from app.core.exceptions.custom import (
    ResourceNotFoundError, BusinessRuleError, ValidationError
)
from tests.utils.db import create_test_session


@pytest.fixture
def db_session():
    """测试数据库会话"""
    session = create_test_session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def card_service(db_session: Session):
    """信用卡服务实例"""
    return CardService(db_session)


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


class TestBankManagement:
    """银行管理测试"""

    def test_create_bank_success(self, card_service: CardService):
        """测试创建银行成功"""
        bank_data = BankCreate(
            bank_code="TESTBANK",
            bank_name="测试银行",
            bank_logo="https://example.com/logo.png",
            sort_order=1
        )
        
        result = card_service.create_bank(bank_data)
        
        assert result.bank_code == "TESTBANK"
        assert result.bank_name == "测试银行"
        assert result.is_active is True

    def test_create_bank_duplicate_code(self, card_service: CardService, test_bank: Bank):
        """测试创建重复银行代码失败"""
        bank_data = BankCreate(
            bank_code=test_bank.bank_code,
            bank_name="另一个银行",
            sort_order=2
        )
        
        with pytest.raises(BusinessRuleError) as exc_info:
            card_service.create_bank(bank_data)
        
        assert "已存在" in str(exc_info.value)

    def test_get_banks_active_only(self, card_service: CardService, db_session: Session):
        """测试获取活跃银行列表"""
        # 创建活跃和非活跃银行
        active_bank = Bank(bank_code="ACTIVE", bank_name="活跃银行", is_active=True)
        inactive_bank = Bank(bank_code="INACTIVE", bank_name="非活跃银行", is_active=False)
        
        db_session.add_all([active_bank, inactive_bank])
        db_session.commit()
        
        banks = card_service.get_banks(active_only=True)
        bank_names = [bank.bank_name for bank in banks]
        
        assert "活跃银行" in bank_names
        assert "非活跃银行" not in bank_names

    def test_get_banks_all(self, card_service: CardService, db_session: Session):
        """测试获取所有银行列表"""
        # 创建活跃和非活跃银行
        active_bank = Bank(bank_code="ACTIVE2", bank_name="活跃银行2", is_active=True)
        inactive_bank = Bank(bank_code="INACTIVE2", bank_name="非活跃银行2", is_active=False)
        
        db_session.add_all([active_bank, inactive_bank])
        db_session.commit()
        
        banks = card_service.get_banks(active_only=False)
        bank_names = [bank.bank_name for bank in banks]
        
        assert "活跃银行2" in bank_names
        assert "非活跃银行2" in bank_names

    def test_get_bank_by_id_success(self, card_service: CardService, test_bank: Bank):
        """测试根据ID获取银行成功"""
        result = card_service.get_bank_by_id(test_bank.id)
        
        assert result is not None
        assert result.id == test_bank.id
        assert result.bank_name == test_bank.bank_name

    def test_get_bank_by_id_not_found(self, card_service: CardService):
        """测试获取不存在的银行"""
        fake_id = uuid.uuid4()
        result = card_service.get_bank_by_id(fake_id)
        
        assert result is None

    def test_get_or_create_bank_by_name_existing(self, card_service: CardService, test_bank: Bank):
        """测试获取已存在的银行"""
        result = card_service.get_or_create_bank_by_name(test_bank.bank_name)
        
        assert result.id == test_bank.id
        assert result.bank_name == test_bank.bank_name

    def test_get_or_create_bank_by_name_new(self, card_service: CardService):
        """测试创建新银行"""
        bank_name = "全新银行"
        result = card_service.get_or_create_bank_by_name(bank_name)
        
        assert result.bank_name == bank_name
        assert result.is_active is True
        assert result.bank_code is not None


class TestCreditCardManagement:
    """信用卡管理测试"""

    def test_create_credit_card_success(self, card_service: CardService, test_user: User, test_bank: Bank):
        """测试创建信用卡成功"""
        card_data = CreditCardCreate(
            bank_id=test_bank.id,
            card_number="6225123456789012",
            card_name="我的测试卡",
            card_type="credit",
            credit_limit=Decimal("100000.00"),
            expiry_month=12,
            expiry_year=2028
        )
        
        result = card_service.create_credit_card(test_user.id, card_data)
        
        assert result.card_name == "我的测试卡"
        assert result.credit_limit == Decimal("100000.00")
        assert result.available_limit == Decimal("100000.00")
        assert result.user_id == test_user.id
        assert result.bank.id == test_bank.id

    def test_create_credit_card_with_bank_name(self, card_service: CardService, test_user: User):
        """测试通过银行名称创建信用卡"""
        card_data = CreditCardCreate(
            bank_name="招商银行",
            card_number="6225123456789013",
            card_name="招商银行信用卡",
            card_type="credit",
            credit_limit=Decimal("50000.00"),
            expiry_month=6,
            expiry_year=2029
        )
        
        result = card_service.create_credit_card(test_user.id, card_data)
        
        assert result.card_name == "招商银行信用卡"
        assert result.bank.bank_name == "招商银行"

    def test_create_credit_card_user_not_found(self, card_service: CardService, test_bank: Bank):
        """测试用户不存在时创建信用卡失败"""
        fake_user_id = uuid.uuid4()
        card_data = CreditCardCreate(
            bank_id=test_bank.id,
            card_number="6225123456789014",
            card_name="测试卡",
            credit_limit=Decimal("50000.00"),
            expiry_month=12,
            expiry_year=2027
        )
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            card_service.create_credit_card(fake_user_id, card_data)
        
        assert "用户不存在" in str(exc_info.value)

    def test_create_credit_card_bank_not_found(self, card_service: CardService, test_user: User):
        """测试银行不存在时创建信用卡失败"""
        fake_bank_id = uuid.uuid4()
        card_data = CreditCardCreate(
            bank_id=fake_bank_id,
            card_number="6225123456789015",
            card_name="测试卡",
            credit_limit=Decimal("50000.00"),
            expiry_month=12,
            expiry_year=2027
        )
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            card_service.create_credit_card(test_user.id, card_data)
        
        assert "银行不存在" in str(exc_info.value)

    def test_create_credit_card_duplicate_number(self, card_service: CardService, test_user: User, test_card: CreditCard):
        """测试重复卡号创建失败"""
        card_data = CreditCardCreate(
            bank_name="测试银行",
            card_number=test_card.card_number,
            card_name="重复卡号",
            credit_limit=Decimal("50000.00"),
            expiry_month=12,
            expiry_year=2027
        )
        
        with pytest.raises(BusinessRuleError) as exc_info:
            card_service.create_credit_card(test_user.id, card_data)
        
        assert "已存在" in str(exc_info.value)

    def test_get_user_cards_success(self, card_service: CardService, test_user: User, test_card: CreditCard):
        """测试获取用户信用卡列表成功"""
        params = CreditCardQueryParams(page=1, page_size=10)
        
        cards, total = card_service.get_user_cards(test_user.id, params)
        
        assert total >= 1
        assert len(cards) >= 1
        assert cards[0].user_id == test_user.id

    def test_get_user_cards_with_keyword_filter(self, card_service: CardService, test_user: User, test_card: CreditCard):
        """测试关键词筛选信用卡"""
        params = CreditCardQueryParams(
            page=1, 
            page_size=10, 
            keyword=test_card.card_name[:5]
        )
        
        cards, total = card_service.get_user_cards(test_user.id, params)
        
        assert total >= 1
        assert any(test_card.card_name[:5] in card.card_name for card in cards)

    def test_get_user_cards_with_status_filter(self, card_service: CardService, test_user: User, test_card: CreditCard):
        """测试状态筛选信用卡"""
        params = CreditCardQueryParams(
            page=1, 
            page_size=10, 
            status="active"
        )
        
        cards, total = card_service.get_user_cards(test_user.id, params)
        
        assert all(card.status == "active" for card in cards)

    def test_get_user_cards_expiring_soon(self, card_service: CardService, test_user: User, db_session: Session):
        """测试获取即将过期的信用卡"""
        # 创建即将过期的卡片
        now = datetime.now()
        expiring_card = CreditCard(
            user_id=test_user.id,
            card_number="6225999999999999",
            card_name="即将过期的卡",
            credit_limit=Decimal("50000.00"),
            available_limit=Decimal("50000.00"),
            expiry_month=now.month,
            expiry_year=now.year,
            status="active"
        )
        db_session.add(expiring_card)
        db_session.commit()
        
        params = CreditCardQueryParams(
            page=1, 
            page_size=10, 
            expiring_soon=True
        )
        
        cards, total = card_service.get_user_cards(test_user.id, params)
        
        assert total >= 1
        assert any(card.card_name == "即将过期的卡" for card in cards)

    def test_get_card_by_id_success(self, card_service: CardService, test_user: User, test_card: CreditCard):
        """测试获取信用卡详情成功"""
        result = card_service.get_card_by_id(test_user.id, test_card.id)
        
        assert result is not None
        assert result.id == test_card.id
        assert result.user_id == test_user.id

    def test_get_card_by_id_not_found(self, card_service: CardService, test_user: User):
        """测试获取不存在的信用卡"""
        fake_card_id = uuid.uuid4()
        result = card_service.get_card_by_id(test_user.id, fake_card_id)
        
        assert result is None

    def test_get_card_by_id_wrong_user(self, card_service: CardService, test_card: CreditCard):
        """测试获取其他用户的信用卡"""
        fake_user_id = uuid.uuid4()
        result = card_service.get_card_by_id(fake_user_id, test_card.id)
        
        assert result is None

    def test_update_credit_card_success(self, card_service: CardService, test_user: User, test_card: CreditCard):
        """测试更新信用卡成功"""
        update_data = CreditCardUpdate(
            card_name="更新后的卡名",
            credit_limit=Decimal("80000.00"),
            notes="更新备注"
        )
        
        result = card_service.update_credit_card(test_user.id, test_card.id, update_data)
        
        assert result.card_name == "更新后的卡名"
        assert result.credit_limit == Decimal("80000.00")
        assert result.notes == "更新备注"

    def test_update_credit_card_not_found(self, card_service: CardService, test_user: User):
        """测试更新不存在的信用卡"""
        fake_card_id = uuid.uuid4()
        update_data = CreditCardUpdate(card_name="新名称")
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            card_service.update_credit_card(test_user.id, fake_card_id, update_data)
        
        assert "信用卡不存在" in str(exc_info.value)

    def test_update_card_status_success(self, card_service: CardService, test_user: User, test_card: CreditCard):
        """测试更新信用卡状态成功"""
        result = card_service.update_card_status(test_user.id, test_card.id, "frozen", "临时冻结")
        
        assert result.status == "frozen"
        assert "临时冻结" in result.notes

    def test_update_card_status_not_found(self, card_service: CardService, test_user: User):
        """测试更新不存在信用卡的状态"""
        fake_card_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            card_service.update_card_status(test_user.id, fake_card_id, "frozen")
        
        assert "信用卡不存在" in str(exc_info.value)

    def test_delete_credit_card_success(self, card_service: CardService, test_user: User, test_card: CreditCard):
        """测试删除信用卡成功"""
        result = card_service.delete_credit_card(test_user.id, test_card.id)
        
        assert result is True
        
        # 验证卡片已删除
        deleted_card = card_service.get_card_by_id(test_user.id, test_card.id)
        assert deleted_card is None

    def test_delete_credit_card_not_found(self, card_service: CardService, test_user: User):
        """测试删除不存在的信用卡"""
        fake_card_id = uuid.uuid4()
        
        with pytest.raises(ResourceNotFoundError) as exc_info:
            card_service.delete_credit_card(test_user.id, fake_card_id)
        
        assert "信用卡不存在" in str(exc_info.value)


class TestCreditCardStatistics:
    """信用卡统计测试"""

    def test_get_card_summary(self, card_service: CardService, test_user: User, test_card: CreditCard):
        """测试获取信用卡摘要统计"""
        summary = card_service.get_card_summary(test_user.id)
        
        assert summary.total_cards >= 1
        assert summary.active_cards >= 1
        assert summary.total_credit_limit >= test_card.credit_limit
        assert summary.average_utilization_rate >= 0

    def test_get_card_summary_empty_user(self, card_service: CardService):
        """测试无信用卡用户的摘要统计"""
        fake_user_id = uuid.uuid4()
        summary = card_service.get_card_summary(fake_user_id)
        
        assert summary.total_cards == 0
        assert summary.active_cards == 0
        assert summary.total_credit_limit == 0
        assert summary.average_utilization_rate == 0

    def test_get_card_statistics(self, card_service: CardService, test_user: User, test_card: CreditCard):
        """测试获取信用卡详细统计"""
        stats = card_service.get_card_statistics(test_user.id)
        
        assert stats.summary.total_cards >= 1
        assert len(stats.by_bank) >= 1
        assert len(stats.by_status) >= 1
        assert len(stats.utilization_distribution) == 4  # 4个使用率区间

    def test_get_card_statistics_multiple_cards(self, card_service: CardService, test_user: User, test_bank: Bank, db_session: Session):
        """测试多张信用卡的统计"""
        # 创建多张不同状态的卡片
        cards_data = [
            {"card_name": "活跃卡1", "status": "active", "credit_limit": Decimal("50000")},
            {"card_name": "活跃卡2", "status": "active", "credit_limit": Decimal("100000")},
            {"card_name": "冻结卡", "status": "frozen", "credit_limit": Decimal("30000")},
        ]
        
        for i, card_data in enumerate(cards_data):
            card = CreditCard(
                user_id=test_user.id,
                bank_id=test_bank.id,
                card_number=f"622512345678901{i}",
                card_name=card_data["card_name"],
                status=card_data["status"],
                credit_limit=card_data["credit_limit"],
                available_limit=card_data["credit_limit"],
                expiry_month=12,
                expiry_year=2027
            )
            db_session.add(card)
        
        db_session.commit()
        
        stats = card_service.get_card_statistics(test_user.id)
        
        # 验证按状态统计
        status_counts = {item['status']: item['count'] for item in stats.by_status}
        assert status_counts.get('active', 0) >= 2
        assert status_counts.get('frozen', 0) >= 1


class TestCardServiceErrorHandling:
    """信用卡服务错误处理测试"""

    def test_create_card_database_error(self, card_service: CardService, test_user: User):
        """测试数据库错误处理"""
        with patch.object(card_service.db, 'commit', side_effect=Exception("数据库错误")):
            card_data = CreditCardCreate(
                bank_name="测试银行",
                card_number="6225123456789999",
                card_name="测试卡",
                credit_limit=Decimal("50000.00"),
                expiry_month=12,
                expiry_year=2027
            )
            
            with pytest.raises(Exception) as exc_info:
                card_service.create_credit_card(test_user.id, card_data)
            
            assert "数据库错误" in str(exc_info.value)

    def test_get_cards_database_error(self, card_service: CardService, test_user: User):
        """测试获取卡片列表时的数据库错误"""
        with patch.object(card_service.db, 'query', side_effect=Exception("查询错误")):
            params = CreditCardQueryParams(page=1, page_size=10)
            
            with pytest.raises(Exception) as exc_info:
                card_service.get_user_cards(test_user.id, params)
            
            assert "查询错误" in str(exc_info.value)

    def test_build_card_response_error_handling(self, card_service: CardService, test_card: CreditCard):
        """测试构建响应对象时的错误处理"""
        # 模拟一个没有银行关联的卡片
        test_card.bank = None
        test_card.bank_id = None
        
        try:
            result = card_service._build_card_response(test_card)
            # 应该能正常处理没有银行的情况
            assert result.bank is None
            assert result.card_name == test_card.card_name
        except Exception as e:
            pytest.fail(f"构建响应对象时不应该抛出异常: {e}")


class TestCardServiceEdgeCases:
    """信用卡服务边界情况测试"""

    def test_create_card_with_zero_limit(self, card_service: CardService, test_user: User, test_bank: Bank):
        """测试创建零额度信用卡"""
        card_data = CreditCardCreate(
            bank_id=test_bank.id,
            card_number="6225000000000000",
            card_name="零额度卡",
            credit_limit=Decimal("0.00"),
            expiry_month=12,
            expiry_year=2027
        )
        
        result = card_service.create_credit_card(test_user.id, card_data)
        
        assert result.credit_limit == Decimal("0.00")
        assert result.available_limit == Decimal("0.00")

    def test_get_cards_with_large_page_size(self, card_service: CardService, test_user: User):
        """测试大页面大小的分页查询"""
        params = CreditCardQueryParams(page=1, page_size=100)  # 使用最大允许值100
        
        cards, total = card_service.get_user_cards(test_user.id, params)
        
        # 应该正常返回，不会出错
        assert isinstance(cards, list)
        assert isinstance(total, int)

    def test_update_card_with_empty_data(self, card_service: CardService, test_user: User, test_card: CreditCard):
        """测试使用空数据更新信用卡"""
        update_data = CreditCardUpdate()
        
        result = card_service.update_credit_card(test_user.id, test_card.id, update_data)
        
        # 应该返回原始数据，没有任何更改
        assert result.card_name == test_card.card_name
        assert result.credit_limit == test_card.credit_limit

    def test_card_utilization_calculation(self, card_service: CardService, test_user: User, test_card: CreditCard, db_session: Session):
        """测试信用卡使用率计算"""
        # 设置已用额度
        test_card.used_limit = Decimal("25000.00")  # 50%使用率
        db_session.commit()
        
        result = card_service.get_card_by_id(test_user.id, test_card.id)
        
        assert result.credit_utilization_rate == 50.0

    def test_expired_card_detection(self, card_service: CardService, test_user: User, db_session: Session):
        """测试过期卡片检测"""
        # 创建已过期的卡片
        expired_card = CreditCard(
            user_id=test_user.id,
            card_number="6225888888888888",
            card_name="过期卡片",
            credit_limit=Decimal("50000.00"),
            available_limit=Decimal("50000.00"),
            expiry_month=1,
            expiry_year=2020,  # 已过期
            status="active"
        )
        db_session.add(expired_card)
        db_session.commit()
        
        result = card_service.get_card_by_id(test_user.id, expired_card.id)
        
        assert result.is_expired is True 