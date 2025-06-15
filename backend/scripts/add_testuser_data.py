#!/usr/bin/env python3
"""
为testuser用户添加测试数据脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.database.user import User
from app.models.database.card import Bank, CreditCard
from app.models.database.transaction import Transaction, TransactionCategory
from app.models.database.fee_waiver import FeeWaiverRule, AnnualFeeRecord
from app.models.database.reminder import ReminderSetting
from app.models.database.recommendation import RecommendationRule, RecommendationRecord


def find_testuser(db: Session) -> User:
    """查找testuser用户"""
    user = db.query(User).filter(User.username == "testuser").first()
    if not user:
        print("错误：未找到用户名为 'testuser' 的用户")
        print("请先创建该用户或确认用户名正确")
        return None
    return user


def create_banks_if_needed(db: Session):
    """创建银行数据（如果不存在）"""
    existing_count = db.query(Bank).count()
    if existing_count > 0:
        print(f"银行数据已存在 {existing_count} 条记录")
        return
    
    banks_data = [
        {"bank_code": "CMB", "bank_name": "招商银行", "sort_order": 1},
        {"bank_code": "CCB", "bank_name": "中国建设银行", "sort_order": 2},
        {"bank_code": "ICBC", "bank_name": "中国工商银行", "sort_order": 3},
        {"bank_code": "SPDB", "bank_name": "浦发银行", "sort_order": 4},
        {"bank_code": "ABC", "bank_name": "中国农业银行", "sort_order": 5},
    ]
    
    for bank_data in banks_data:
        bank = Bank(**bank_data)
        db.add(bank)
    
    db.commit()
    print(f"创建了 {len(banks_data)} 个银行记录")


def create_transaction_categories_if_needed(db: Session):
    """创建交易分类（如果不存在）"""
    existing_count = db.query(TransactionCategory).count()
    if existing_count > 0:
        print(f"交易分类已存在 {existing_count} 条记录")
        return
    
    categories_data = [
        {"name": "餐饮美食", "icon": "restaurant", "color": "#FF6B6B", "sort_order": 1},
        {"name": "购物消费", "icon": "shopping", "color": "#4ECDC4", "sort_order": 2},
        {"name": "交通出行", "icon": "car", "color": "#45B7D1", "sort_order": 3},
        {"name": "生活服务", "icon": "home", "color": "#96CEB4", "sort_order": 4},
        {"name": "娱乐休闲", "icon": "game", "color": "#FFEAA7", "sort_order": 5},
        {"name": "医疗健康", "icon": "medical", "color": "#DDA0DD", "sort_order": 6},
        {"name": "教育培训", "icon": "book", "color": "#98D8C8", "sort_order": 7},
        {"name": "数码电器", "icon": "phone", "color": "#F7DC6F", "sort_order": 8},
    ]
    
    for category_data in categories_data:
        category = TransactionCategory(**category_data)
        db.add(category)
    
    db.commit()
    print(f"创建了 {len(categories_data)} 个交易分类")


def create_credit_cards(db: Session, user: User):
    """为用户创建信用卡"""
    # 获取银行
    cmb_bank = db.query(Bank).filter(Bank.bank_code == "CMB").first()
    ccb_bank = db.query(Bank).filter(Bank.bank_code == "CCB").first()
    spdb_bank = db.query(Bank).filter(Bank.bank_code == "SPDB").first()
    
    cards_data = [
        {
            "user_id": user.id,
            "bank_id": cmb_bank.id if cmb_bank else None,
            "card_number": "1111",  # 只保存后4位
            "card_name": "招商银行经典白金卡",
            "card_type": "credit",
            "card_network": "VISA",
            "card_level": "白金卡",
            "bank_color": "#DC2626",  # 招商银行红色
            "credit_limit": Decimal("100000.00"),
            "available_limit": Decimal("95000.00"),
            "used_limit": Decimal("5000.00"),
            "expiry_month": 12,
            "expiry_year": 2027,
            "billing_date": 5,
            "due_date": 25,
            "annual_fee": Decimal("580.00"),
            "fee_waivable": True,
            "fee_auto_deduct": False,
            "fee_due_month": 3,
            "features": ["积分永久有效", "机场贵宾厅", "道路救援"],
            "points_rate": Decimal("1.00"),
            "cashback_rate": Decimal("0.01"),
            "status": "active",
            "is_primary": True,
            "notes": "主要使用的信用卡"
        },
        {
            "user_id": user.id,
            "bank_id": ccb_bank.id if ccb_bank else None,
            "card_number": "4444",  # 只保存后4位
            "card_name": "建设银行龙卡信用卡",
            "card_type": "credit",
            "card_network": "MasterCard",
            "card_level": "金卡",
            "bank_color": "#2563EB",  # 建设银行蓝色
            "credit_limit": Decimal("50000.00"),
            "available_limit": Decimal("48000.00"),
            "used_limit": Decimal("2000.00"),
            "expiry_month": 8,
            "expiry_year": 2026,
            "billing_date": 10,
            "due_date": 28,
            "annual_fee": Decimal("200.00"),
            "fee_waivable": True,
            "fee_auto_deduct": True,
            "fee_due_month": 6,
            "features": ["积分兑换", "分期免息", "消费返现"],
            "points_rate": Decimal("1.00"),
            "cashback_rate": Decimal("0.005"),
            "status": "active",
            "is_primary": False,
            "notes": "备用信用卡"
        },
        {
            "user_id": user.id,
            "bank_id": spdb_bank.id if spdb_bank else None,
            "card_number": "0002",  # 只保存后4位
            "card_name": "浦发银行AE白金卡",
            "card_type": "credit",
            "card_network": "American Express",
            "card_level": "白金卡",
            "bank_color": "#7C3AED",  # 浦发银行紫色
            "credit_limit": Decimal("200000.00"),
            "available_limit": Decimal("190000.00"),
            "used_limit": Decimal("10000.00"),
            "expiry_month": 6,
            "expiry_year": 2028,
            "billing_date": 15,
            "due_date": 5,
            "annual_fee": Decimal("3600.00"),
            "fee_waivable": False,
            "fee_auto_deduct": True,
            "fee_due_month": 1,
            "features": ["无限额度", "全球机场贵宾厅", "专属客服", "高端酒店权益"],
            "points_rate": Decimal("2.00"),
            "cashback_rate": Decimal("0.02"),
            "status": "active",
            "is_primary": False,
            "notes": "高端消费专用卡"
        }
    ]
    
    created_cards = []
    for card_data in cards_data:
        card = CreditCard(**card_data)
        db.add(card)
        created_cards.append(card)
    
    db.commit()
    
    # 刷新对象以获取ID
    for card in created_cards:
        db.refresh(card)
    
    print(f"为用户 {user.username} 创建了 {len(created_cards)} 张信用卡")
    return created_cards


def create_transactions(db: Session, user: User, cards: list):
    """创建交易记录"""
    # 获取交易分类
    categories = db.query(TransactionCategory).all()
    category_map = {cat.name: cat for cat in categories}
    
    # 为每张卡创建一些交易记录
    all_transactions = []
    
    # 招商银行卡的交易（主卡，交易较多）
    cmb_card = cards[0]
    cmb_transactions = [
        {
            "user_id": user.id,
            "card_id": cmb_card.id,
            "category_id": category_map.get("餐饮美食").id if category_map.get("餐饮美食") else None,
            "transaction_type": "expense",
            "amount": Decimal("128.50"),
            "currency": "CNY",
            "description": "星巴克咖啡",
            "merchant_name": "星巴克咖啡",
            "merchant_category": "餐饮美食",
            "location": "北京市朝阳区",
            "points_earned": 129,
            "cashback_earned": Decimal("1.29"),
            "status": "completed",
            "transaction_date": datetime.now() - timedelta(days=1),
            "notes": "早餐咖啡",
            "tags": ["餐饮", "咖啡"]
        },
        {
            "user_id": user.id,
            "card_id": cmb_card.id,
            "category_id": category_map.get("购物消费").id if category_map.get("购物消费") else None,
            "transaction_type": "expense",
            "amount": Decimal("2599.00"),
            "currency": "CNY",
            "description": "苹果专卖店购买iPhone配件",
            "merchant_name": "苹果专卖店",
            "merchant_category": "数码电器",
            "location": "北京市海淀区",
            "points_earned": 2599,
            "cashback_earned": Decimal("25.99"),
            "status": "completed",
            "transaction_date": datetime.now() - timedelta(days=3),
            "notes": "购买手机壳和充电器",
            "tags": ["数码", "苹果"]
        },
        {
            "user_id": user.id,
            "card_id": cmb_card.id,
            "category_id": category_map.get("交通出行").id if category_map.get("交通出行") else None,
            "transaction_type": "expense",
            "amount": Decimal("350.00"),
            "currency": "CNY",
            "description": "中石化加油",
            "merchant_name": "中石化加油站",
            "merchant_category": "交通出行",
            "location": "北京市丰台区",
            "points_earned": 350,
            "cashback_earned": Decimal("3.50"),
            "status": "completed",
            "transaction_date": datetime.now() - timedelta(days=5),
            "notes": "汽车加油",
            "tags": ["加油", "出行"]
        }
    ]
    
    # 建设银行卡的交易
    ccb_card = cards[1]
    ccb_transactions = [
        {
            "user_id": user.id,
            "card_id": ccb_card.id,
            "category_id": category_map.get("生活服务").id if category_map.get("生活服务") else None,
            "transaction_type": "expense",
            "amount": Decimal("89.90"),
            "currency": "CNY",
            "description": "美团外卖",
            "merchant_name": "美团外卖",
            "merchant_category": "生活服务",
            "location": "北京市朝阳区",
            "points_earned": 90,
            "cashback_earned": Decimal("0.45"),
            "status": "completed",
            "transaction_date": datetime.now() - timedelta(days=2),
            "notes": "午餐外卖",
            "tags": ["外卖", "午餐"]
        },
        {
            "user_id": user.id,
            "card_id": ccb_card.id,
            "category_id": category_map.get("娱乐休闲").id if category_map.get("娱乐休闲") else None,
            "transaction_type": "expense",
            "amount": Decimal("168.00"),
            "currency": "CNY",
            "description": "电影院观影",
            "merchant_name": "万达影城",
            "merchant_category": "娱乐休闲",
            "location": "北京市西城区",
            "points_earned": 168,
            "cashback_earned": Decimal("0.84"),
            "status": "completed",
            "transaction_date": datetime.now() - timedelta(days=7),
            "notes": "周末看电影",
            "tags": ["电影", "娱乐"]
        }
    ]
    
    # 浦发银行卡的交易（高端消费）
    spdb_card = cards[2]
    spdb_transactions = [
        {
            "user_id": user.id,
            "card_id": spdb_card.id,
            "category_id": category_map.get("餐饮美食").id if category_map.get("餐饮美食") else None,
            "transaction_type": "expense",
            "amount": Decimal("1580.00"),
            "currency": "CNY",
            "description": "海底捞火锅",
            "merchant_name": "海底捞火锅",
            "merchant_category": "餐饮美食",
            "location": "北京市朝阳区",
            "points_earned": 3160,  # 2倍积分
            "cashback_earned": Decimal("31.60"),
            "status": "completed",
            "transaction_date": datetime.now() - timedelta(days=4),
            "notes": "朋友聚餐",
            "tags": ["火锅", "聚餐"]
        },
        {
            "user_id": user.id,
            "card_id": spdb_card.id,
            "category_id": category_map.get("购物消费").id if category_map.get("购物消费") else None,
            "transaction_type": "expense",
            "amount": Decimal("8999.00"),
            "currency": "CNY",
            "description": "华为专卖店购买笔记本电脑",
            "merchant_name": "华为专卖店",
            "merchant_category": "数码电器",
            "location": "北京市海淀区",
            "points_earned": 17998,  # 2倍积分
            "cashback_earned": Decimal("179.98"),
            "status": "completed",
            "transaction_date": datetime.now() - timedelta(days=10),
            "notes": "购买工作用笔记本",
            "tags": ["笔记本", "华为", "工作"]
        }
    ]
    
    # 合并所有交易
    all_transaction_data = cmb_transactions + ccb_transactions + spdb_transactions
    
    for transaction_data in all_transaction_data:
        transaction = Transaction(**transaction_data)
        db.add(transaction)
        all_transactions.append(transaction)
    
    db.commit()
    print(f"为用户 {user.username} 创建了 {len(all_transactions)} 条交易记录")
    return all_transactions


def create_fee_waiver_rules(db: Session, user: User, cards: list):
    """创建年费减免规则"""
    rules_data = []
    
    # 为招商银行卡创建年费减免规则
    cmb_card = cards[0]
    rules_data.extend([
        {
            "card_id": cmb_card.id,
            "rule_name": "年消费满6万免年费",
            "condition_type": "spending_amount",
            "condition_value": Decimal("60000.00"),
            "condition_period": "yearly",
            "priority": 1,
            "is_enabled": True,
            "description": "年消费满6万元免次年年费"
        },
        {
            "card_id": cmb_card.id,
            "rule_name": "年刷卡满18次免年费",
            "condition_type": "transaction_count",
            "condition_count": 18,
            "condition_period": "yearly",
            "priority": 2,
            "is_enabled": True,
            "description": "年刷卡满18次免次年年费"
        }
    ])
    
    # 为建设银行卡创建年费减免规则
    ccb_card = cards[1]
    rules_data.append({
        "card_id": ccb_card.id,
        "rule_name": "年消费满3万免年费",
        "condition_type": "spending_amount",
        "condition_value": Decimal("30000.00"),
        "condition_period": "yearly",
        "priority": 1,
        "is_enabled": True,
        "description": "年消费满3万元免次年年费"
    })
    
    created_rules = []
    for rule_data in rules_data:
        rule = FeeWaiverRule(**rule_data)
        db.add(rule)
        created_rules.append(rule)
    
    db.commit()
    print(f"为用户 {user.username} 创建了 {len(created_rules)} 条年费减免规则")
    return created_rules


def create_annual_fee_records(db: Session, user: User, cards: list):
    """创建年费记录"""
    records_data = []
    current_year = datetime.now().year
    
    for card in cards:
        # 为每张卡创建当年的年费记录
        fee_month = card.fee_due_month or 12
        # 确保日期有效，使用月末最后一天
        if fee_month == 2:
            # 2月份，考虑闰年
            if current_year % 4 == 0 and (current_year % 100 != 0 or current_year % 400 == 0):
                due_day = 29
            else:
                due_day = 28
        elif fee_month in [4, 6, 9, 11]:
            # 4、6、9、11月只有30天
            due_day = 30
        else:
            # 其他月份有31天
            due_day = 31
            
        record_data = {
            "card_id": card.id,
            "fee_year": current_year,
            "base_fee": card.annual_fee,
            "actual_fee": card.annual_fee,
            "waiver_amount": Decimal("0.00"),
            "status": "pending",
            "due_date": datetime(current_year, fee_month, due_day).date(),
            "notes": f"{current_year}年度年费"
        }
        
        # 如果是招商银行卡，模拟已减免的情况
        if "招商银行" in card.card_name:
            record_data.update({
                "actual_fee": Decimal("0.00"),
                "waiver_amount": card.annual_fee,
                "waiver_reason": "年消费满6万免年费",
                "status": "waived"
            })
        
        record = AnnualFeeRecord(**record_data)
        db.add(record)
        records_data.append(record)
    
    db.commit()
    print(f"为用户 {user.username} 创建了 {len(records_data)} 条年费记录")
    return records_data


def create_reminder_settings(db: Session, user: User, cards: list):
    """创建提醒设置"""
    settings_data = []
    
    # 全局还款提醒
    settings_data.append({
        "user_id": user.id,
        "card_id": None,  # 全局设置
        "reminder_type": "payment_due",
        "advance_days": 3,
        "reminder_time": datetime.strptime("09:00:00", "%H:%M:%S").time(),
        "email_enabled": True,
        "sms_enabled": False,
        "push_enabled": True,
        "wechat_enabled": False,
        "is_recurring": True,
        "frequency": "monthly",
        "is_enabled": True
    })
    
    # 年费提醒
    settings_data.append({
        "user_id": user.id,
        "card_id": None,  # 全局设置
        "reminder_type": "annual_fee",
        "advance_days": 30,
        "reminder_time": datetime.strptime("10:00:00", "%H:%M:%S").time(),
        "email_enabled": True,
        "sms_enabled": True,
        "push_enabled": True,
        "wechat_enabled": False,
        "is_recurring": True,
        "frequency": "yearly",
        "is_enabled": True
    })
    
    # 为主卡设置特殊提醒
    primary_card = next((card for card in cards if card.is_primary), None)
    if primary_card:
        settings_data.append({
            "user_id": user.id,
            "card_id": primary_card.id,
            "reminder_type": "balance_alert",
            "advance_days": 0,
            "reminder_time": datetime.strptime("20:00:00", "%H:%M:%S").time(),
            "email_enabled": False,
            "sms_enabled": False,
            "push_enabled": True,
            "wechat_enabled": False,
            "is_recurring": False,
            "frequency": "daily",
            "is_enabled": True
        })
    
    created_settings = []
    for setting_data in settings_data:
        setting = ReminderSetting(**setting_data)
        db.add(setting)
        created_settings.append(setting)
    
    db.commit()
    print(f"为用户 {user.username} 创建了 {len(created_settings)} 个提醒设置")
    return created_settings


def create_recommendation_data(db: Session, user: User):
    """创建推荐相关数据"""
    # 创建推荐规则（如果不存在）
    existing_rules = db.query(RecommendationRule).count()
    if existing_rules == 0:
        rules_data = [
            {
                "rule_name": "信用卡使用优化建议",
                "rule_type": "card_usage",
                "conditions": {
                    "min_transactions": 5,
                    "min_amount": 1000
                },
                "recommendation_title": "优化信用卡使用",
                "recommendation_content": "根据您的消费习惯，建议调整信用卡使用策略",
                "action_type": "card_switch",
                "priority": 1,
                "is_active": True
            },
            {
                "rule_name": "年费减免提醒",
                "rule_type": "fee_optimization",
                "conditions": {
                    "annual_fee_due": True,
                    "spending_threshold": 50000
                },
                "recommendation_title": "年费减免机会",
                "recommendation_content": "您的信用卡年费即将到期，建议查看减免条件",
                "action_type": "fee_waiver",
                "priority": 2,
                "is_active": True
            }
        ]
        
        for rule_data in rules_data:
            rule = RecommendationRule(**rule_data)
            db.add(rule)
        
        db.commit()
        print("创建了推荐规则")
    
    # 为用户创建推荐记录
    rule = db.query(RecommendationRule).first()
    if rule:
        record_data = {
            "user_id": user.id,
            "rule_id": rule.id,
            "recommendation_type": "card_usage",
            "title": "信用卡使用优化建议",
            "content": "根据您最近的消费记录，建议您优先使用招商银行白金卡进行大额消费，以获得更多积分回报。",
            "action_data": {
                "recommended_card": "招商银行经典白金卡",
                "reason": "积分倍率更高",
                "potential_benefit": "每月可多获得500积分"
            },
            "status": "pending"
        }
        
        record = RecommendationRecord(**record_data)
        db.add(record)
        db.commit()
        print(f"为用户 {user.username} 创建了推荐记录")


def main():
    """主函数"""
    print("开始为testuser用户添加测试数据...")
    
    db: Session = SessionLocal()
    
    try:
        # 1. 查找testuser用户
        user = find_testuser(db)
        if not user:
            return
        
        print(f"找到用户: {user.username} (ID: {user.id})")
        
        # 2. 创建基础数据
        create_banks_if_needed(db)
        create_transaction_categories_if_needed(db)
        
        # 3. 检查用户是否已有数据
        existing_cards = db.query(CreditCard).filter(CreditCard.user_id == user.id).count()
        if existing_cards > 0:
            print(f"用户已有 {existing_cards} 张信用卡，是否继续添加数据？(y/n): ", end="")
            response = input().lower()
            if response != 'y':
                print("取消添加数据")
                return
        
        # 4. 创建信用卡
        cards = create_credit_cards(db, user)
        
        # 5. 创建交易记录
        transactions = create_transactions(db, user, cards)
        
        # 6. 创建年费减免规则
        fee_rules = create_fee_waiver_rules(db, user, cards)
        
        # 7. 创建年费记录
        fee_records = create_annual_fee_records(db, user, cards)
        
        # 8. 创建提醒设置
        reminder_settings = create_reminder_settings(db, user, cards)
        
        # 9. 创建推荐数据
        create_recommendation_data(db, user)
        
        print("\n" + "="*50)
        print("测试数据添加完成！")
        print("="*50)
        print(f"用户: {user.username}")
        print(f"信用卡: {len(cards)} 张")
        print(f"交易记录: {len(transactions)} 条")
        print(f"年费规则: {len(fee_rules)} 条")
        print(f"年费记录: {len(fee_records)} 条")
        print(f"提醒设置: {len(reminder_settings)} 个")
        print("推荐数据: 已创建")
        print("="*50)
        
        # 显示信用卡信息
        print("\n信用卡详情:")
        for i, card in enumerate(cards, 1):
            print(f"{i}. {card.card_name}")
            print(f"   卡号: {card.card_number}")
            print(f"   额度: ¥{card.credit_limit:,.2f}")
            print(f"   状态: {card.status}")
            print(f"   主卡: {'是' if card.is_primary else '否'}")
            print()
        
    except Exception as e:
        db.rollback()
        print(f"添加测试数据失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main() 