#!/usr/bin/env python3
"""
简化版信用卡API测试脚本 - 使用已知测试用户
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def get_test_token():
    """使用已知测试用户获取令牌"""
    print("=== 使用测试用户登录 ===")
    
    login_data = {
        "username": "testuser2024",
        "password": "TestPass123456"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/public/auth/login/username", json=login_data)
    print(f"登录响应状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        access_token = data["data"]["access_token"]
        print("✓ 登录成功")
        return access_token
    else:
        print(f"✗ 登录失败: {response.text}")
        return None

def test_banks_api(headers):
    """测试银行列表API"""
    print("\n=== 测试银行列表API ===")
    
    response = requests.get(f"{BASE_URL}/api/v1/user/cards/banks/list", headers=headers)
    print(f"响应状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        banks = data["data"]
        print(f"✓ 成功获取 {len(banks)} 个银行")
        for bank in banks[:3]:
            print(f"  - {bank['bank_name']}")
        return banks[0] if banks else None
    else:
        print(f"✗ 失败: {response.text}")
        return None

def test_create_card(headers, bank):
    """测试创建信用卡"""
    print("\n=== 测试创建信用卡 ===")
    
    if not bank:
        print("✗ 没有可用银行")
        return None
    
    import random
    card_data = {
        "card_name": "测试信用卡",
        "card_number": f"6225{random.randint(100000000000, 999999999999)}",
        "bank_id": bank["id"],
        "credit_limit": 50000,
        "expiry_month": 12,
        "expiry_year": 2027
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/user/cards", json=card_data, headers=headers)
    print(f"响应状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        card = data["data"]
        print(f"✓ 信用卡创建成功: {card['card_name']}")
        return card["id"]
    else:
        print(f"✗ 创建失败: {response.text}")
        return None

def test_cards_list(headers):
    """测试信用卡列表"""
    print("\n=== 测试信用卡列表 ===")
    
    response = requests.get(f"{BASE_URL}/api/v1/user/cards", headers=headers)
    print(f"响应状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        cards = data["data"]
        print(f"✓ 获取到 {len(cards)} 张信用卡")
        for card in cards:
            print(f"  - {card['card_name']} (额度: {card['credit_limit']})")
    else:
        print(f"✗ 失败: {response.text}")

def main():
    """主函数"""
    print("开始简化版信用卡API测试...\n")
    
    # 1. 获取测试令牌
    token = get_test_token()
    if not token:
        print("无法获取令牌，测试终止")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 测试银行列表
    bank = test_banks_api(headers)
    
    # 3. 测试创建信用卡
    card_id = test_create_card(headers, bank)
    
    # 4. 测试信用卡列表
    test_cards_list(headers)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main() 