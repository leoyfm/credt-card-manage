#!/usr/bin/env python3
"""
统计接口手动测试脚本

用于验证统计接口的功能是否正常工作。
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "http://localhost:8000/api"
TEST_USER = {
    "username": "testuser2024",
    "password": "TestPass123456"
}

def login():
    """登录获取访问令牌"""
    print("正在登录...")
    
    response = requests.post(f"{BASE_URL}/auth/login/username", json={
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    })
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            token = data["data"]["access_token"]
            print(f"登录成功，获取到访问令牌")
            return {"Authorization": f"Bearer {token}"}
        else:
            print(f"登录失败: {data['message']}")
            return None
    else:
        print(f"登录请求失败: {response.status_code}")
        return None

def test_statistics_overview(headers):
    """测试统计概览接口"""
    print("\n=== 测试统计概览接口 ===")
    
    response = requests.get(f"{BASE_URL}/statistics/overview", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            stats = data["data"]
            print("✅ 统计概览获取成功")
            print(f"   信用卡总数: {stats['card_stats']['total_cards']}")
            print(f"   激活卡数: {stats['card_stats']['active_cards']}")
            print(f"   总信用额度: {stats['credit_stats']['total_credit_limit']}")
            print(f"   总使用金额: {stats['credit_stats']['total_used_amount']}")
            print(f"   整体利用率: {stats['credit_stats']['overall_utilization_rate']:.2f}%")
            print(f"   总交易笔数: {stats['transaction_stats']['total_transactions']}")
            print(f"   总消费金额: {stats['transaction_stats']['total_expense_amount']}")
            print(f"   银行分布数量: {len(stats['bank_distribution'])}")
            return True
        else:
            print(f"❌ 获取统计概览失败: {data['message']}")
            return False
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return False

def test_card_statistics(headers):
    """测试信用卡统计接口"""
    print("\n=== 测试信用卡统计接口 ===")
    
    response = requests.get(f"{BASE_URL}/statistics/cards", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            stats = data["data"]
            print("✅ 信用卡统计获取成功")
            print(f"   总卡数: {stats['total_cards']}")
            print(f"   激活卡数: {stats['active_cards']}")
            print(f"   未激活卡数: {stats['inactive_cards']}")
            print(f"   冻结卡数: {stats['frozen_cards']}")
            print(f"   已注销卡数: {stats['cancelled_cards']}")
            print(f"   过期卡数: {stats['expired_cards']}")
            print(f"   即将过期卡数: {stats['expiring_soon_cards']}")
            return True
        else:
            print(f"❌ 获取信用卡统计失败: {data['message']}")
            return False
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return False

def test_credit_limit_statistics(headers):
    """测试信用额度统计接口"""
    print("\n=== 测试信用额度统计接口 ===")
    
    response = requests.get(f"{BASE_URL}/statistics/credit-limit", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            stats = data["data"]
            print("✅ 信用额度统计获取成功")
            print(f"   总信用额度: {stats['total_credit_limit']}")
            print(f"   总使用金额: {stats['total_used_amount']}")
            print(f"   总可用金额: {stats['total_available_amount']}")
            print(f"   整体利用率: {stats['overall_utilization_rate']:.2f}%")
            print(f"   最高利用率: {stats['highest_utilization_rate']:.2f}%")
            print(f"   最低利用率: {stats['lowest_utilization_rate']:.2f}%")
            print(f"   平均利用率: {stats['average_utilization_rate']:.2f}%")
            return True
        else:
            print(f"❌ 获取信用额度统计失败: {data['message']}")
            return False
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return False

def test_transaction_statistics(headers):
    """测试交易统计接口"""
    print("\n=== 测试交易统计接口 ===")
    
    response = requests.get(f"{BASE_URL}/statistics/transactions", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            stats = data["data"]
            print("✅ 交易统计获取成功")
            print(f"   总交易笔数: {stats['total_transactions']}")
            print(f"   总消费金额: {stats['total_expense_amount']}")
            print(f"   总还款金额: {stats['total_payment_amount']}")
            print(f"   总积分收入: {stats['total_points_earned']}")
            print(f"   平均交易金额: {stats['average_transaction_amount']}")
            print(f"   本月交易笔数: {stats['current_month_transactions']}")
            print(f"   本月消费金额: {stats['current_month_expense_amount']}")
            return True
        else:
            print(f"❌ 获取交易统计失败: {data['message']}")
            return False
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return False

def test_annual_fee_statistics(headers):
    """测试年费统计接口"""
    print("\n=== 测试年费统计接口 ===")
    
    response = requests.get(f"{BASE_URL}/statistics/annual-fee", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            stats = data["data"]
            print("✅ 年费统计获取成功")
            print(f"   年费总额: {stats['total_annual_fee']}")
            print(f"   减免次数: {stats['waived_count']}")
            print(f"   待缴费次数: {stats['pending_count']}")
            print(f"   已缴费次数: {stats['paid_count']}")
            print(f"   逾期次数: {stats['overdue_count']}")
            print(f"   本年度应缴费用: {stats['current_year_due_amount']}")
            print(f"   减免节省金额: {stats['total_waived_amount']}")
            return True
        else:
            print(f"❌ 获取年费统计失败: {data['message']}")
            return False
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return False

def test_category_statistics(headers):
    """测试消费分类统计接口"""
    print("\n=== 测试消费分类统计接口 ===")
    
    response = requests.get(f"{BASE_URL}/statistics/categories", headers=headers, params={"limit": 5})
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            categories = data["data"]
            print(f"✅ 消费分类统计获取成功，共 {len(categories)} 个分类")
            for i, category in enumerate(categories, 1):
                print(f"   {i}. {category['category_name']}: {category['total_amount']} ({category['percentage']:.1f}%)")
            return True
        else:
            print(f"❌ 获取消费分类统计失败: {data['message']}")
            return False
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return False

def test_monthly_trends(headers):
    """测试月度趋势接口"""
    print("\n=== 测试月度趋势接口 ===")
    
    response = requests.get(f"{BASE_URL}/statistics/monthly-trends", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            trends = data["data"]
            print(f"✅ 月度趋势获取成功，共 {len(trends)} 个月份")
            for trend in trends[-3:]:  # 显示最近3个月
                print(f"   {trend['year_month']}: 交易{trend['transaction_count']}笔, 消费{trend['expense_amount']}, 还款{trend['payment_amount']}")
            return True
        else:
            print(f"❌ 获取月度趋势失败: {data['message']}")
            return False
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return False

def test_bank_statistics(headers):
    """测试银行分布统计接口"""
    print("\n=== 测试银行分布统计接口 ===")
    
    response = requests.get(f"{BASE_URL}/statistics/banks", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data["success"]:
            banks = data["data"]
            print(f"✅ 银行分布统计获取成功，共 {len(banks)} 家银行")
            for bank in banks:
                print(f"   {bank['bank_name']}: {bank['card_count']}张卡, 额度{bank['total_credit_limit']}, 利用率{bank['utilization_rate']:.1f}%")
            return True
        else:
            print(f"❌ 获取银行分布统计失败: {data['message']}")
            return False
    else:
        print(f"❌ 请求失败: {response.status_code}")
        return False

def main():
    """主函数"""
    print("🚀 开始测试统计接口...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 登录获取令牌
    headers = login()
    if not headers:
        print("❌ 登录失败，无法继续测试")
        return
    
    # 测试各个统计接口
    tests = [
        ("统计概览", test_statistics_overview),
        ("信用卡统计", test_card_statistics),
        ("信用额度统计", test_credit_limit_statistics),
        ("交易统计", test_transaction_statistics),
        ("年费统计", test_annual_fee_statistics),
        ("消费分类统计", test_category_statistics),
        ("月度趋势", test_monthly_trends),
        ("银行分布统计", test_bank_statistics),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func(headers):
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}测试出现异常: {str(e)}")
    
    # 输出测试结果
    print(f"\n📊 测试完成！")
    print(f"总测试数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有统计接口测试通过！")
    else:
        print("⚠️  部分测试失败，请检查接口实现")

if __name__ == "__main__":
    main() 