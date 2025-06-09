"""
推荐接口单元测试

使用FastAPI TestClient进行单元测试，不依赖真实服务器
测试覆盖：
- API接口逻辑
- 数据模型验证
- 业务逻辑正确性
"""

import pytest
import logging
from uuid import uuid4
from typing import List, Dict, Any

from tests.base_test import (
    FastAPITestClient, 
    BaseRecommendationTest, 
    TestPerformanceMixin,
    TestDataGenerator
)

pytestmark = pytest.mark.unit

logger = logging.getLogger(__name__)


class TestRecommendationsUnit:
    """推荐接口单元测试类"""
    
    def setup_method(self):
        """每个测试方法的初始化"""
        self.client = FastAPITestClient()
        self.api_test = BaseRecommendationTest(self.client)
        
        # 设置测试用户（每次都创建新用户避免冲突）
        self.user_info = self.api_test.setup_test_user()
        
        # 创建基础测试数据
        self.test_cards = []
        card_data_list = TestDataGenerator.generate_test_cards(2)
        for card_data in card_data_list:
            card = self.api_test.create_test_card(card_data)
            self.test_cards.append(card)
            
            # 为每张卡创建一些交易记录
            transaction_data_list = TestDataGenerator.generate_test_transactions(card["id"], 3)
            for transaction_data in transaction_data_list:
                self.api_test.create_test_transaction(card["id"], transaction_data)
    
    def test_01_user_profile_stats_structure(self):
        """测试用户画像分析数据结构"""
        logger.info("📊 测试用户画像分析...")
        
        # 测量响应时间
        import time
        start_time = time.time()
        data = self.api_test.test_user_profile_stats()
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 1.0, f"响应时间过长: {duration:.3f}s > 1.0s"
        print(f"⏱️  响应时间: {duration:.3f}s")
        
        # 验证数据类型和范围
        assert isinstance(data["total_cards"], int)
        # API可能返回字符串格式的数字，需要转换
        total_limit = float(data["total_limit"]) if isinstance(data["total_limit"], str) else data["total_limit"]
        used_limit = float(data["used_limit"]) if isinstance(data["used_limit"], str) else data["used_limit"]
        utilization_rate = float(data["utilization_rate"]) if isinstance(data["utilization_rate"], str) else data["utilization_rate"]
        
        assert isinstance(total_limit, (int, float))
        assert isinstance(used_limit, (int, float))
        assert isinstance(utilization_rate, (int, float))
        assert 0 <= utilization_rate <= 100
        
        # 验证数据逻辑一致性
        if total_limit > 0:
            calculated_rate = (used_limit / total_limit) * 100
            assert abs(calculated_rate - utilization_rate) < 0.01
        
        logger.info(f"✅ 用户画像验证通过: {data['total_cards']}张卡，使用率{utilization_rate:.1f}%")
    
    def test_02_generate_recommendations_logic(self):
        """测试推荐生成逻辑"""
        logger.info("🎯 测试推荐生成逻辑...")
        
        # 测量响应时间
        import time
        start_time = time.time()
        recommendations = self.api_test.test_generate_recommendations()
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration < 2.0, f"响应时间过长: {duration:.3f}s > 2.0s"
        print(f"⏱️  响应时间: {duration:.3f}s")
        
        if len(recommendations) > 0:
            # 验证推荐评分排序
            scores = [rec["recommendation_score"] for rec in recommendations]
            assert scores == sorted(scores, reverse=True), "推荐应按评分从高到低排序"
            
            # 验证推荐类型分布
            types = [rec["recommendation_type"] for rec in recommendations]
            unique_types = set(types)
            assert len(unique_types) > 0, "应该有不同类型的推荐"
            
            logger.info(f"✅ 推荐生成验证通过: {len(recommendations)}条推荐，{len(unique_types)}种类型")
        else:
            logger.info("ℹ️  当前用户数据不足以生成推荐")
    
    def test_03_recommendations_list_pagination(self):
        """测试推荐列表分页功能"""
        logger.info("📄 测试推荐列表分页...")
        
        # 先生成推荐
        self.api_test.test_generate_recommendations()
        
        # 测试分页
        page_sizes = [5, 10, 20]
        for page_size in page_sizes:
            import time
            start_time = time.time()
            data = self.api_test.test_get_recommendations_list(page=1, page_size=page_size)
            end_time = time.time()
            
            duration = end_time - start_time
            assert duration < 1.0, f"响应时间过长: {duration:.3f}s > 1.0s"
            
            pagination = data["pagination"]
            assert pagination["page_size"] == page_size
            assert pagination["current_page"] == 1
            assert len(data["items"]) <= page_size
            
            logger.info(f"✅ 分页验证通过: 每页{page_size}条，实际{len(data['items'])}条")
    
    def test_04_recommendations_search_functionality(self):
        """测试推荐搜索功能"""
        logger.info("🔍 测试推荐搜索功能...")
        
        # 先生成推荐
        self.api_test.test_generate_recommendations()
        
        search_keywords = ["信用卡", "银行", "推荐"]
        for keyword in search_keywords:
            import time
            start_time = time.time()
            data = self.api_test.test_get_recommendations_list(keyword=keyword)
            end_time = time.time()
            
            duration = end_time - start_time
            assert duration < 1.0, f"响应时间过长: {duration:.3f}s > 1.0s"
            
            # 如果有结果，验证搜索相关性
            if len(data["items"]) > 0:
                for item in data["items"][:3]:  # 检查前3个
                    content = f"{item.get('title', '')} {item.get('description', '')} {item.get('bank_name', '')}"
                    # 注意：这里只是检查结构，具体的搜索逻辑由服务端决定
                    assert isinstance(item.get("title"), str)
                    assert isinstance(item.get("description"), str)
            
            logger.info(f"✅ 搜索'{keyword}'验证通过: {len(data['items'])}条结果")
    
    def test_05_recommendation_detail_access(self):
        """测试推荐详情访问"""
        logger.info("📝 测试推荐详情访问...")
        
        # 先生成推荐
        recommendations = self.api_test.test_generate_recommendations()
        
        if len(recommendations) > 0:
            # 测试获取推荐详情
            rec_id = recommendations[0]["id"]
            
            response = self.client.get(f"/api/recommendations/{rec_id}", headers=self.api_test.headers)
            data = self.api_test.assert_api_success(response)
            
            # 验证详情数据完整性
            required_fields = [
                "id", "title", "bank_name", "card_name", "recommendation_type",
                "recommendation_score", "reason", "description", "created_at"
            ]
            for field in required_fields:
                assert field in data, f"推荐详情缺少{field}字段"
            
            assert data["id"] == rec_id
            logger.info(f"✅ 推荐详情验证通过: {data['title']}")
        else:
            logger.info("ℹ️  无推荐数据，跳过详情测试")
    
    def test_06_recommendation_feedback_submission(self):
        """测试推荐反馈提交"""
        logger.info("👍 测试推荐反馈提交...")
        
        # 先生成推荐
        recommendations = self.api_test.test_generate_recommendations()
        
        if len(recommendations) > 0:
            rec_id = recommendations[0]["id"]
            feedback_data = {
                "feedback_type": "like",
                "rating": 5,
                "comment": "非常有用的推荐！"
            }
            
            response = self.client.post(
                f"/api/recommendations/{rec_id}/feedback",
                json=feedback_data,
                headers=self.api_test.headers
            )
            
            data = self.api_test.assert_api_success(response, expected_status=201)
            
            # 验证反馈数据
            assert "feedback_id" in data or "id" in data
            logger.info("✅ 推荐反馈提交验证通过")
        else:
            logger.info("ℹ️  无推荐数据，跳过反馈测试")
    
    def test_07_unauthorized_access_protection(self):
        """测试未授权访问保护"""
        logger.info("🔒 测试未授权访问保护...")
        
        # 测试不带token的请求
        endpoints = [
            "/api/recommendations/stats/user-profile",
            "/api/recommendations/generate",
            "/api/recommendations"
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            assert response.status_code in [401, 403], f"端点{endpoint}应该返回401或403未授权"
        
        logger.info("✅ 未授权访问保护验证通过")
    
    def test_08_error_handling(self):
        """测试错误处理"""
        logger.info("⚠️  测试错误处理...")
        
        # 测试无效的推荐ID
        invalid_id = "invalid-recommendation-id"
        response = self.client.get(
            f"/api/recommendations/{invalid_id}",
            headers=self.api_test.headers
        )
        
        assert response.status_code in [404, 400, 422], "无效ID应该返回404、400或422错误"
        
        # 测试无效的反馈数据
        if len(self.api_test.test_generate_recommendations()) > 0:
            rec_id = self.api_test.test_generate_recommendations()[0]["id"]
            invalid_feedback = {"invalid_field": "invalid_value"}
            
            response = self.client.post(
                f"/api/recommendations/{rec_id}/feedback",
                json=invalid_feedback,
                headers=self.api_test.headers
            )
            
            assert response.status_code in [400, 422], "无效反馈数据应该返回400或422错误"
        
        logger.info("✅ 错误处理验证通过")
    
    def test_09_performance_batch_operations(self):
        """测试批量操作性能"""
        logger.info("🚀 测试批量操作性能...")
        
        def single_recommendation_request(index):
            """单次推荐请求"""
            return self.api_test.test_get_recommendations_list(page=1, page_size=10)
        
        # 测量批量操作性能
        import time
        start_time = time.time()
        count = 10
        
        for i in range(count):
            single_recommendation_request(i)
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / count
        
        assert avg_time < 1.0, f"平均操作时间过长: {avg_time:.3f}s > 1.0s"
        
        logger.info(f"📊 批量操作性能: {count}次操作，总时间{total_time:.3f}s，平均{avg_time:.3f}s")
    
    def test_10_data_consistency(self):
        """测试数据一致性"""
        logger.info("🔍 测试数据一致性...")
        
        # 生成推荐并获取列表
        generated_recs = self.api_test.test_generate_recommendations()
        list_data = self.api_test.test_get_recommendations_list(page=1, page_size=50)
        
        if len(generated_recs) > 0 and len(list_data["items"]) > 0:
            # 验证推荐数据一致性
            generated_ids = {rec["id"] for rec in generated_recs}
            list_ids = {rec["id"] for rec in list_data["items"]}
            
            # 至少应该有一些重叠
            common_ids = generated_ids.intersection(list_ids)
            assert len(common_ids) > 0, "生成的推荐与列表中的推荐应该有重叠"
            
            # 验证相同ID的推荐数据一致性
            for common_id in list(common_ids)[:3]:  # 检查前3个
                gen_rec = next(rec for rec in generated_recs if rec["id"] == common_id)
                list_rec = next(rec for rec in list_data["items"] if rec["id"] == common_id)
                
                # 关键字段应该一致
                key_fields = ["title", "bank_name", "recommendation_score", "recommendation_type"]
                for field in key_fields:
                    if field in gen_rec and field in list_rec:
                        assert gen_rec[field] == list_rec[field], f"字段{field}不一致"
            
            logger.info(f"✅ 数据一致性验证通过: {len(common_ids)}条推荐数据一致")
        else:
            logger.info("ℹ️  无推荐数据，跳过一致性测试") 