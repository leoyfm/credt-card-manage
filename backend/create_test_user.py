#!/usr/bin/env python3
"""
创建测试用户脚本

用于创建系统测试用户，并获取认证令牌。
"""

import requests
import json
import sys

# 服务器配置
BASE_URL = "http://localhost:8000"

# 测试用户信息
TEST_USER = {
    "username": "testuser2024",
    "email": "testuser2024@example.com", 
    "password": "TestPass123456",
    "nickname": "测试用户2024",
    "phone": None
}

def create_test_user():
    """创建测试用户"""
    print("=== 创建测试用户 ===")
    
    # 注册请求
    register_url = f"{BASE_URL}/api/auth/register"
    register_data = {
        "username": TEST_USER["username"],
        "email": TEST_USER["email"],
        "password": TEST_USER["password"],
        "nickname": TEST_USER["nickname"]
    }
    
    try:
        response = requests.post(register_url, json=register_data)
        print(f"注册响应状态码: {response.status_code}")
        print(f"注册响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 用户注册成功")
                user_data = result.get("data", {})
                print(f"用户ID: {user_data.get('id')}")
                print(f"用户名: {user_data.get('username')}")
                print(f"邮箱: {user_data.get('email')}")
                print(f"昵称: {user_data.get('nickname')}")
                return True
            else:
                print(f"❌ 注册失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 注册请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 注册异常: {str(e)}")
        return False

def login_test_user():
    """测试用户登录"""
    print("\n=== 测试用户登录 ===")
    
    # 登录请求
    login_url = f"{BASE_URL}/api/auth/login/username"
    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    
    try:
        response = requests.post(login_url, json=login_data)
        print(f"登录响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 用户登录成功")
                login_data = result.get("data", {})
                access_token = login_data.get("access_token")
                user_info = login_data.get("user", {})
                
                print(f"访问令牌: {access_token}")
                print(f"用户信息: {json.dumps(user_info, ensure_ascii=False, indent=2)}")
                
                return access_token, user_info
            else:
                print(f"❌ 登录失败: {result.get('message')}")
                return None, None
        else:
            print(f"❌ 登录请求失败: {response.status_code}")
            return None, None
            
    except Exception as e:
        print(f"❌ 登录异常: {str(e)}")
        return None, None

def test_authenticated_api(access_token):
    """测试需要认证的API"""
    print("\n=== 测试认证API ===")
    
    # 测试获取用户资料
    profile_url = f"{BASE_URL}/api/auth/profile"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(profile_url, headers=headers)
        print(f"获取用户资料响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ 认证API测试成功")
                print(f"用户资料: {json.dumps(result.get('data'), ensure_ascii=False, indent=2)}")
                return True
            else:
                print(f"❌ 认证API失败: {result.get('message')}")
                return False
        else:
            print(f"❌ 认证API请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 认证API异常: {str(e)}")
        return False

def main():
    """主函数"""
    print("开始创建和测试用户...")
    
    # 1. 创建测试用户
    if create_test_user():
        print("用户创建成功，继续登录测试...")
    else:
        print("用户可能已存在，直接进行登录测试...")
    
    # 2. 测试用户登录
    access_token, user_info = login_test_user()
    
    if not access_token:
        print("❌ 无法获取访问令牌，退出测试")
        sys.exit(1)
    
    # 3. 测试认证API
    if test_authenticated_api(access_token):
        print("\n🎉 所有测试通过！")
        
        # 输出测试用户信息摘要
        print("\n=== 测试用户信息摘要 ===")
        print(f"用户名: {TEST_USER['username']}")
        print(f"密码: {TEST_USER['password']}")
        print(f"邮箱: {TEST_USER['email']}")
        print(f"昵称: {TEST_USER['nickname']}")
        print(f"访问令牌: {access_token}")
        
        # 保存到文件
        test_info = {
            "user": TEST_USER,
            "access_token": access_token,
            "user_info": user_info
        }
        
        with open("test_user_info.json", "w", encoding="utf-8") as f:
            json.dump(test_info, f, ensure_ascii=False, indent=2)
        
        print("\n✅ 测试用户信息已保存到 test_user_info.json 文件")
        
    else:
        print("\n❌ 认证API测试失败")
        sys.exit(1)

if __name__ == "__main__":
    main() 