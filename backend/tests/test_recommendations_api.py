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
import requests
import json
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 测试配置
BASE_URL = "http://127.0.0.1:8000/api"
TEST_USER = {
    "username": "testuser003",
    "password": "TestPass123456"
}

class TestRecommendationsAPI:
    """推荐接口API测试类"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """获取认证令牌"""
        logger.info("开始用户登录获取认证令牌...")
        
        response = requests.post(f"{BASE_URL}/auth/login/username", json=TEST_USER)
        logger.info(f"登录响应状态: {response.status_code}")
        
        result = response.json()
        logger.info(f"登录响应: {result}")
        
        if response.status_code != 200 or not result.get("success", True):
            # 如果用户不存在，先注册
            logger.info("用户不存在，开始注册...")
            register_data = {
                "username": TEST_USER["username"],
                "email": "testuser003@example.com",
                "password": TEST_USER["password"],
                "nickname": "推荐测试用户003"
            }
            
            register_response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
            logger.info(f"注册响应状态: {register_response.status_code}")
            logger.info(f"注册响应: {register_response.json()}")
            
            if register_response.status_code == 200 or register_response.status_code == 201:
                # 注册成功后重新登录
                response = requests.post(f"{BASE_URL}/auth/login/username", json=TEST_USER)
                result = response.json()
                logger.info(f"重新登录响应: {result}")
        
        assert response.status_code == 200 and result.get("success", True), f"登录失败: {result}"
        
        # 处理不同的响应格式
        if result.get("data"):
            token = result["data"]["access_token"]
            user_id = result["data"]["user"]["id"]
        else:
            # 兼容老格式
            token = result.get("access_token")
            user_id = result.get("user", {}).get("id")
        
        logger.info(f"✅ 登录成功，用户ID: {user_id}")
        return {
            "token": token,
            "user_id": user_id,
            "headers": {"Authorization": f"Bearer {token}"}
        }
    
    @pytest.fixture(scope="class")
    def test_data_setup(self, auth_token):
        """设置测试数据"""
        headers = auth_token["headers"]
        
        # 创建测试信用卡
        card_data = {
            "card_name": "招商银行信用卡",
            "bank_name": "招商银行",
            "card_number": "4321123412341234",
            "cardholder_name": "推荐测试用户",
            "expiry_month": 12,
            "expiry_year": 2027,
            "cvv": "123",
            "credit_limit": 100000,
            "available_limit": 65000,
            "card_type": "visa",
            "billing_day": 5,
            "due_day": 25,
            "color": "#FF6B35",
            "notes": "测试推荐功能的信用卡"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/cards", json=card_data, headers=headers)
            if response.status_code == 201:
                card_result = response.json()
                card_id = card_result["data"]["id"]
                logger.info(f"✅ 创建测试信用卡成功，ID: {card_id}")
                
                # 创建一些交易记录
                transaction_data = {
                    "card_id": card_id,
                    "amount": 299.50,
                    "transaction_type": "expense",
                    "category": "dining",
                    "description": "测试餐饮消费",
                    "merchant_name": "美食餐厅",
                    "transaction_date": datetime.now().isoformat()
                }
                
                trans_response = requests.post(f"{BASE_URL}/transactions", json=transaction_data, headers=headers)
                if trans_response.status_code == 201:
                    logger.info("✅ 创建测试交易记录成功")
                
                return {"card_id": card_id}
        except Exception as e:
            logger.warning(f"创建测试数据失败: {str(e)}")
            return {}
    
    def test_01_user_profile_stats(self, auth_token):
        """测试获取用户画像分析"""
        logger.info("\n🧪 测试1: 获取用户画像分析")
        
        headers = auth_token["headers"]
        response = requests.get(f"{BASE_URL}/recommendations/stats/user-profile", headers=headers)
        
        logger.info(f"响应状态: {response.status_code}")
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert "data" in result
        
        profile_data = result["data"]
        logger.info(f"用户画像数据: {json.dumps(profile_data, indent=2, ensure_ascii=False)}")
        
        # 验证字段存在
        required_fields = [
            "total_cards", "total_limit", "used_limit", "utilization_rate",
            "monthly_spending", "top_categories", "avg_transaction_amount"
        ]
        for field in required_fields:
            assert field in profile_data, f"缺少字段: {field}"
        
        logger.info("✅ 用户画像分析测试通过")
    
    def test_02_generate_recommendations(self, auth_token, test_data_setup):
        """测试生成个性化推荐"""
        logger.info("\n🧪 测试2: 生成个性化推荐")
        
        headers = auth_token["headers"]
        response = requests.post(f"{BASE_URL}/recommendations/generate", headers=headers)
        
        logger.info(f"响应状态: {response.status_code}")
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert "data" in result
        
        recommendations = result["data"]
        logger.info(f"生成推荐数量: {len(recommendations)}")
        
        if len(recommendations) > 0:
            # 验证推荐结构
            rec = recommendations[0]
            required_fields = [
                "id", "title", "bank_name", "card_name", "recommendation_type",
                "recommendation_score", "reason", "description"
            ]
            for field in required_fields:
                assert field in rec, f"推荐缺少字段: {field}"
            
            assert 0 <= rec["recommendation_score"] <= 100
            
            logger.info(f"第一条推荐: {rec['title']} (评分: {rec['recommendation_score']})")
            logger.info(f"推荐理由: {rec['reason'][:100]}...")
        
        logger.info("✅ 个性化推荐生成测试通过")
    
    def test_03_get_recommendations_list(self, auth_token):
        """测试获取推荐列表"""
        logger.info("\n🧪 测试3: 获取推荐列表")
        
        headers = auth_token["headers"]
        response = requests.get(f"{BASE_URL}/recommendations/", headers=headers)
        
        logger.info(f"响应状态: {response.status_code}")
        assert response.status_code == 200
        
        result = response.json()
        logger.info(f"推荐列表响应: {result}")
        assert result["success"] is True
        assert "data" in result
        
        data = result["data"]
        assert "items" in data
        assert "pagination" in data
        
        pagination = data["pagination"]
        logger.info(f"推荐总数: {pagination['total']}, 当前页: {pagination['current_page']}")
        
        items = data["items"]
        logger.info(f"当前页推荐数量: {len(items)}")
        
        if len(items) > 0:
            logger.info(f"第一条推荐标题: {items[0]['title']}")
        
        logger.info("✅ 推荐列表获取测试通过")
    
    def test_04_get_recommendations_with_pagination(self, auth_token):
        """测试推荐列表分页功能"""
        logger.info("\n🧪 测试4: 推荐列表分页")
        
        headers = auth_token["headers"]
        
        # 测试分页参数
        response = requests.get(f"{BASE_URL}/recommendations/?page=1&page_size=5", headers=headers)
        
        logger.info(f"分页请求响应状态: {response.status_code}")
        assert response.status_code == 200
        
        result = response.json()
        logger.info(f"分页响应: {result}")
        assert result["success"] is True
        
        pagination = result["data"]["pagination"]
        assert pagination["current_page"] == 1
        assert pagination["page_size"] == 5
        
        logger.info(f"分页信息: 第{pagination['current_page']}页，每页{pagination['page_size']}条")
        logger.info("✅ 分页功能测试通过")
    
    def test_05_get_recommendations_with_search(self, auth_token):
        """测试推荐列表搜索功能"""
        logger.info("\n🧪 测试5: 推荐列表搜索")
        
        headers = auth_token["headers"]
        
        # 测试搜索功能
        search_keyword = "招商"
        response = requests.get(f"{BASE_URL}/recommendations/?keyword={search_keyword}", headers=headers)
        
        logger.info(f"搜索请求响应状态: {response.status_code}")
        assert response.status_code == 200
        
        result = response.json()
        logger.info(f"搜索响应: {result}")
        assert result["success"] is True
        
        logger.info(f"搜索关键词 '{search_keyword}' 的结果数量: {len(result['data']['items'])}")
        logger.info("✅ 搜索功能测试通过")
    
    def test_06_get_recommendation_detail(self, auth_token):
        """测试获取推荐详情"""
        logger.info("\n🧪 测试6: 获取推荐详情")
        
        headers = auth_token["headers"]
        
        # 先获取推荐列表
        list_response = requests.get(f"{BASE_URL}/recommendations/", headers=headers)
        assert list_response.status_code == 200
        
        items = list_response.json()["data"]["items"]
        if len(items) == 0:
            logger.warning("没有推荐数据，跳过详情测试")
            return
        
        # 获取第一个推荐的详情
        rec_id = items[0]["id"]
        response = requests.get(f"{BASE_URL}/recommendations/{rec_id}", headers=headers)
        
        logger.info(f"推荐详情响应状态: {response.status_code}")
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        assert "data" in result
        
        rec_detail = result["data"]
        logger.info(f"推荐详情标题: {rec_detail['title']}")
        logger.info(f"推荐银行: {rec_detail['bank_name']}")
        logger.info(f"推荐评分: {rec_detail['recommendation_score']}")
        
        logger.info("✅ 推荐详情获取测试通过")
    
    def test_07_submit_recommendation_feedback(self, auth_token):
        """测试提交推荐反馈"""
        logger.info("\n🧪 测试7: 提交推荐反馈")
        
        headers = auth_token["headers"]
        
        # 先获取推荐列表
        list_response = requests.get(f"{BASE_URL}/recommendations/", headers=headers)
        assert list_response.status_code == 200
        
        items = list_response.json()["data"]["items"]
        if len(items) == 0:
            logger.warning("没有推荐数据，跳过反馈测试")
            return
        
        # 对第一个推荐提交反馈
        rec_id = items[0]["id"]
        feedback = "interested"
        
        response = requests.put(
            f"{BASE_URL}/recommendations/{rec_id}/feedback?feedback={feedback}",
            headers=headers
        )
        
        logger.info(f"反馈提交响应状态: {response.status_code}")
        assert response.status_code == 200
        
        result = response.json()
        assert result["success"] is True
        
        logger.info(f"反馈类型: {feedback}")
        logger.info(f"反馈结果: {result['message']}")
        logger.info("✅ 推荐反馈提交测试通过")
    
    def test_08_error_handling_unauthorized(self):
        """测试未授权访问的错误处理"""
        logger.info("\n🧪 测试8: 未授权访问错误处理")
        
        # 不带认证头的请求
        response = requests.get(f"{BASE_URL}/recommendations/")
        
        logger.info(f"未授权请求响应状态: {response.status_code}")
        # FastAPI可能返回401或403，都表示未授权
        assert response.status_code in [401, 403]
        
        logger.info("✅ 未授权访问错误处理测试通过")
    
    def test_09_error_handling_not_found(self, auth_token):
        """测试不存在资源的错误处理"""
        logger.info("\n🧪 测试9: 不存在资源错误处理")
        
        headers = auth_token["headers"]
        
        # 请求不存在的推荐ID
        fake_id = "12345678-1234-1234-1234-123456789abc"
        response = requests.get(f"{BASE_URL}/recommendations/{fake_id}", headers=headers)
        
        logger.info(f"不存在资源请求响应状态: {response.status_code}")
        assert response.status_code == 200  # 按照API设计，返回200但success为false
        
        result = response.json()
        assert result["success"] is False
        assert "不存在" in result["message"]
        
        logger.info(f"错误消息: {result['message']}")
        logger.info("✅ 不存在资源错误处理测试通过")
    
    def test_10_recommendation_algorithm_validation(self, auth_token):
        """测试推荐算法的有效性"""
        logger.info("\n🧪 测试10: 推荐算法有效性验证")
        
        headers = auth_token["headers"]
        
        # 生成推荐
        response = requests.post(f"{BASE_URL}/recommendations/generate", headers=headers)
        assert response.status_code == 200
        
        recommendations = response.json()["data"]
        
        for i, rec in enumerate(recommendations[:3]):  # 检查前3条推荐
            logger.info(f"\n推荐 {i+1}:")
            logger.info(f"  标题: {rec['title']}")
            logger.info(f"  银行: {rec['bank_name']}")
            logger.info(f"  类型: {rec['recommendation_type']}")
            logger.info(f"  评分: {rec['recommendation_score']}")
            logger.info(f"  理由: {rec['reason'][:80]}...")
            
            # 验证推荐质量
            assert len(rec['title']) > 0
            assert len(rec['reason']) > 20  # 推荐理由应该有一定长度
            assert rec['recommendation_score'] > 0  # 评分应该大于0
        
        logger.info("✅ 推荐算法有效性验证通过")


def run_tests():
    """运行所有测试"""
    logger.info("🚀 开始运行推荐接口测试...")
    
    try:
        # 运行pytest
        exit_code = pytest.main([
            __file__,
            "-v",
            "--tb=short",
            "--capture=no",
            "-s"
        ])
        
        if exit_code == 0:
            logger.info("🎉 所有测试通过！")
        else:
            logger.error("❌ 部分测试失败")
        
        return exit_code
    
    except Exception as e:
        logger.error(f"❌ 测试运行失败: {str(e)}")
        return 1


if __name__ == "__main__":
    run_tests() 