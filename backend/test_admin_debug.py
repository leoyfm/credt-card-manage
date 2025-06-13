#!/usr/bin/env python3
"""
管理员API调试脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import requests
import json
from tests.utils.api import APIClient
from tests.factories.user_factory import build_user

def test_admin_api():
    """测试管理员API并捕获错误"""
    print("🧪 开始测试管理员API...")
    
    try:
        # 1. 登录管理员用户
        print("\n1. 尝试登录管理员用户...")
        api = APIClient()
        
        login_resp = api.post("/api/v1/public/auth/login/username", {
            "username": "admin",
            "password": "Admin123456"
        })
        
        print(f"   登录响应状态码: {login_resp.status_code}")
        if login_resp.status_code != 200:
            print(f"   登录失败: {login_resp.text}")
            return
        
        login_data = login_resp.json()
        print(f"   登录成功: {login_data.get('success', False)}")
        
        if not login_data.get("success"):
            print(f"   登录响应: {login_data}")
            return
            
        token = login_data["data"]["access_token"]
        api.set_auth(token)
        print(f"   获取到token: {token[:20]}...")
        
        # 2. 测试获取用户列表
        print("\n2. 测试获取用户列表...")
        response = api.get("/api/v1/admin/users/list?page=1&page_size=5")
        print(f"   响应状态码: {response.status_code}")
        
        if response.status_code == 500:
            print(f"   ❌ 500错误详情:")
            print(f"   响应头: {dict(response.headers)}")
            print(f"   响应体: {response.text}")
            
            # 检查是否有详细错误信息
            try:
                error_data = response.json()
                print(f"   错误JSON: {json.dumps(error_data, indent=2, ensure_ascii=False)}")
            except:
                print("   无法解析错误JSON")
        
        elif response.status_code == 200:
            print(f"   ✅ 请求成功")
            data = response.json()
            print(f"   返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   其他错误: {response.status_code}")
            print(f"   响应: {response.text}")
        
        # 3. 测试用户统计接口
        print("\n3. 测试用户统计接口...")
        response = api.get("/api/v1/admin/users/statistics")
        print(f"   响应状态码: {response.status_code}")
        
        if response.status_code == 500:
            print(f"   ❌ 500错误详情:")
            print(f"   响应体: {response.text}")
        elif response.status_code == 200:
            print(f"   ✅ 请求成功")
            data = response.json()
            print(f"   统计数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admin_api() 