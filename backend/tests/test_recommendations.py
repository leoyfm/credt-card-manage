"""
推荐接口测试

测试智能推荐系统的所有功能，包括：
- 生成个性化推荐
- 获取推荐列表
- 获取推荐详情
- 提交推荐反馈
- 用户画像分析
"""

import pytest
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID, uuid4
from typing import List, Dict, Any

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from database import get_db
from db_models.users import User
from db_models.cards import CreditCard
from db_models.transactions import Transaction
from db_models.recommendations import Recommendation as DBRecommendation
from models.recommendations import RecommendationType, RecommendationStatus
from models.transactions import TransactionCategory, TransactionType
from services.auth_service import AuthService
from services.recommendations_service import RecommendationsService
from utils.auth import AuthUtils

logger = logging.getLogger(__name__)

# 测试客户端
client = TestClient(app)

class TestRecommendations:
    """推荐接口测试类"""
    
    @pytest.fixture(scope="class")
    def test_user_data(self, db_session: Session):
        """创建测试用户和相关数据"""
        # 创建测试用户
        auth_service = AuthService(db_session)
        user_data = {
            "username": "test_rec_user",
            "email": "testrec@example.com",
            "password": "TestPass123456",
            "nickname": "推荐测试用户"
        }
        
        # 注册用户
        from models.users import UserRegisterRequest
        register_request = UserRegisterRequest(**user_data)
        user_profile = auth_service.register_user(register_request, "127.0.0.1")
        user_id = UUID(user_profile.id)
        
        # 生成JWT令牌
        token_data = {"sub": str(user_id), "username": user_data["username"]}
        access_token = AuthUtils.create_access_token(token_data)
        
        # 创建测试信用卡
        card1 = CreditCard(
            id=uuid4(),
            user_id=user_id,
            bank_name="招商银行",
            card_name="招商银行全币种信用卡",
            card_number="4321123412341234",
            cardholder_name="推荐测试用户",
            card_type="visa",
            credit_limit=Decimal("100000"),
            used_amount=Decimal("35000"),
            available_amount=Decimal("65000"),
            billing_day=5,
            due_day=25,
            expiry_month=12,
            expiry_year=2027,
            status="active",
            is_active=True,
            activation_date=datetime.utcnow() - timedelta(days=365),
            created_at=datetime.utcnow() - timedelta(days=365)
        )
        
        card2 = CreditCard(
            id=uuid4(),
            user_id=user_id,
            bank_name="中信银行",
            card_name="中信银行颜卡",
            card_number="5432154321543215",
            cardholder_name="推荐测试用户",
            card_type="mastercard",
            credit_limit=Decimal("50000"),
            used_amount=Decimal("15000"),
            available_amount=Decimal("35000"),
            billing_day=10,
            due_day=30,
            expiry_month=8,
            expiry_year=2026,
            status="active",
            is_active=True,
            activation_date=datetime.utcnow() - timedelta(days=200),
            created_at=datetime.utcnow() - timedelta(days=200)
        )
        
        db_session.add(card1)
        db_session.add(card2)
        
        # 创建测试交易记录
        transactions = []
        
        # 最近3个月的交易记录
        for i in range(30):
            date = datetime.utcnow() - timedelta(days=i*3)
            
            # 餐饮消费
            trans1 = Transaction(
                id=uuid4(),
                user_id=user_id,
                card_id=card1.id,
                amount=Decimal(f"{120 + i * 5}"),
                transaction_type=TransactionType.EXPENSE,
                category=TransactionCategory.DINING,
                description=f"餐厅消费{i+1}",
                merchant_name=f"美食餐厅{i+1}",
                transaction_date=date,
                created_at=date
            )
            
            # 购物消费
            if i % 3 == 0:
                trans2 = Transaction(
                    id=uuid4(),
                    user_id=user_id,
                    card_id=card2.id,
                    amount=Decimal(f"{500 + i * 20}"),
                    transaction_type=TransactionType.EXPENSE,
                    category=TransactionCategory.SHOPPING,
                    description=f"购物消费{i+1}",
                    merchant_name=f"购物中心{i+1}",
                    transaction_date=date,
                    created_at=date
                )
                transactions.append(trans2)
            
            # 交通出行
            if i % 5 == 0:
                trans3 = Transaction(
                    id=uuid4(),
                    user_id=user_id,
                    card_id=card1.id,
                    amount=Decimal(f"{50 + i * 2}"),
                    transaction_type=TransactionType.EXPENSE,
                    category=TransactionCategory.TRANSPORT,
                    description=f"打车费用{i+1}",
                    merchant_name="滴滴出行",
                    transaction_date=date,
                    created_at=date
                )
                transactions.append(trans3)
            
            transactions.append(trans1)
        
        db_session.add_all(transactions)
        db_session.commit()
        
        return {
            "user_id": user_id,
            "access_token": access_token,
            "username": user_data["username"],
            "cards": [card1, card2],
            "transactions": transactions
        }
    
    @pytest.fixture
    def auth_headers(self, test_user_data):
        """获取认证头"""
        return {"Authorization": f"Bearer {test_user_data['access_token']}"}
    
    def test_generate_recommendations_success(self, test_user_data, auth_headers):
        """测试生成个性化推荐 - 成功"""
        logger.info("测试生成个性化推荐...")
        
        response = client.post("/api/recommendations/generate", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "data" in result
        
        recommendations = result["data"]
        assert isinstance(recommendations, list)
        
        # 应该生成一些推荐
        if len(recommendations) > 0:
            rec = recommendations[0]
            assert "id" in rec
            assert "title" in rec
            assert "bank_name" in rec
            assert "card_name" in rec
            assert "recommendation_type" in rec
            assert "recommendation_score" in rec
            assert "reason" in rec
            assert rec["recommendation_score"] >= 0
            assert rec["recommendation_score"] <= 100
        
        logger.info(f"成功生成 {len(recommendations)} 条推荐")
    
    def test_generate_recommendations_unauthorized(self):
        """测试生成个性化推荐 - 未授权"""
        response = client.post("/api/recommendations/generate")
        assert response.status_code == 401
    
    def test_get_user_profile_stats_success(self, test_user_data, auth_headers):
        """测试获取用户画像分析 - 成功"""
        logger.info("测试获取用户画像分析...")
        
        response = client.get("/api/recommendations/stats/user-profile", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "data" in result
        
        profile_data = result["data"]
        assert "total_cards" in profile_data
        assert "total_limit" in profile_data
        assert "used_limit" in profile_data
        assert "utilization_rate" in profile_data
        assert "monthly_spending" in profile_data
        assert "top_categories" in profile_data
        
        # 验证数据合理性
        assert profile_data["total_cards"] == 2
        assert float(profile_data["total_limit"]) > 0
        assert float(profile_data["monthly_spending"]) > 0
        assert isinstance(profile_data["top_categories"], list)
        
        logger.info(f"用户画像: {profile_data}")
    
    def test_get_user_profile_stats_unauthorized(self):
        """测试获取用户画像分析 - 未授权"""
        response = client.get("/api/recommendations/stats/user-profile")
        assert response.status_code == 401
    
    def test_get_recommendations_list_success(self, test_user_data, auth_headers):
        """测试获取推荐列表 - 成功"""
        logger.info("测试获取推荐列表...")
        
        # 先生成一些推荐
        client.post("/api/recommendations/generate", headers=auth_headers)
        
        # 获取推荐列表
        response = client.get("/api/recommendations/", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "data" in result
        
        data = result["data"]
        assert "items" in data
        assert "pagination" in data
        
        pagination = data["pagination"]
        assert "total" in pagination
        assert "page" in pagination
        assert "size" in pagination
        assert "total_pages" in pagination
        
        items = data["items"]
        assert isinstance(items, list)
        
        logger.info(f"获取到 {len(items)} 条推荐，总计 {pagination['total']} 条")
    
    def test_get_recommendations_list_with_pagination(self, test_user_data, auth_headers):
        """测试获取推荐列表 - 分页"""
        logger.info("测试推荐列表分页...")
        
        # 先生成推荐
        client.post("/api/recommendations/generate", headers=auth_headers)
        
        # 测试分页参数
        response = client.get("/api/recommendations/?page=1&page_size=5", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        
        pagination = result["data"]["pagination"]
        assert pagination["page"] == 1
        assert pagination["size"] == 5
    
    def test_get_recommendations_list_with_search(self, test_user_data, auth_headers):
        """测试获取推荐列表 - 搜索"""
        logger.info("测试推荐列表搜索...")
        
        # 先生成推荐
        client.post("/api/recommendations/generate", headers=auth_headers)
        
        # 测试搜索功能
        response = client.get("/api/recommendations/?keyword=招商", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
    
    def test_get_recommendations_list_unauthorized(self):
        """测试获取推荐列表 - 未授权"""
        response = client.get("/api/recommendations/")
        assert response.status_code == 401
    
    def test_get_recommendation_detail_success(self, test_user_data, auth_headers, db_session):
        """测试获取推荐详情 - 成功"""
        logger.info("测试获取推荐详情...")
        
        user_id = test_user_data["user_id"]
        
        # 创建一个测试推荐
        test_rec = DBRecommendation(
            id=uuid4(),
            user_id=user_id,
            title="测试推荐",
            bank_name="测试银行",
            card_name="测试信用卡",
            recommendation_type=RecommendationType.CASHBACK,
            recommendation_score=85,
            reason="测试推荐理由",
            description="详细描述",
            key_features=["特色1", "特色2"],
            pros=["优点1", "优点2"],
            cons=["缺点1"],
            annual_fee=Decimal("200"),
            cashback_rate=Decimal("1.5"),
            points_rate=Decimal("1.0"),
            grace_period_days=50,
            status=RecommendationStatus.ACTIVE,
            is_featured=False,
            view_count=0,
            created_at=datetime.utcnow()
        )
        
        db_session.add(test_rec)
        db_session.commit()
        
        # 获取推荐详情
        response = client.get(f"/api/recommendations/{test_rec.id}", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "data" in result
        
        rec_data = result["data"]
        assert rec_data["id"] == str(test_rec.id)
        assert rec_data["title"] == test_rec.title
        assert rec_data["bank_name"] == test_rec.bank_name
        assert rec_data["recommendation_score"] == test_rec.recommendation_score
        
        # 验证查看次数增加了
        db_session.refresh(test_rec)
        assert test_rec.view_count == 1
        assert test_rec.last_viewed_at is not None
        
        logger.info(f"成功获取推荐详情: {rec_data['title']}")
    
    def test_get_recommendation_detail_not_found(self, test_user_data, auth_headers):
        """测试获取推荐详情 - 不存在"""
        fake_id = uuid4()
        response = client.get(f"/api/recommendations/{fake_id}", headers=auth_headers)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is False
        assert "不存在" in result["message"]
    
    def test_get_recommendation_detail_unauthorized(self):
        """测试获取推荐详情 - 未授权"""
        fake_id = uuid4()
        response = client.get(f"/api/recommendations/{fake_id}")
        assert response.status_code == 401
    
    def test_submit_recommendation_feedback_success(self, test_user_data, auth_headers, db_session):
        """测试提交推荐反馈 - 成功"""
        logger.info("测试提交推荐反馈...")
        
        user_id = test_user_data["user_id"]
        
        # 创建一个测试推荐
        test_rec = DBRecommendation(
            id=uuid4(),
            user_id=user_id,
            title="测试推荐反馈",
            bank_name="测试银行",
            card_name="测试信用卡",
            recommendation_type=RecommendationType.POINTS,
            recommendation_score=75,
            reason="测试推荐理由",
            description="详细描述",
            status=RecommendationStatus.ACTIVE,
            created_at=datetime.utcnow()
        )
        
        db_session.add(test_rec)
        db_session.commit()
        
        # 提交反馈
        response = client.put(
            f"/api/recommendations/{test_rec.id}/feedback?feedback=interested",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert "反馈提交成功" in result["message"]
        
        # 验证反馈已保存
        db_session.refresh(test_rec)
        assert test_rec.user_feedback == "interested"
        assert test_rec.feedback_at is not None
        
        logger.info("推荐反馈提交成功")
    
    def test_submit_recommendation_feedback_not_found(self, test_user_data, auth_headers):
        """测试提交推荐反馈 - 推荐不存在"""
        fake_id = uuid4()
        response = client.put(
            f"/api/recommendations/{fake_id}/feedback?feedback=not_interested",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is False
        assert "不存在" in result["message"]
    
    def test_submit_recommendation_feedback_unauthorized(self):
        """测试提交推荐反馈 - 未授权"""
        fake_id = uuid4()
        response = client.put(f"/api/recommendations/{fake_id}/feedback?feedback=interested")
        assert response.status_code == 401
    
    def test_recommendation_service_user_profile_analysis(self, test_user_data, db_session):
        """测试推荐服务 - 用户画像分析"""
        logger.info("测试推荐服务用户画像分析...")
        
        user_id = test_user_data["user_id"]
        service = RecommendationsService(db_session)
        
        # 分析用户画像
        profile = service._analyze_user_profile(user_id)
        
        assert "card_count" in profile
        assert "total_limit" in profile
        assert "credit_utilization" in profile
        assert "monthly_spending" in profile
        assert "top_categories" in profile
        
        # 验证数据
        assert profile["card_count"] == 2
        assert profile["total_limit"] > 0
        assert profile["monthly_spending"] > 0
        assert len(profile["top_categories"]) > 0
        
        logger.info(f"用户画像分析结果: {profile}")
    
    def test_recommendation_algorithm_cashback(self, test_user_data, db_session):
        """测试推荐算法 - 现金回馈推荐"""
        logger.info("测试现金回馈推荐算法...")
        
        user_id = test_user_data["user_id"]
        service = RecommendationsService(db_session)
        
        # 分析用户画像
        profile = service._analyze_user_profile(user_id)
        
        # 生成现金回馈推荐
        cashback_recs = service._generate_cashback_recommendations(user_id, profile)
        
        assert isinstance(cashback_recs, list)
        if len(cashback_recs) > 0:
            rec = cashback_recs[0]
            assert rec["recommendation_type"] == RecommendationType.CASHBACK.value
            assert "title" in rec
            assert "reason" in rec
            assert "cashback_rate" in rec
        
        logger.info(f"生成 {len(cashback_recs)} 条现金回馈推荐")
    
    def test_recommendation_algorithm_points(self, test_user_data, db_session):
        """测试推荐算法 - 积分奖励推荐"""
        logger.info("测试积分奖励推荐算法...")
        
        user_id = test_user_data["user_id"]
        service = RecommendationsService(db_session)
        
        # 分析用户画像
        profile = service._analyze_user_profile(user_id)
        
        # 生成积分奖励推荐
        points_recs = service._generate_points_recommendations(user_id, profile)
        
        assert isinstance(points_recs, list)
        if len(points_recs) > 0:
            rec = points_recs[0]
            assert rec["recommendation_type"] == RecommendationType.POINTS.value
            assert "title" in rec
            assert "reason" in rec
            assert "points_rate" in rec
        
        logger.info(f"生成 {len(points_recs)} 条积分奖励推荐")
    
    def test_recommendation_algorithm_grace_period(self, test_user_data, db_session):
        """测试推荐算法 - 免息期推荐"""
        logger.info("测试免息期推荐算法...")
        
        user_id = test_user_data["user_id"]
        service = RecommendationsService(db_session)
        
        # 分析用户画像
        profile = service._analyze_user_profile(user_id)
        
        # 生成免息期推荐
        grace_recs = service._generate_grace_period_recommendations(user_id, profile)
        
        assert isinstance(grace_recs, list)
        if len(grace_recs) > 0:
            rec = grace_recs[0]
            assert rec["recommendation_type"] == RecommendationType.GRACE_PERIOD.value
            assert "title" in rec
            assert "reason" in rec
            assert "grace_period_days" in rec
        
        logger.info(f"生成 {len(grace_recs)} 条免息期推荐")
    
    def test_cleanup_expired_recommendations(self, test_user_data, db_session):
        """测试清理过期推荐"""
        logger.info("测试清理过期推荐...")
        
        user_id = test_user_data["user_id"]
        service = RecommendationsService(db_session)
        
        # 创建一个过期推荐
        expired_rec = DBRecommendation(
            id=uuid4(),
            user_id=user_id,
            title="过期推荐",
            bank_name="测试银行",
            card_name="测试卡",
            recommendation_type=RecommendationType.CASHBACK,
            recommendation_score=60,
            reason="测试",
            description="测试",
            status=RecommendationStatus.ACTIVE,
            created_at=datetime.utcnow() - timedelta(days=31),  # 31天前
            expires_at=datetime.utcnow() - timedelta(days=1)   # 昨天过期
        )
        
        db_session.add(expired_rec)
        db_session.commit()
        
        # 清理过期推荐
        service._cleanup_expired_recommendations(user_id)
        db_session.commit()
        
        # 验证推荐被标记为过期
        db_session.refresh(expired_rec)
        assert expired_rec.status == RecommendationStatus.EXPIRED
        
        logger.info("过期推荐清理成功")
    
    def test_recommendation_scoring(self, test_user_data, db_session):
        """测试推荐评分算法"""
        logger.info("测试推荐评分算法...")
        
        user_id = test_user_data["user_id"]
        service = RecommendationsService(db_session)
        
        # 生成推荐
        recommendations = service.generate_recommendations(user_id)
        
        for rec in recommendations:
            # 验证评分在合理范围内
            assert 0 <= rec.recommendation_score <= 100
            # 验证必要字段存在
            assert rec.title
            assert rec.bank_name
            assert rec.reason
        
        logger.info(f"推荐评分测试完成，共 {len(recommendations)} 条推荐")


@pytest.fixture(scope="session")
def db_session():
    """创建测试数据库会话"""
    from database import get_db
    
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"]) 