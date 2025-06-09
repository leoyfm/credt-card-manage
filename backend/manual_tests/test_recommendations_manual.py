"""
推荐功能手动测试脚本

测试智能推荐系统的各个功能点。
"""

import requests
import json
from typing import Dict, Any
from uuid import UUID

# 测试配置
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": "testuser002",
    "password": "TestPass123456"
}

class RecommendationsTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.token = None
        self.user_id = None
        
    def login(self) -> bool:
        """用户登录获取token"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login/username",
                json={
                    "username": TEST_USER["username"],
                    "password": TEST_USER["password"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.token = result["data"]["access_token"]
                    self.user_id = result["data"]["user"]["id"]
                    print(f"✅ 登录成功 - User ID: {self.user_id}")
                    return True
            
            print(f"❌ 登录失败: {response.text}")
            return False
            
        except Exception as e:
            print(f"❌ 登录异常: {str(e)}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_user_profile_analysis(self) -> bool:
        """测试用户画像分析"""
        try:
            print("\n=== 测试用户画像分析 ===")
            
            response = requests.get(
                f"{self.base_url}/recommendations/stats/user-profile",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    profile = result["data"]
                    print("✅ 用户画像分析成功")
                    print(f"   信用卡数量: {profile.get('total_cards', 0)}")
                    print(f"   总额度: {profile.get('total_limit', 0)}元")
                    print(f"   已用额度: {profile.get('used_limit', 0)}元")
                    print(f"   使用率: {profile.get('utilization_rate', 0):.1f}%")
                    print(f"   月均消费: {profile.get('monthly_spending', 0):.0f}元")
                    print(f"   主要消费类别: {[cat[0].value if hasattr(cat[0], 'value') else str(cat[0]) for cat in profile.get('top_categories', [])]}")
                    print(f"   偏好现金回馈: {profile.get('prefers_cashback', False)}")
                    print(f"   偏好积分奖励: {profile.get('prefers_points', False)}")
                    print(f"   需要更高额度: {profile.get('needs_higher_limit', False)}")
                    print(f"   需要长免息期: {profile.get('needs_longer_grace_period', False)}")
                    return True
                else:
                    print(f"❌ 用户画像分析失败: {result.get('message')}")
            else:
                print(f"❌ 用户画像分析请求失败: {response.status_code} - {response.text}")
            
            return False
            
        except Exception as e:
            print(f"❌ 用户画像分析异常: {str(e)}")
            return False
    
    def test_generate_recommendations(self) -> bool:
        """测试生成个性化推荐"""
        try:
            print("\n=== 测试生成个性化推荐 ===")
            
            response = requests.post(
                f"{self.base_url}/recommendations/generate",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    recommendations = result["data"]
                    print(f"✅ 生成个性化推荐成功 - 共{len(recommendations)}条推荐")
                    
                    for i, rec in enumerate(recommendations, 1):
                        print(f"\n推荐 {i}:")
                        print(f"   卡片: {rec['bank_name']} {rec['card_name']}")
                        print(f"   类型: {rec['recommendation_type']}")
                        print(f"   标题: {rec['title']}")
                        print(f"   评分: {rec['recommendation_score']}分")
                        print(f"   年费: {rec['annual_fee']}元")
                        print(f"   额度范围: {rec['credit_limit_range']}")
                        print(f"   申请难度: {rec['approval_difficulty']}/5")
                        print(f"   是否精选: {rec['is_featured']}")
                        print(f"   匹配原因: {rec['match_reasons']}")
                        print(f"   优点: {rec['pros']}")
                        print(f"   缺点: {rec['cons']}")
                    
                    return True
                else:
                    print(f"❌ 生成推荐失败: {result.get('message')}")
            else:
                print(f"❌ 生成推荐请求失败: {response.status_code} - {response.text}")
            
            return False
            
        except Exception as e:
            print(f"❌ 生成推荐异常: {str(e)}")
            return False
    
    def test_get_recommendations_list(self) -> list:
        """测试获取推荐列表"""
        try:
            print("\n=== 测试获取推荐列表 ===")
            
            response = requests.get(
                f"{self.base_url}/recommendations/",
                headers=self.get_headers(),
                params={
                    "page": 1,
                    "page_size": 10,
                    "keyword": ""
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    items = result["data"]["items"]
                    pagination = result["data"]["pagination"]
                    print(f"✅ 获取推荐列表成功")
                    print(f"   总数: {pagination['total']}")
                    print(f"   当前页: {pagination['current_page']}")
                    print(f"   每页数量: {pagination['page_size']}")
                    print(f"   总页数: {pagination['total_pages']}")
                    
                    print("\n推荐列表:")
                    for i, rec in enumerate(items, 1):
                        print(f"   {i}. {rec['bank_name']} {rec['card_name']} - {rec['recommendation_score']}分")
                    
                    return items
                else:
                    print(f"❌ 获取推荐列表失败: {result.get('message')}")
            else:
                print(f"❌ 获取推荐列表请求失败: {response.status_code} - {response.text}")
            
            return []
            
        except Exception as e:
            print(f"❌ 获取推荐列表异常: {str(e)}")
            return []
    
    def test_get_recommendation_detail(self, recommendation_id: str) -> bool:
        """测试获取推荐详情"""
        try:
            print(f"\n=== 测试获取推荐详情 ===")
            
            response = requests.get(
                f"{self.base_url}/recommendations/{recommendation_id}",
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    rec = result["data"]
                    print("✅ 获取推荐详情成功")
                    print(f"   推荐ID: {rec['id']}")
                    print(f"   卡片: {rec['bank_name']} {rec['card_name']}")
                    print(f"   描述: {rec['description']}")
                    print(f"   特色功能: {rec['features']}")
                    print(f"   查看次数: {rec['view_count']}")
                    print(f"   状态: {rec['status']}")
                    return True
                else:
                    print(f"❌ 获取推荐详情失败: {result.get('message')}")
            else:
                print(f"❌ 获取推荐详情请求失败: {response.status_code} - {response.text}")
            
            return False
            
        except Exception as e:
            print(f"❌ 获取推荐详情异常: {str(e)}")
            return False
    
    def test_submit_feedback(self, recommendation_id: str, feedback: str) -> bool:
        """测试提交推荐反馈"""
        try:
            print(f"\n=== 测试提交推荐反馈 ===")
            
            response = requests.put(
                f"{self.base_url}/recommendations/{recommendation_id}/feedback",
                headers=self.get_headers(),
                params={"feedback": feedback}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print(f"✅ 提交推荐反馈成功 - 反馈: {feedback}")
                    return True
                else:
                    print(f"❌ 提交推荐反馈失败: {result.get('message')}")
            else:
                print(f"❌ 提交推荐反馈请求失败: {response.status_code} - {response.text}")
            
            return False
            
        except Exception as e:
            print(f"❌ 提交推荐反馈异常: {str(e)}")
            return False
    
    def test_search_recommendations(self) -> bool:
        """测试搜索推荐"""
        try:
            print("\n=== 测试搜索推荐 ===")
            
            # 搜索银行名称
            response = requests.get(
                f"{self.base_url}/recommendations/",
                headers=self.get_headers(),
                params={
                    "page": 1,
                    "page_size": 5,
                    "keyword": "招商"
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    items = result["data"]["items"]
                    print(f"✅ 搜索推荐成功 - 关键词'招商'，找到{len(items)}条结果")
                    
                    for rec in items:
                        print(f"   {rec['bank_name']} {rec['card_name']}")
                    
                    return True
                else:
                    print(f"❌ 搜索推荐失败: {result.get('message')}")
            else:
                print(f"❌ 搜索推荐请求失败: {response.status_code} - {response.text}")
            
            return False
            
        except Exception as e:
            print(f"❌ 搜索推荐异常: {str(e)}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始推荐功能测试")
        
        if not self.login():
            print("❌ 无法登录，测试终止")
            return
        
        # 测试计数
        total_tests = 0
        passed_tests = 0
        
        # 1. 测试用户画像分析
        total_tests += 1
        if self.test_user_profile_analysis():
            passed_tests += 1
        
        # 2. 测试生成个性化推荐
        total_tests += 1
        if self.test_generate_recommendations():
            passed_tests += 1
        
        # 3. 测试获取推荐列表
        total_tests += 1
        recommendations = self.test_get_recommendations_list()
        if recommendations:
            passed_tests += 1
        
        # 4. 测试获取推荐详情
        if recommendations:
            total_tests += 1
            first_rec_id = recommendations[0]["id"]
            if self.test_get_recommendation_detail(first_rec_id):
                passed_tests += 1
            
            # 5. 测试提交反馈
            total_tests += 1
            if self.test_submit_feedback(first_rec_id, "interested"):
                passed_tests += 1
        
        # 6. 测试搜索功能
        total_tests += 1
        if self.test_search_recommendations():
            passed_tests += 1
        
        # 输出测试结果
        print(f"\n📊 测试完成")
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {total_tests - passed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        
        if passed_tests == total_tests:
            print("🎉 所有测试通过！")
        else:
            print("⚠️  部分测试失败，请检查日志")


if __name__ == "__main__":
    tester = RecommendationsTester()
    tester.run_all_tests() 