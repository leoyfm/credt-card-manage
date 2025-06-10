"""
智能推荐服务API测试套件

使用新测试框架v2.0进行智能推荐功能的全面测试
包括推荐引擎、用户反馈、个性化推荐等功能
"""

import pytest
from tests.framework import (
    test_suite, api_test, with_user, with_cards, with_transactions,
    performance_test, stress_test
)


@test_suite("智能推荐API")
class RecommendationTests:
    """智能推荐功能测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=2)
    @with_transactions(count=20)
    def test_get_card_recommendations(self, api, user, cards, transactions):
        """测试获取信用卡推荐"""
        api.get("/api/v1/user/recommendations/cards").should.succeed().with_data_structure({
            "recommendations": list,
            "total_count": int,
            "recommendation_reasons": list
        })
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=10)
    def test_get_spending_recommendations(self, api, user, cards, transactions):
        """测试获取消费优化推荐"""
        api.get("/api/v1/user/recommendations/spending").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=2)
    def test_get_fee_optimization_recommendations(self, api, user, cards):
        """测试获取年费优化推荐"""
        api.get("/api/v1/user/recommendations/fee-optimization").should.succeed()
    
    @api_test
    @with_user
    @with_cards(count=1)
    @with_transactions(count=15)
    def test_get_category_recommendations(self, api, user, cards, transactions):
        """测试获取分类消费推荐"""
        api.get("/api/v1/user/recommendations/categories").should.succeed()
    
    @api_test
    @with_user
    def test_get_personalized_recommendations(self, api, user):
        """测试获取个性化推荐"""
        api.get("/api/v1/user/recommendations/personalized").should.succeed()


@test_suite("推荐反馈管理")  
class RecommendationFeedbackTests:
    """推荐反馈管理测试套件"""
    
    @api_test
    @with_user
    def test_submit_recommendation_feedback(self, api, user):
        """测试提交推荐反馈"""
        feedback_data = {
            "recommendation_id": "rec_123456",
            "feedback_type": "helpful",
            "rating": 5,
            "comment": "这个推荐很有用",
            "action_taken": "applied"
        }
        
        api.post("/api/v1/user/recommendations/feedback", data=feedback_data).should.succeed()
    
    @api_test
    @with_user
    def test_get_feedback_history(self, api, user):
        """测试获取反馈历史"""
        api.get("/api/v1/user/recommendations/feedback/history").should.succeed()
    
    @api_test
    @with_user
    def test_update_feedback(self, api, user):
        """测试更新反馈"""
        # 先提交反馈
        create_response = api.post("/api/v1/user/recommendations/feedback", data={
            "recommendation_id": "rec_123456",
            "feedback_type": "helpful",
            "rating": 4
        }).should.succeed()
        
        feedback_id = create_response.data['id']
        
        # 更新反馈
        api.put(f"/api/v1/user/recommendations/feedback/{feedback_id}", data={
            "rating": 5,
            "comment": "更新后的评价"
        }).should.succeed()


@test_suite("推荐算法配置")
class RecommendationAlgorithmTests:
    """推荐算法配置测试套件"""
    
    @api_test
    @with_user
    def test_get_recommendation_preferences(self, api, user):
        """测试获取推荐偏好设置"""
        api.get("/api/v1/user/recommendations/preferences").should.succeed()
    
    @api_test
    @with_user
    def test_update_recommendation_preferences(self, api, user):
        """测试更新推荐偏好设置"""
        preferences_data = {
            "card_recommendation_enabled": True,
            "spending_advice_enabled": True,
            "fee_optimization_enabled": True,
            "notification_frequency": "weekly",
            "preferred_categories": ["餐饮", "购物", "交通"]
        }
        
        api.put("/api/v1/user/recommendations/preferences", data=preferences_data).should.succeed()
    
    @api_test
    @with_user
    def test_get_recommendation_weights(self, api, user):
        """测试获取推荐权重配置"""
        api.get("/api/v1/user/recommendations/weights").should.succeed()
    
    @api_test
    @with_user
    def test_update_recommendation_weights(self, api, user):
        """测试更新推荐权重配置"""
        weights_data = {
            "spending_pattern_weight": 0.4,
            "cashback_rate_weight": 0.3,
            "annual_fee_weight": 0.2,
            "user_preference_weight": 0.1
        }
        
        api.put("/api/v1/user/recommendations/weights", data=weights_data).should.succeed()


@test_suite("推荐权限测试")
class RecommendationPermissionTests:
    """推荐权限验证测试套件"""
    
    @api_test
    def test_unauthenticated_access(self, api):
        """测试未认证访问推荐接口"""
        api.get("/api/v1/user/recommendations/cards").should.fail(401)
    
    @api_test
    @with_user
    def test_unauthorized_feedback_access(self, api, user):
        """测试未授权访问他人反馈"""
        other_feedback_id = "11111111-1111-1111-1111-111111111111"
        api.get(f"/api/v1/user/recommendations/feedback/{other_feedback_id}").should.fail(403)


@test_suite("推荐性能测试")
class RecommendationPerformanceTests:
    """推荐服务性能测试套件"""
    
    @performance_test
    @with_user
    @with_cards(count=5)
    @with_transactions(count=100)
    def test_recommendations_generation_performance(self, api, user, cards, transactions):
        """测试推荐生成性能"""
        api.get("/api/v1/user/recommendations/cards").should.succeed().complete_within(seconds=2.0)
    
    @performance_test
    @with_user
    def test_preferences_update_performance(self, api, user):
        """测试偏好更新性能"""
        preferences_data = {
            "card_recommendation_enabled": True,
            "spending_advice_enabled": True,
            "preferred_categories": ["餐饮", "购物"]
        }
        
        api.put("/api/v1/user/recommendations/preferences", data=preferences_data).should.succeed().complete_within(seconds=0.5)
    
    @stress_test(concurrent_users=10, duration=30)
    @with_user
    def test_recommendations_concurrent_access(self, api, user):
        """测试推荐并发访问"""
        api.get("/api/v1/user/recommendations/personalized").should.succeed()


@test_suite("推荐业务逻辑测试")
class RecommendationBusinessLogicTests:
    """推荐业务逻辑测试套件"""
    
    @api_test
    @with_user
    @with_cards(count=1)
    def test_spending_pattern_analysis(self, api, user, cards):
        """测试消费模式分析"""
        card = cards[0] if isinstance(cards, list) else cards
        
        # 模拟不同类别的消费
        categories = ["餐饮", "购物", "交通", "娱乐"]
        for i, category in enumerate(categories):
            for j in range(5):  # 每个类别5笔交易
                api.post("/api/v1/user/transactions/create", data={
                    "card_id": card['id'],
                    "transaction_type": "expense",
                    "amount": 100.00 * (i + 1),  # 不同金额
                    "description": f"{category}消费{j+1}",
                    "merchant_category": category
                }).should.succeed()
        
        # 获取基于消费模式的推荐
        api.get("/api/v1/user/recommendations/spending").should.succeed()
    
    @api_test
    @with_user
    def test_recommendation_filtering(self, api, user):
        """测试推荐过滤功能"""
        # 按类型过滤推荐
        api.get("/api/v1/user/recommendations/cards?type=cashback").should.succeed()
        api.get("/api/v1/user/recommendations/cards?type=travel").should.succeed()
        
        # 按评分过滤推荐
        api.get("/api/v1/user/recommendations/cards?min_rating=4.0").should.succeed()
    
    @api_test
    @with_user
    def test_recommendation_sorting(self, api, user):
        """测试推荐排序功能"""
        # 按相关性排序
        api.get("/api/v1/user/recommendations/cards?sort=relevance").should.succeed()
        
        # 按评分排序
        api.get("/api/v1/user/recommendations/cards?sort=rating&order=desc").should.succeed()
    
    @api_test
    @with_user
    def test_recommendation_explanation(self, api, user):
        """测试推荐解释功能"""
        response = api.get("/api/v1/user/recommendations/cards?include_explanation=true").should.succeed()
        
        # 验证推荐包含解释信息
        recommendations = response.data.get('recommendations', [])
        if recommendations:
            first_recommendation = recommendations[0]
            assert 'explanation' in first_recommendation, "推荐应该包含解释信息"
            assert 'reasons' in first_recommendation, "推荐应该包含推荐理由"
    
    @api_test
    @with_user
    def test_feedback_impact_on_recommendations(self, api, user):
        """测试反馈对推荐的影响"""
        # 获取初始推荐
        initial_response = api.get("/api/v1/user/recommendations/cards").should.succeed()
        
        # 提交负面反馈
        if initial_response.data.get('recommendations'):
            first_rec = initial_response.data['recommendations'][0]
            api.post("/api/v1/user/recommendations/feedback", data={
                "recommendation_id": first_rec.get('id'),
                "feedback_type": "not_helpful",
                "rating": 1
            }).should.succeed()
        
        # 获取更新后的推荐（应该有所不同）
        updated_response = api.get("/api/v1/user/recommendations/cards").should.succeed()
    
    @api_test
    @with_user
    def test_recommendation_diversity(self, api, user):
        """测试推荐多样性"""
        response = api.get("/api/v1/user/recommendations/cards?limit=10").should.succeed()
        
        recommendations = response.data.get('recommendations', [])
        if len(recommendations) > 1:
            # 验证推荐的多样性（不同银行、不同类型等）
            banks = set()
            types = set()
            for rec in recommendations:
                if 'bank_name' in rec:
                    banks.add(rec['bank_name'])
                if 'card_type' in rec:
                    types.add(rec['card_type'])
            
            # 应该有多样性
            assert len(banks) > 1 or len(types) > 1, "推荐应该具有多样性"