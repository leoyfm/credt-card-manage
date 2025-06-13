#!/usr/bin/env python3
"""
测试管理员登录日志接口
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from tests.utils.api import APIClient

def test_login_logs_api():
    """测试登录日志API"""
    print("🧪 测试管理员登录日志接口...")
    
    try:
        # 1. 登录管理员用户
        print("\n1. 登录管理员用户...")
        api = APIClient()
        
        login_resp = api.post("/api/v1/public/auth/login/username", {
            "username": "admin",
            "password": "Admin123456"
        })
        
        if login_resp.status_code != 200:
            print(f"   ❌ 登录失败: {login_resp.text}")
            return
        
        login_data = login_resp.json()
        if not login_data.get("success"):
            print(f"   ❌ 登录失败: {login_data}")
            return
            
        token = login_data["data"]["access_token"]
        api.set_auth(token)
        print(f"   ✅ 登录成功")
        
        # 2. 获取用户列表，找到一个测试用户
        print("\n2. 获取用户列表...")
        response = api.get("/api/v1/admin/users/list?page=1&page_size=5")
        
        if response.status_code != 200:
            print(f"   ❌ 获取用户列表失败: {response.text}")
            return
        
        users_data = response.json()["data"]["items"]
        if not users_data:
            print("   ⚠️ 没有用户数据")
            return
        
        # 找到一个非管理员用户进行测试
        test_user = None
        for user in users_data:
            if not user.get("is_admin", False):
                test_user = user
                break
        
        if not test_user:
            # 如果没有非管理员用户，就用管理员用户测试
            test_user = users_data[0]
        
        test_user_id = test_user["id"]
        print(f"   测试用户: {test_user['username']} (ID: {test_user_id})")
        
        # 3. 测试获取登录日志接口（之前出现500错误的接口）
        print("\n3. 测试获取登录日志接口...")
        response = api.get(f"/api/v1/admin/users/{test_user_id}/login-logs?page=1&page_size=10")
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ 登录日志查询成功！")
            data = response.json()
            if data.get("success"):
                pagination = data['data']['pagination']
                items = data['data']['items']
                print(f"   日志总数: {pagination['total']}")
                print(f"   当前页: {pagination['page']}")
                print(f"   每页大小: {pagination['page_size']}")
                print(f"   总页数: {pagination['total_pages']}")
                print(f"   当前页日志数: {len(items)}")
                
                if items:
                    print(f"   最新日志: {items[0].get('login_time', 'N/A')}")
                else:
                    print(f"   该用户暂无登录日志")
            else:
                print(f"   ❌ 响应格式错误: {data}")
        elif response.status_code == 500:
            print(f"   ❌ 500错误仍然存在!")
            print(f"   响应: {response.text}")
            try:
                error_data = response.json()
                print(f"   错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print("   无法解析错误JSON")
        else:
            print(f"   ❌ 其他错误: {response.status_code}")
            print(f"   响应: {response.text}")
        
        print("\n🎉 登录日志接口测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login_logs_api() 