#!/usr/bin/env python3
"""
推荐模块API测试脚本

测试推荐模块的所有API接口功能
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import httpx
from app.core.config import settings


class RecommendationAPITester:
    """推荐API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.access_token = None
        self.user_id = None
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def login(self, username: str = "testuser_72164f72", password: str = "testpass123"):
        """用户登录获取访问令牌"""
        print("🔐 用户登录...")
        
        login_data = {
            "username": username,
            "password": password
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/public/auth/login/username",
                json=login_data
            )
            
            print(f"登录请求状态码: {response.status_code}")
            print(f"登录响应内容: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    self.access_token = result["data"]["access_token"]
                    self.user_id = result["data"]["user_id"]
                    print(f"✅ 登录成功，用户ID: {self.user_id}")
                    return True
                else:
                    print(f"❌ 登录失败: {result.get('message', '未知错误')}")
                    return False
            else:
                print(f"❌ 登录请求失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 登录异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_headers(self):
        """获取请求头"""
        if not self.access_token:
            raise ValueError("未登录，请先调用login方法")
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    async def test_get_available_types(self):
        """测试获取可用推荐类型"""
        print("\n📋 测试获取可用推荐类型...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/user/recommendations/types/available",
                headers=self.get_headers()
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if result.get("success"):
                    types = result.get("data", [])
                    print(f"✅ 获取到{len(types)}种推荐类型")
                    for i, type_name in enumerate(types, 1):
                        print(f"   {i}. {type_name}")
                    return True
                else:
                    print(f"❌ 获取失败: {result.get('message')}")
                    return False
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"响应: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return False
    
    async def test_get_available_actions(self):
        """测试获取可用用户行动"""
        print("\n🎯 测试获取可用用户行动...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/user/recommendations/actions/available",
                headers=self.get_headers()
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if result.get("success"):
                    actions = result.get("data", [])
                    print(f"✅ 获取到{len(actions)}种用户行动")
                    for i, action in enumerate(actions, 1):
                        print(f"   {i}. {action}")
                    return True
                else:
                    print(f"❌ 获取失败: {result.get('message')}")
                    return False
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"响应: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return False
    
    async def test_get_smart_recommendations(self):
        """测试获取智能推荐"""
        print("\n🧠 测试获取智能推荐...")
        
        try:
            params = {
                "limit": 5,
                "include_history": False
            }
            
            response = await self.client.get(
                f"{self.base_url}/api/v1/user/recommendations/smart",
                headers=self.get_headers(),
                params=params
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if result.get("success"):
                    recommendations = result.get("data", [])
                    print(f"✅ 生成了{len(recommendations)}条智能推荐")
                    
                    for i, rec in enumerate(recommendations, 1):
                        print(f"   {i}. {rec.get('title')} ({rec.get('recommendation_type')})")
                        print(f"      内容: {rec.get('content')[:50]}...")
                    
                    return recommendations
                else:
                    print(f"❌ 获取失败: {result.get('message')}")
                    return []
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"响应: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return []
    
    async def test_get_recommendation_history(self):
        """测试获取推荐历史"""
        print("\n📚 测试获取推荐历史...")
        
        try:
            params = {
                "page": 1,
                "page_size": 10
            }
            
            response = await self.client.get(
                f"{self.base_url}/api/v1/user/recommendations/history",
                headers=self.get_headers(),
                params=params
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if result.get("success"):
                    data = result.get("data", [])
                    pagination = result.get("pagination", {})
                    # 如果data是列表，说明是直接的推荐记录列表
                    if isinstance(data, list):
                        items = data
                    else:
                        # 如果data是对象，尝试获取items字段
                        items = data.get("items", [])
                    
                    print(f"✅ 查询到{len(items)}条推荐历史")
                    print(f"   总数: {pagination.get('total', 0)}")
                    print(f"   当前页: {pagination.get('current_page', 1)}")
                    
                    for i, rec in enumerate(items, 1):
                        print(f"   {i}. {rec.get('title')} - {rec.get('status')}")
                    
                    return items
                else:
                    print(f"❌ 获取失败: {result.get('message')}")
                    return []
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"响应: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return []
    
    async def test_submit_feedback(self, recommendation_id: str):
        """测试提交推荐反馈"""
        print(f"\n💬 测试提交推荐反馈 (ID: {recommendation_id})...")
        
        try:
            feedback_data = {
                "user_action": "accepted",
                "feedback": "这个推荐很有用，我会考虑采纳"
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/user/recommendations/{recommendation_id}/feedback",
                headers=self.get_headers(),
                json=feedback_data
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if result.get("success"):
                    rec = result.get("data", {})
                    print(f"✅ 反馈提交成功")
                    print(f"   用户行动: {rec.get('user_action')}")
                    print(f"   状态: {rec.get('status')}")
                    return True
                else:
                    print(f"❌ 提交失败: {result.get('message')}")
                    return False
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"响应: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return False
    
    async def test_get_recommendation_stats(self):
        """测试获取推荐统计"""
        print("\n📊 测试获取推荐统计...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/user/recommendations/stats/overview",
                headers=self.get_headers()
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if result.get("success"):
                    stats = result.get("data", {})
                    print(f"✅ 获取推荐统计成功")
                    print(f"   总推荐数: {stats.get('total_recommendations', 0)}")
                    print(f"   待处理: {stats.get('pending_recommendations', 0)}")
                    print(f"   已接受: {stats.get('accepted_recommendations', 0)}")
                    print(f"   已拒绝: {stats.get('rejected_recommendations', 0)}")
                    
                    type_dist = stats.get('type_distribution', {})
                    if type_dist:
                        print("   类型分布:")
                        for type_name, count in type_dist.items():
                            print(f"     - {type_name}: {count}")
                    
                    return True
                else:
                    print(f"❌ 获取失败: {result.get('message')}")
                    return False
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"响应: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return False
    
    async def test_evaluate_rules(self):
        """测试评估推荐规则"""
        print("\n⚙️ 测试评估推荐规则...")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/user/recommendations/evaluate-rules",
                headers=self.get_headers()
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
                
                if result.get("success"):
                    recommendations = result.get("data", [])
                    print(f"✅ 基于规则生成了{len(recommendations)}条推荐")
                    
                    for i, rec in enumerate(recommendations, 1):
                        print(f"   {i}. {rec.get('title')} ({rec.get('recommendation_type')})")
                    
                    return recommendations
                else:
                    print(f"❌ 评估失败: {result.get('message')}")
                    return []
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"响应: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ 测试异常: {str(e)}")
            return []


async def main():
    """主测试函数"""
    print("=" * 60)
    print("推荐模块API测试")
    print("=" * 60)
    print(f"测试服务器: http://localhost:8000")
    print("=" * 60)
    
    async with RecommendationAPITester() as tester:
        # 1. 用户登录
        if not await tester.login():
            print("❌ 登录失败，无法继续测试")
            return
        
        # 2. 测试获取可用推荐类型
        await tester.test_get_available_types()
        
        # 3. 测试获取可用用户行动
        await tester.test_get_available_actions()
        
        # 4. 测试获取智能推荐
        smart_recommendations = await tester.test_get_smart_recommendations()
        
        # 5. 测试获取推荐历史
        history_recommendations = await tester.test_get_recommendation_history()
        
        # 6. 测试评估推荐规则
        rule_recommendations = await tester.test_evaluate_rules()
        
        # 7. 如果有推荐记录，测试提交反馈
        all_recommendations = smart_recommendations + history_recommendations + rule_recommendations
        if all_recommendations:
            first_rec = all_recommendations[0]
            rec_id = first_rec.get("id")
            if rec_id:
                await tester.test_submit_feedback(rec_id)
        
        # 8. 测试获取推荐统计
        await tester.test_get_recommendation_stats()
        
        print("\n" + "=" * 60)
        print("🎉 推荐模块API测试完成!")
        print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程出现异常: {str(e)}")
        sys.exit(1) 