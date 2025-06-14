#!/usr/bin/env python3
"""
测试提醒API功能
"""
import requests
import json
from datetime import datetime, time

# 基础配置
BASE_URL = "http://localhost:8000/api/v1"
headers = {"Content-Type": "application/json"}

def test_reminders_api():
    """测试提醒API功能"""
    
    # 1. 登录获取token
    print("=== 1. 用户登录 ===")
    login_data = {
        "username": "testuser2024",
        "password": "TestPass123456"
    }
    
    response = requests.post(f"{BASE_URL}/public/auth/login/username", json=login_data)
    if response.status_code != 200:
        print(f"登录失败: {response.text}")
        return
    
    token = response.json()["data"]["access_token"]
    auth_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    print(f"登录成功，获取token: {token[:50]}...")
    
    # 2. 获取用户信用卡列表（用于创建提醒）
    print("\n=== 2. 获取信用卡列表 ===")
    response = requests.get(f"{BASE_URL}/user/cards", headers=auth_headers)
    if response.status_code != 200:
        print(f"获取信用卡列表失败: {response.text}")
        return
    
    # 处理不同的响应格式
    cards_response = response.json()
    if "data" in cards_response:
        if isinstance(cards_response["data"], dict) and "items" in cards_response["data"]:
            cards_data = cards_response["data"]["items"]
        elif isinstance(cards_response["data"], list):
            cards_data = cards_response["data"]
        else:
            cards_data = []
    else:
        cards_data = cards_response if isinstance(cards_response, list) else []
    
    print(f"用户共有 {len(cards_data)} 张信用卡")
    card_id = cards_data[0]["id"] if cards_data else None
    
    # 3. 获取未读提醒个数
    print("\n=== 3. 获取未读提醒个数 ===")
    response = requests.get(f"{BASE_URL}/user/reminders/unread-count", headers=auth_headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        unread_data = response.json()["data"]
        print(f"未读提醒个数: {unread_data['total_unread']}")
        print(f"类型分布: {unread_data['type_breakdown']}")
    else:
        print(f"获取未读提醒个数失败: {response.text}")
    
    # 4. 创建提醒设置
    print("\n=== 4. 创建提醒设置 ===")
    setting_data = {
        "card_id": card_id,
        "reminder_type": "payment",
        "advance_days": 3,
        "reminder_time": "09:00:00",
        "email_enabled": True,
        "push_enabled": True,
        "is_enabled": True
    }
    
    response = requests.post(f"{BASE_URL}/user/reminders/settings", json=setting_data, headers=auth_headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        setting = response.json()["data"]
        setting_id = setting["id"]
        print(f"创建提醒设置成功: {setting_id}")
    else:
        print(f"创建提醒设置失败: {response.text}")
        setting_id = None
    
    # 5. 获取提醒设置列表
    print("\n=== 5. 获取提醒设置列表 ===")
    response = requests.get(f"{BASE_URL}/user/reminders/settings", headers=auth_headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        settings_response = response.json()["data"]
        # 处理不同的响应格式
        if isinstance(settings_response, dict) and "pagination" in settings_response:
            print(f"提醒设置总数: {settings_response['pagination']['total']}")
            print(f"设置列表: {len(settings_response['items'])} 条")
        elif isinstance(settings_response, list):
            print(f"设置列表: {len(settings_response)} 条")
        else:
            print(f"设置响应: {settings_response}")
    else:
        print(f"获取提醒设置列表失败: {response.text}")
    
    # 6. 创建提醒记录
    if setting_id:
        print("\n=== 6. 创建提醒记录 ===")
        record_data = {
            "setting_id": setting_id,
            "card_id": card_id,
            "reminder_type": "payment",
            "title": "还款提醒",
            "content": "您的信用卡还款日即将到来，请及时还款"
        }
        
        response = requests.post(f"{BASE_URL}/user/reminders/records", json=record_data, headers=auth_headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            record = response.json()["data"]
            record_id = record["id"]
            print(f"创建提醒记录成功: {record_id}")
        else:
            print(f"创建提醒记录失败: {response.text}")
            record_id = None
    
    # 7. 再次获取未读提醒个数
    print("\n=== 7. 再次获取未读提醒个数 ===")
    response = requests.get(f"{BASE_URL}/user/reminders/unread-count", headers=auth_headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        unread_data = response.json()["data"]
        print(f"未读提醒个数: {unread_data['total_unread']}")
        print(f"类型分布: {unread_data['type_breakdown']}")
    else:
        print(f"获取未读提醒个数失败: {response.text}")
    
    # 8. 获取提醒记录列表
    print("\n=== 8. 获取提醒记录列表 ===")
    response = requests.get(f"{BASE_URL}/user/reminders/records", headers=auth_headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        records_response = response.json()["data"]
        # 处理不同的响应格式
        if isinstance(records_response, dict) and "pagination" in records_response:
            print(f"提醒记录总数: {records_response['pagination']['total']}")
            print(f"记录列表: {len(records_response['items'])} 条")
        elif isinstance(records_response, list):
            print(f"记录列表: {len(records_response)} 条")
        else:
            print(f"记录响应: {records_response}")
    else:
        print(f"获取提醒记录列表失败: {response.text}")
    
    # 9. 标记所有提醒为已读
    print("\n=== 9. 标记所有提醒为已读 ===")
    response = requests.post(f"{BASE_URL}/user/reminders/mark-all-read", headers=auth_headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()["data"]
        print(f"标记结果: {result['message']}")
    else:
        print(f"标记失败: {response.text}")
    
    # 10. 最后再次获取未读提醒个数
    print("\n=== 10. 最后获取未读提醒个数 ===")
    response = requests.get(f"{BASE_URL}/user/reminders/unread-count", headers=auth_headers)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        unread_data = response.json()["data"]
        print(f"未读提醒个数: {unread_data['total_unread']}")
        print(f"类型分布: {unread_data['type_breakdown']}")
    else:
        print(f"获取未读提醒个数失败: {response.text}")

if __name__ == "__main__":
    test_reminders_api() 