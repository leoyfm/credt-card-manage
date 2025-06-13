#!/usr/bin/env python3
"""
信用卡API功能测试脚本
"""
import requests
import json
from typing import Dict, Any

BASE_URL = "http://127.0.0.1:8000"

def test_user_registration_and_login() -> str:
    """测试用户注册和登录，返回访问令牌"""
    print("=== 测试用户注册和登录 ===")
    
    # 注册用户
    register_data = {
        "username": "testuser_card",
        "email": "testuser_card@example.com",
        "password": "TestPass123456",
        "nickname": "信用卡测试用户"
    }
    
    print("1. 注册用户...")
    response = requests.post(f"{BASE_URL}/api/v1/public/auth/register", json=register_data)
    print(f"注册响应: {response.status_code}")
    if response.status_code == 200:
        print("✓ 用户注册成功")
    else:
        print(f"✗ 用户注册失败: {response.text}")
        # 可能用户已存在，继续登录
    
    # 登录用户
    login_data = {
        "username": "testuser_card",
        "password": "TestPass123456"
    }
    
    print("2. 用户登录...")
    response = requests.post(f"{BASE_URL}/api/v1/public/auth/login/username", json=login_data)
    print(f"登录响应: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        access_token = data["data"]["access_token"]
        print("✓ 用户登录成功")
        return access_token
    else:
        print(f"✗ 用户登录失败: {response.text}")
        return None

def test_banks_list(headers: Dict[str, str]):
    """测试获取银行列表"""
    print("\n=== 测试获取银行列表 ===")
    
    response = requests.get(f"{BASE_URL}/api/v1/user/cards/banks/list", headers=headers)
    print(f"响应状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        banks = data["data"]
        print(f"✓ 获取银行列表成功，共 {len(banks)} 个银行")
        for bank in banks[:5]:  # 显示前5个银行
            print(f"  - {bank['bank_name']} ({bank['bank_code']})")
        return banks
    else:
        print(f"✗ 获取银行列表失败: {response.text}")
        return []

def test_create_credit_card(headers: Dict[str, str], banks: list) -> str:
    """测试创建信用卡"""
    print("\n=== 测试创建信用卡 ===")
    
    if not banks:
        print("✗ 没有可用的银行数据")
        return None
    
    # 使用第一个银行创建信用卡
    bank = banks[0]
    card_data = {
        "card_name": "我的测试信用卡",
        "card_number": "6225123456789012",
        "bank_id": bank["id"],
        "credit_limit": 50000.00,
        "expiry_month": 12,
        "expiry_year": 2027,
        "billing_date": 5,
        "due_date": 25,
        "annual_fee": 200.00,
        "notes": "这是一张测试信用卡"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/user/cards", json=card_data, headers=headers)
    print(f"响应状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        card = data["data"]
        print(f"✓ 信用卡创建成功")
        print(f"  卡片ID: {card['id']}")
        print(f"  卡片名称: {card['card_name']}")
        print(f"  银行: {card.get('bank_name', '未知')}")
        print(f"  信用额度: {card['credit_limit']}")
        return card["id"]
    else:
        print(f"✗ 信用卡创建失败: {response.text}")
        return None

def test_get_cards_list(headers: Dict[str, str]):
    """测试获取信用卡列表"""
    print("\n=== 测试获取信用卡列表 ===")
    
    response = requests.get(f"{BASE_URL}/api/v1/user/cards", headers=headers)
    print(f"响应状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        cards = data["data"]
        pagination = data.get("pagination", {})
        print(f"✓ 获取信用卡列表成功")
        print(f"  总数: {pagination.get('total', 0)}")
        print(f"  当前页: {pagination.get('current_page', 1)}")
        
        for card in cards:
            print(f"  - {card['card_name']} (额度: {card['credit_limit']})")
        
        return cards
    else:
        print(f"✗ 获取信用卡列表失败: {response.text}")
        return []

def test_get_card_details(headers: Dict[str, str], card_id: str):
    """测试获取信用卡详情"""
    print("\n=== 测试获取信用卡详情 ===")
    
    if not card_id:
        print("✗ 没有可用的信用卡ID")
        return
    
    response = requests.get(f"{BASE_URL}/api/v1/user/cards/{card_id}", headers=headers)
    print(f"响应状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        card = data["data"]
        print(f"✓ 获取信用卡详情成功")
        print(f"  卡片名称: {card['card_name']}")
        print(f"  有效期: {card.get('expiry_display', 'N/A')}")
        print(f"  状态: {card['status']}")
        print(f"  是否主卡: {card['is_primary']}")
    else:
        print(f"✗ 获取信用卡详情失败: {response.text}")

def test_card_statistics(headers: Dict[str, str]):
    """测试信用卡统计"""
    print("\n=== 测试信用卡统计 ===")
    
    # 测试摘要统计
    response = requests.get(f"{BASE_URL}/api/v1/user/cards/summary/overview", headers=headers)
    print(f"摘要统计响应状态: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        summary = data["data"]
        print(f"✓ 获取摘要统计成功")
        print(f"  信用卡总数: {summary.get('total_cards', 0)}")
        print(f"  激活卡片数: {summary.get('active_cards', 0)}")
        print(f"  总信用额度: {summary.get('total_credit_limit', 0)}")
        print(f"  平均使用率: {summary.get('average_utilization_rate', 0)}%")
    else:
        print(f"✗ 获取摘要统计失败: {response.text}")

def main():
    """主测试函数"""
    print("开始信用卡API功能测试...\n")
    
    # 1. 用户注册和登录
    access_token = test_user_registration_and_login()
    if not access_token:
        print("无法获取访问令牌，测试终止")
        return
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 2. 获取银行列表
    banks = test_banks_list(headers)
    
    # 3. 创建信用卡
    card_id = test_create_credit_card(headers, banks)
    
    # 4. 获取信用卡列表
    cards = test_get_cards_list(headers)
    
    # 5. 获取信用卡详情
    if card_id:
        test_get_card_details(headers, card_id)
    
    # 6. 测试统计功能
    test_card_statistics(headers)
    
    print("\n=== 信用卡API功能测试完成 ===")

if __name__ == "__main__":
    main() 