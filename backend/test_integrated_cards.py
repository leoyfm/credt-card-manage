"""
信用卡集成年费管理接口测试
"""
import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000/api"
test_user = {
    "username": "testuser2024",
    "password": "TestPass123456"
}

def authenticate():
    """用户认证获取token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={
                "username": test_user["username"],
                "password": test_user["password"]
            }
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data["access_token"]
    except Exception as e:
        print(f"认证失败: {e}")
        return None

def test_create_card_with_annual_fee(token):
    """测试创建集成年费管理的信用卡"""
    print("\n=== 测试创建信用卡（集成年费管理）===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 测试数据1：启用年费管理，刷卡次数减免
    card_data = {
        "bank_name": "交通银行",
        "card_name": "Y-POWER信用卡",
        "card_type": "信用卡",
        "credit_limit": 50000,
        "used_amount": 8000,
        "bill_date": 15,
        "due_date": 5,
        "annual_fee_enabled": True,
        "fee_type": "SWIPE_COUNT",
        "base_annual_fee": 288,
        "waiver_condition": "年刷卡满20次免年费",
        "required_swipe_count": 20
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/cards/",
            headers=headers,
            json=card_data
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ 创建成功: {result['data']['bank_name']} {result['data']['card_name']}")
        print(f"  年费管理状态: {'已启用' if result['data']['annual_fee_enabled'] else '未启用'}")
        if result['data']['annual_fee_rule']:
            rule = result['data']['annual_fee_rule']
            print(f"  年费类型: {rule['fee_type_display']}")
            print(f"  基础年费: {rule['base_annual_fee']}元")
            print(f"  减免条件: {rule['waiver_condition']}")
        print(f"  信用额度: {result['data']['credit_limit']}")
        print(f"  可用额度: {result['data']['available_amount']}")
        return result['data']['id']
    except Exception as e:
        print(f"✗ 创建失败: {e}")
        return None

def test_create_card_with_points_fee(token):
    """测试创建积分兑换年费减免的信用卡"""
    print("\n=== 测试创建信用卡（积分兑换年费）===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    card_data = {
        "bank_name": "中信银行",
        "card_name": "颜卡信用卡",
        "card_type": "信用卡",
        "credit_limit": 80000,
        "used_amount": 15000,
        "bill_date": 8,
        "due_date": 28,
        "annual_fee_enabled": True,
        "fee_type": "POINTS_EXCHANGE",
        "base_annual_fee": 580,
        "waiver_condition": "积分兑换年费",
        "points_ratio": 5800
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/cards/",
            headers=headers,
            json=card_data
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ 创建成功: {result['data']['bank_name']} {result['data']['card_name']}")
        print(f"  年费管理状态: {'已启用' if result['data']['annual_fee_enabled'] else '未启用'}")
        if result['data']['annual_fee_rule']:
            rule = result['data']['annual_fee_rule']
            print(f"  年费类型: {rule['fee_type_display']}")
            print(f"  基础年费: {rule['base_annual_fee']}元")
            print(f"  积分比例: {rule['points_ratio']}积分")
        return result['data']['id']
    except Exception as e:
        print(f"✗ 创建失败: {e}")
        return None

def test_create_card_without_annual_fee(token):
    """测试创建不启用年费管理的信用卡"""
    print("\n=== 测试创建信用卡（不启用年费管理）===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    card_data = {
        "bank_name": "华夏银行",
        "card_name": "华夏ETC信用卡",
        "card_type": "信用卡",
        "credit_limit": 30000,
        "used_amount": 5000,
        "bill_date": 20,
        "due_date": 10,
        "annual_fee_enabled": False
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/cards/",
            headers=headers,
            json=card_data
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ 创建成功: {result['data']['bank_name']} {result['data']['card_name']}")
        print(f"  年费管理状态: {'已启用' if result['data']['annual_fee_enabled'] else '未启用'}")
        print(f"  年费规则: {'有' if result['data']['annual_fee_rule'] else '无'}")
        return result['data']['id']
    except Exception as e:
        print(f"✗ 创建失败: {e}")
        return None

def test_get_cards_list(token):
    """测试获取信用卡列表（集成年费信息）"""
    print("\n=== 测试获取信用卡列表（集成年费信息）===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/cards/?page=1&page_size=10",
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ 获取成功，总数: {result['data']['pagination']['total']}")
        
        for card in result['data']['items']:
            print(f"  - {card['bank_name']} {card['card_name']}")
            print(f"    信用额度: {card['credit_limit']}，可用额度: {card['available_amount']}")
            print(f"    年费管理: {'已启用' if card['annual_fee_enabled'] else '未启用'}")
            if card['annual_fee_rule']:
                rule = card['annual_fee_rule']
                print(f"    年费规则: {rule['fee_type_display']} - {rule['base_annual_fee']}元")
            if card['current_annual_fee']:
                fee = card['current_annual_fee']
                print(f"    当前年费: {fee['status_display']} - 到期日: {fee['due_date']}")
    except Exception as e:
        print(f"✗ 获取列表失败: {e}")

def test_get_card_detail(token, card_id):
    """测试获取信用卡详情（集成年费信息）"""
    print(f"\n=== 测试获取信用卡详情（集成年费信息）===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/cards/{card_id}",
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        card = result['data']
        print(f"✓ 获取详情成功: {card['bank_name']} {card['card_name']}")
        print(f"  信用额度: {card['credit_limit']}")
        print(f"  已用额度: {card['used_amount']}")
        print(f"  可用额度: {card['available_amount']}")
        print(f"  账单日: {card['bill_date']}号")
        print(f"  还款日: {card['due_date']}号")
        print(f"  年费管理: {'已启用' if card['annual_fee_enabled'] else '未启用'}")
        
        if card['annual_fee_rule']:
            rule = card['annual_fee_rule']
            print(f"  年费规则:")
            print(f"    类型: {rule['fee_type_display']}")
            print(f"    基础年费: {rule['base_annual_fee']}元")
            print(f"    减免条件: {rule['waiver_condition']}")
            if rule['required_swipe_count']:
                print(f"    要求刷卡次数: {rule['required_swipe_count']}次")
            if rule['points_ratio']:
                print(f"    积分比例: {rule['points_ratio']}积分")
        
        if card['current_annual_fee']:
            fee = card['current_annual_fee']
            print(f"  当前年费:")
            print(f"    状态: {fee['status_display']}")
            print(f"    到期日: {fee['due_date']}")
            print(f"    金额: {fee['amount']}元")
    except Exception as e:
        print(f"✗ 获取详情失败: {e}")

def test_update_card(token, card_id):
    """测试更新信用卡（集成年费管理）"""
    print(f"\n=== 测试更新信用卡（集成年费管理）===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 更新数据：启用年费管理，改为刷卡金额减免
    update_data = {
        "credit_limit": 60000,
        "used_amount": 12000,
        "annual_fee_enabled": True,
        "fee_type": "SWIPE_AMOUNT",
        "base_annual_fee": 380,
        "waiver_condition": "年刷卡满50000元免年费",
        "required_swipe_amount": 50000
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/cards/{card_id}",
            headers=headers,
            json=update_data
        )
        response.raise_for_status()
        result = response.json()
        card = result['data']
        print(f"✓ 更新成功: {card['bank_name']} {card['card_name']}")
        print(f"  新信用额度: {card['credit_limit']}")
        print(f"  新可用额度: {card['available_amount']}")
        if card['annual_fee_rule']:
            rule = card['annual_fee_rule']
            print(f"  更新后年费规则: {rule['fee_type_display']} - {rule['base_annual_fee']}元")
            print(f"  减免条件: {rule['waiver_condition']}")
    except Exception as e:
        print(f"✗ 更新失败: {e}")

def test_search_cards(token):
    """测试搜索信用卡"""
    print("\n=== 测试搜索信用卡 ===")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            f"{BASE_URL}/cards/?keyword=交通",
            headers=headers
        )
        response.raise_for_status()
        result = response.json()
        print(f"✓ 搜索成功，找到 {result['data']['pagination']['total']} 条记录")
        
        for card in result['data']['items']:
            print(f"  - {card['bank_name']} {card['card_name']}")
    except Exception as e:
        print(f"✗ 搜索失败: {e}")

def main():
    """主测试函数"""
    print("开始测试信用卡集成年费管理接口...")
    
    # 认证获取token
    token = authenticate()
    if not token:
        print("认证失败，停止测试")
        return
    
    print(f"✓ 认证成功，token获取成功")
    
    # 测试创建不同类型的信用卡
    card_id1 = test_create_card_with_annual_fee(token)
    card_id2 = test_create_card_with_points_fee(token)
    card_id3 = test_create_card_without_annual_fee(token)
    
    # 测试获取列表
    test_get_cards_list(token)
    
    # 测试获取详情
    if card_id1:
        test_get_card_detail(token, card_id1)
    
    # 测试更新
    if card_id1:
        test_update_card(token, card_id1)
    
    # 测试搜索
    test_search_cards(token)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main() 