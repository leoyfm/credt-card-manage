#!/usr/bin/env python3
"""
手动测试脚本

直接通过HTTP请求测试交易接口，不依赖pytest和复杂的数据库设置。
"""

import requests
import json
from datetime import datetime
import sys

# 服务器配置
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_auth_and_get_token():
    """测试认证并获取token"""
    print("🔑 测试用户认证...")
    
    # 使用已知的测试用户
    login_data = {
        "username": "testuser2024",
        "password": "TestPass123456"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login/username", json=login_data)
        print(f"登录响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                token = result["data"]["access_token"]
                print("✅ 登录成功，获取到token")
                return token
            else:
                print(f"❌ 登录失败: {result.get('message', '未知错误')}")
                return None
        else:
            print(f"❌ 登录请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录请求异常: {str(e)}")
        return None

def get_user_cards(token):
    """获取用户的信用卡列表"""
    print("💳 获取用户信用卡列表...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/cards/", headers=headers)
        print(f"获取信用卡响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                cards = result["data"]["items"]
                print(f"✅ 获取到 {len(cards)} 张信用卡")
                if cards:
                    card = cards[0]
                    print(f"使用信用卡: {card['card_name']} (ID: {card['id']})")
                    return card["id"]
                else:
                    print("❌ 没有可用的信用卡")
                    return None
            else:
                print(f"❌ 获取信用卡失败: {result.get('message', '未知错误')}")
                return None
        else:
            print(f"❌ 获取信用卡请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 获取信用卡请求异常: {str(e)}")
        return None

def test_create_transaction(token, card_id):
    """测试创建交易记录"""
    print("📝 测试创建交易记录...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    transaction_data = {
        "card_id": card_id,
        "transaction_type": "expense",
        "amount": 88.88,
        "transaction_date": datetime.now().isoformat(),
        "merchant_name": "测试商户",
        "description": "测试交易记录",
        "category": "dining",
        "status": "completed",
        "points_earned": 8.88,
        "points_rate": 1.0,
        "reference_number": f"TEST{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "location": "北京市朝阳区",
        "is_installment": False,
        "notes": "自动化测试创建的交易记录"
    }
    
    try:
        response = requests.post(f"{API_BASE}/transactions/", json=transaction_data, headers=headers)
        print(f"创建交易响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                transaction = result["data"]
                print(f"✅ 交易创建成功，ID: {transaction['id']}")
                return transaction["id"]
            else:
                print(f"❌ 创建交易失败: {result.get('message', '未知错误')}")
                return None
        else:
            print(f"❌ 创建交易请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 创建交易请求异常: {str(e)}")
        return None

def test_get_transactions(token):
    """测试获取交易记录列表"""
    print("📋 测试获取交易记录列表...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/transactions/", headers=headers)
        print(f"获取交易列表响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                transactions = result["data"]["items"]
                print(f"✅ 获取到 {len(transactions)} 条交易记录")
                # 显示分页信息
                if 'pagination' in result['data']:
                    print(f"分页信息: {result['data']['pagination']}")
                else:
                    print("⚠️  响应中没有分页信息")
                return True
            else:
                print(f"❌ 获取交易列表失败: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 获取交易列表请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 获取交易列表请求异常: {str(e)}")
        return False

def test_get_transaction_detail(token, transaction_id):
    """测试获取交易记录详情"""
    print("🔍 测试获取交易记录详情...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/transactions/{transaction_id}", headers=headers)
        print(f"获取交易详情响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                transaction = result["data"]
                print(f"✅ 获取交易详情成功: {transaction['merchant_name']}")
                return True
            else:
                print(f"❌ 获取交易详情失败: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 获取交易详情请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 获取交易详情请求异常: {str(e)}")
        return False

def test_transaction_statistics(token):
    """测试交易统计接口"""
    print("📊 测试交易统计接口...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试概览统计
    try:
        response = requests.get(f"{API_BASE}/transactions/statistics/overview", headers=headers)
        print(f"统计概览响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                stats = result["data"]
                print(f"✅ 统计概览获取成功")
                print(f"   总支出: {stats.get('total_expense', 0)}")
                print(f"   总收入: {stats.get('total_income', 0)}")
                print(f"   交易笔数: {stats.get('transaction_count', 0)}")
                return True
            else:
                print(f"❌ 获取统计概览失败: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 获取统计概览请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 获取统计概览请求异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始手动测试交易接口...")
    print("=" * 60)
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ 服务器未运行，请先启动服务: python start.py dev")
            return False
    except:
        print("❌ 无法连接到服务器，请先启动服务: python start.py dev")
        return False
    
    print("✅ 服务器连接正常")
    print("-" * 60)
    
    # 测试步骤
    token = test_auth_and_get_token()
    if not token:
        print("❌ 认证失败，无法继续测试")
        return False
    
    print("-" * 60)
    
    card_id = get_user_cards(token)
    if not card_id:
        print("❌ 没有可用的信用卡，无法测试交易功能")
        return False
    
    print("-" * 60)
    
    transaction_id = test_create_transaction(token, card_id)
    if not transaction_id:
        print("❌ 创建交易失败")
        return False
    
    print("-" * 60)
    
    if not test_get_transactions(token):
        print("❌ 获取交易列表失败")
        return False
    
    print("-" * 60)
    
    if not test_get_transaction_detail(token, transaction_id):
        print("❌ 获取交易详情失败")
        return False
    
    print("-" * 60)
    
    if not test_transaction_statistics(token):
        print("❌ 获取交易统计失败")
        return False
    
    print("=" * 60)
    print("🎉 所有测试通过！交易接口工作正常")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 