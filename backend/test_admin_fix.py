#!/usr/bin/env python3
"""
测试管理员API修复
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from tests.utils.api import APIClient

def test_admin_api_fix():
    """测试管理员API修复"""
    print("🧪 测试管理员API修复...")
    
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
        
        # 2. 测试获取用户列表
        print("\n2. 测试获取用户列表...")
        response = api.get("/api/v1/admin/users/list?page=1&page_size=5")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ 用户列表查询成功")
            data = response.json()
            if data.get("success"):
                print(f"   用户总数: {data['data']['pagination']['total']}")
            else:
                print(f"   ❌ 响应格式错误: {data}")
        else:
            print(f"   ❌ 请求失败: {response.text}")
            return
        
        # 3. 获取一个用户ID用于测试登录日志
        users_data = response.json()["data"]["items"]
        if not users_data:
            print("   ⚠️ 没有用户数据，跳过登录日志测试")
            return
        
        test_user_id = users_data[0]["id"]
        print(f"   测试用户ID: {test_user_id}")
        
        # 4. 测试获取用户登录日志（之前出现500错误的接口）
        print("\n3. 测试获取用户登录日志...")
        response = api.get(f"/api/v1/admin/users/{test_user_id}/login-logs?page=1&page_size=10")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ 登录日志查询成功")
            data = response.json()
            if data.get("success"):
                print(f"   日志总数: {data['data']['pagination']['total']}")
                print(f"   当前页日志数: {len(data['data']['items'])}")
            else:
                print(f"   ❌ 响应格式错误: {data}")
        elif response.status_code == 500:
            print(f"   ❌ 500错误仍然存在:")
            print(f"   响应: {response.text}")
            try:
                error_data = response.json()
                print(f"   错误详情: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print("   无法解析错误JSON")
        else:
            print(f"   ❌ 其他错误: {response.status_code}")
            print(f"   响应: {response.text}")
        
        # 5. 测试用户统计接口
        print("\n4. 测试用户统计接口...")
        response = api.get("/api/v1/admin/users/statistics")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ 用户统计查询成功")
            data = response.json()
            if data.get("success"):
                stats = data["data"]
                print(f"   总用户数: {stats.get('total_users', 0)}")
                print(f"   活跃用户数: {stats.get('active_users', 0)}")
                print(f"   管理员数: {stats.get('admin_users', 0)}")
            else:
                print(f"   ❌ 响应格式错误: {data}")
        else:
            print(f"   ❌ 请求失败: {response.text}")
        
        print("\n🎉 管理员API测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admin_api_fix() 