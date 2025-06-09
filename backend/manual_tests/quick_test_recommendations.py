#!/usr/bin/env python3
"""
快速测试推荐接口
"""

import requests
import json

def test_recommendations():
    """测试推荐接口"""
    base_url = "http://127.0.0.1:8000/api"
    
    print("🚀 开始测试推荐接口...")
    
    # 1. 登录获取令牌
    print("\n1. 用户登录...")
    login_data = {
        "username": "user123",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login/username", json=login_data)
        print(f"登录响应状态: {response.status_code}")
        
        if response.status_code != 200:
            print(f"登录失败: {response.text}")
            return
        
        result = response.json()
        token = result["data"]["access_token"]
        print("✅ 登录成功，获取到JWT令牌")
        
        # 2. 测试生成推荐
        print("\n2. 生成个性化推荐...")
        headers = {"Authorization": f"Bearer {token}"}
        
        rec_response = requests.post(f"{base_url}/recommendations/generate", headers=headers)
        print(f"生成推荐响应状态: {rec_response.status_code}")
        
        if rec_response.status_code == 200:
            rec_result = rec_response.json()
            recommendations = rec_result["data"]
            print(f"✅ 成功生成 {len(recommendations)} 条推荐")
            
            # 显示前3条推荐
            for i, rec in enumerate(recommendations[:3]):
                print(f"\n推荐 {i+1}:")
                print(f"  标题: {rec['title']}")
                print(f"  银行: {rec['bank_name']}")
                print(f"  卡片: {rec['card_name']}")
                print(f"  分数: {rec['recommendation_score']}")
                print(f"  推荐理由: {rec['reason'][:100]}...")
        else:
            print(f"❌ 生成推荐失败: {rec_response.text}")
            return
        
        # 3. 测试获取推荐列表
        print("\n3. 获取推荐列表...")
        list_response = requests.get(f"{base_url}/recommendations/", headers=headers)
        print(f"获取列表响应状态: {list_response.status_code}")
        
        if list_response.status_code == 200:
            list_result = list_response.json()
            print(f"✅ 成功获取推荐列表，共 {list_result['data']['pagination']['total']} 条")
        else:
            print(f"❌ 获取列表失败: {list_response.text}")
        
        # 4. 测试用户画像分析
        print("\n4. 获取用户画像分析...")
        profile_response = requests.get(f"{base_url}/recommendations/stats/user-profile", headers=headers)
        print(f"用户画像响应状态: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            profile_result = profile_response.json()
            profile_data = profile_result["data"]
            print("✅ 用户画像分析成功:")
            print(f"  月消费金额: {profile_data.get('monthly_spending', 0)}")
            print(f"  信用卡数量: {profile_data.get('card_count', 0)}")
            print(f"  额度使用率: {profile_data.get('credit_utilization', 0)}%")
        else:
            print(f"❌ 获取用户画像失败: {profile_response.text}")
            
        print("\n🎉 推荐接口测试完成!")
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接服务器失败，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    test_recommendations() 