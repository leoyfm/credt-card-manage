#!/usr/bin/env python3
"""
测试数据生成脚本

为信用卡管理系统生成丰富的测试数据，用于验证统计功能。
"""

import asyncio
import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List
import uuid

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import SessionLocal
from db_models.users import User
from db_models.cards import CreditCard
from db_models.transactions import Transaction, TransactionType, TransactionCategory, TransactionStatus
from db_models.annual_fee import AnnualFeeRecord, AnnualFeeRule
from models.annual_fee import WaiverStatus, FeeType

# 密码加密工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class TestDataGenerator:
    """测试数据生成器"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.users = []
        self.cards = []
        self.transactions = []
        self.annual_fee_rules = []
        
        # 中国主要银行列表
        self.banks = [
            "中国工商银行", "中国建设银行", "中国农业银行", "中国银行",
            "招商银行", "交通银行", "中信银行", "光大银行",
            "民生银行", "华夏银行", "浦发银行", "平安银行",
            "兴业银行", "广发银行", "中国邮政储蓄银行"
        ]
        
        # 信用卡产品名称
        self.card_products = {
            "中国工商银行": ["牡丹白金卡", "环球旅行卡", "奋斗信用卡", "星座卡"],
            "招商银行": ["全币种国际卡", "经典白金卡", "青年卡", "YOUNG卡"],
            "中国建设银行": ["龙卡信用卡", "全球热购卡", "分期通", "车卡"],
            "交通银行": ["Y-POWER卡", "白麒麟卡", "沃尔玛卡", "苏宁卡"],
            "中信银行": ["颜卡", "i白金卡", "淘宝卡", "爱奇艺联名卡"],
            "光大银行": ["福卡", "淘宝卡", "京东PLUS卡", "阳光商旅卡"],
            "民生银行": ["女人花卡", "豆瓣联名卡", "精英白金卡", "途牛旅游卡"],
            "华夏银行": ["精英尊享卡", "易达金卡", "聪明卡", "爱奇艺卡"],
            "浦发银行": ["美国运通卡", "简约白金卡", "奔驰卡", "梦卡"],
            "平安银行": ["车主卡", "由你卡", "白金卡", "标准卡"],
            "兴业银行": ["淘宝卡", "行悠白金卡", "加菲猫卡", "PASS卡"],
            "广发银行": ["真情卡", "臻享白金卡", "DIY卡", "聪明卡"],
            "中国邮政储蓄银行": ["绿卡通", "VISA信用卡", "公务卡", "商务卡"]
        }
        
        # 商户名称
        self.merchants = {
            TransactionCategory.DINING: [
                "肯德基", "麦当劳", "星巴克", "海底捞", "西贝莜面村",
                "外婆家", "绿茶餐厅", "必胜客", "汉堡王", "真功夫",
                "永和大王", "沙县小吃", "兰州拉面", "黄焖鸡米饭", "重庆小面"
            ],
            TransactionCategory.SHOPPING: [
                "苹果专卖店", "华为专卖店", "小米之家", "NIKE", "阿迪达斯",
                "优衣库", "ZARA", "H&M", "无印良品", "宜家家居",
                "屈臣氏", "丝芙兰", "周大福", "周生生", "潘多拉"
            ],
            TransactionCategory.TRANSPORT: [
                "滴滴出行", "中国石油", "中国石化", "地铁", "公交",
                "高德打车", "首汽约车", "神州专车", "摩拜单车", "哈啰单车",
                "12306", "南方航空", "东方航空", "国航", "春秋航空"
            ],
            TransactionCategory.ENTERTAINMENT: [
                "万达影城", "金逸影城", "大地影院", "KTV", "迪士尼",
                "欢乐谷", "海洋世界", "游戏厅", "健身房", "瑜伽馆",
                "爱奇艺会员", "腾讯视频", "优酷会员", "网易云音乐", "QQ音乐"
            ],
            TransactionCategory.MEDICAL: [
                "北京协和医院", "301医院", "华西医院", "瑞金医院", "中山医院",
                "同仁堂", "康美药业", "九州通", "国药集团", "华润医药",
                "好大夫在线", "丁香医生", "平安好医生", "微医", "春雨医生"
            ],
            TransactionCategory.EDUCATION: [
                "新东方", "好未来", "跟谁学", "VIPKID", "51Talk",
                "猿辅导", "作业帮", "网易有道", "腾讯课堂", "学而思",
                "驾校", "培训机构", "在线教育", "技能培训", "语言培训"
            ],
            TransactionCategory.TRAVEL: [
                "携程旅行", "去哪儿", "飞猪", "同程旅游", "马蜂窝",
                "希尔顿酒店", "万豪酒店", "如家酒店", "汉庭酒店", "七天酒店",
                "民宿", "青年旅社", "度假村", "温泉酒店", "主题酒店"
            ],
            TransactionCategory.SUPERMARKET: [
                "沃尔玛", "家乐福", "大润发", "华润万家", "永辉超市",
                "物美", "联华超市", "世纪联华", "乐购", "欧尚",
                "7-ELEVEN", "全家", "罗森", "美宜佳", "红旗连锁"
            ],
            TransactionCategory.ONLINE: [
                "淘宝", "天猫", "京东", "拼多多", "苏宁易购",
                "唯品会", "当当网", "亚马逊", "网易严选", "小红书",
                "美团", "饿了么", "叮咚买菜", "每日优鲜", "盒马鲜生"
            ],
            TransactionCategory.OTHER: [
                "水电费", "燃气费", "物业费", "手机话费", "宽带费",
                "保险费", "房租", "停车费", "过路费", "其他消费"
            ]
        }

    def generate_users(self, count: int = 5) -> List[User]:
        """生成测试用户"""
        print(f"正在生成 {count} 个测试用户...")
        
        users = []
        for i in range(count):
            # 生成唯一的用户基本信息
            username = f"testuser{i+1:03d}"
            email = f"testuser{i+1:03d}@example.com"
            # 确保手机号唯一
            phone = f"138{random.randint(10000000, 99999999)}"
            
            # 检查是否已存在，如果存在则跳过
            existing_user = self.db.query(User).filter(
                (User.username == username) | 
                (User.email == email) | 
                (User.phone == phone)
            ).first()
            
            if existing_user:
                print(f"用户 {username} 已存在，跳过...")
                continue
            
            user = User(
                username=username,
                email=email,
                phone=phone,
                password_hash=pwd_context.hash("TestPass123456"),
                nickname=f"测试用户{i+1}",
                gender=random.choice(["male", "female", "unknown"]),
                is_active=True,
                is_verified=True,
                login_count="0"
            )
            
            users.append(user)
            self.db.add(user)
        
        self.db.commit()
        self.users = users
        print(f"成功生成 {len(users)} 个测试用户")
        return users

    def generate_annual_fee_rules(self) -> List[AnnualFeeRule]:
        """生成年费规则"""
        print("正在生成年费规则...")
        
        rules = []
        
        # 为每个银行创建不同的年费规则
        for bank in self.banks[:10]:  # 只为前10个银行创建规则
            # 普通卡年费规则
            rule1 = AnnualFeeRule(
                fee_type=FeeType.TRANSACTION_COUNT,
                base_fee=Decimal("200.00"),
                waiver_condition_value=Decimal("6"),
                annual_fee_month=2,
                annual_fee_day=15,
                description=f"{bank}普通卡年费规则：年内消费满6次即可免年费"
            )
            
            # 金卡年费规则
            rule2 = AnnualFeeRule(
                fee_type=FeeType.TRANSACTION_COUNT,
                base_fee=Decimal("500.00"),
                waiver_condition_value=Decimal("10"),
                annual_fee_month=3,
                annual_fee_day=15,
                description=f"{bank}金卡年费规则：年内消费满10次即可免年费"
            )
            
            # 白金卡年费规则
            rule3 = AnnualFeeRule(
                fee_type=FeeType.TRANSACTION_AMOUNT,
                base_fee=Decimal("2000.00"),
                waiver_condition_value=Decimal("200000.00"),
                annual_fee_month=4,
                annual_fee_day=15,
                description=f"{bank}白金卡年费规则：年内消费满20万元即可免年费"
            )
            
            rules.extend([rule1, rule2, rule3])
            for rule in [rule1, rule2, rule3]:
                self.db.add(rule)
        
        self.db.commit()
        self.annual_fee_rules = rules
        print(f"成功生成 {len(rules)} 个年费规则")
        return rules

    def generate_credit_cards(self, users: List[User]) -> List[CreditCard]:
        """为用户生成信用卡"""
        print("正在生成信用卡...")
        
        cards = []
        
        for user in users:
            # 每个用户生成3-8张信用卡
            card_count = random.randint(3, 8)
            
            for i in range(card_count):
                bank = random.choice(self.banks)
                card_products = self.card_products.get(bank, ["标准卡", "金卡", "白金卡"])
                card_name = random.choice(card_products)
                
                # 生成信用卡号
                card_number = self._generate_card_number()
                
                # 随机生成额度（5千到20万之间）
                credit_limit = Decimal(random.randint(5000, 200000))
                
                # 已使用额度（0-80%之间）
                used_amount = credit_limit * Decimal(random.random() * 0.8)
                
                # 随机状态
                status = random.choices(
                    ["active", "inactive", "frozen", "cancelled"],
                    weights=[70, 15, 10, 5]
                )[0]
                
                # 卡片类型
                card_type = random.choice(["visa", "mastercard", "unionpay", "amex"])
                
                # 账单日和还款日
                billing_day = random.randint(1, 28)
                due_day = random.randint(1, 28)
                
                # 有效期（现在到未来5年内）
                expiry_month = random.randint(1, 12)
                expiry_year = random.randint(2024, 2029)
                
                # 年费规则
                annual_fee_rule = None
                if self.annual_fee_rules:
                    # 根据银行名称匹配年费规则
                    bank_rules = [rule for rule in self.annual_fee_rules if bank in rule.description]
                    if bank_rules:
                        annual_fee_rule = random.choice(bank_rules)
                
                card = CreditCard(
                    user_id=user.id,
                    bank_name=bank,
                    card_name=card_name,
                    card_number=card_number,
                    card_type=card_type,
                    credit_limit=credit_limit,
                    used_amount=used_amount,
                    billing_day=billing_day,
                    due_day=due_day,
                    expiry_month=expiry_month,
                    expiry_year=expiry_year,
                    status=status,
                    is_active=status != "cancelled",
                    activation_date=date.today() - timedelta(days=random.randint(30, 1000)),
                    annual_fee_rule_id=annual_fee_rule.id if annual_fee_rule else None,
                    card_color=random.choice(["#1890ff", "#52c41a", "#faad14", "#f5222d", "#722ed1", "#13c2c2"]),
                    notes=f"测试信用卡 - {bank}"
                )
                
                cards.append(card)
                self.db.add(card)
        
        self.db.commit()
        self.cards = cards
        print(f"成功生成 {len(cards)} 张信用卡")
        return cards

    def generate_transactions(self, cards: List[CreditCard]) -> List[Transaction]:
        """为信用卡生成交易记录"""
        print("正在生成交易记录...")
        
        transactions = []
        
        for card in cards:
            if card.status == "cancelled":
                continue
            
            # 每张卡生成30-200笔交易
            transaction_count = random.randint(30, 200)
            
            for i in range(transaction_count):
                # 交易时间（过去12个月内）
                days_ago = random.randint(1, 365)
                transaction_date = datetime.now() - timedelta(days=days_ago)
                
                # 交易类型（80%消费，15%还款，5%其他）
                transaction_type = random.choices(
                    [TransactionType.EXPENSE, TransactionType.PAYMENT, TransactionType.REFUND, TransactionType.WITHDRAWAL, TransactionType.FEE],
                    weights=[80, 15, 2, 2, 1]
                )[0]
                
                # 交易分类（仅对消费类交易）
                if transaction_type == TransactionType.EXPENSE:
                    category = random.choice(list(TransactionCategory))
                else:
                    category = TransactionCategory.OTHER
                
                # 交易金额
                if transaction_type == TransactionType.EXPENSE:
                    amount = Decimal(random.uniform(10, 5000))
                elif transaction_type == TransactionType.PAYMENT:
                    amount = Decimal(random.uniform(100, 10000))
                else:
                    amount = Decimal(random.uniform(10, 1000))
                
                # 商户名称
                merchant_name = random.choice(self.merchants.get(category, ["其他商户"]))
                
                # 积分计算（消费类交易才有积分）
                points_earned = Decimal("0")
                points_rate = None
                if transaction_type == TransactionType.EXPENSE:
                    points_rate = Decimal(random.choice([1.0, 1.5, 2.0, 3.0, 5.0]))
                    points_earned = amount * points_rate
                
                # 交易状态
                status = random.choices(
                    [TransactionStatus.COMPLETED, TransactionStatus.PENDING, TransactionStatus.FAILED],
                    weights=[90, 5, 5]
                )[0]
                
                transaction = Transaction(
                    card_id=card.id,
                    user_id=card.user_id,
                    transaction_type=transaction_type,
                    amount=amount,
                    transaction_date=transaction_date,
                    merchant_name=merchant_name,
                    description=f"{merchant_name} 消费",
                    category=category,
                    status=status,
                    points_earned=points_earned,
                    points_rate=points_rate,
                    reference_number=f"TXN{random.randint(100000, 999999)}",
                    location=random.choice(["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "西安"]),
                    is_installment=random.choice([True, False]) if transaction_type == TransactionType.EXPENSE and amount > 1000 else False,
                    installment_count=random.choice([3, 6, 12, 24]) if random.choice([True, False]) else None
                )
                
                transactions.append(transaction)
                self.db.add(transaction)
        
        self.db.commit()
        self.transactions = transactions
        print(f"成功生成 {len(transactions)} 笔交易记录")
        return transactions

    def generate_annual_fee_records(self, cards: List[CreditCard]) -> List[AnnualFeeRecord]:
        """生成年费记录"""
        print("正在生成年费记录...")
        
        records = []
        
        for card in cards:
            if not card.annual_fee_rule_id:
                continue
            
            # 获取年费规则
            rule = self.db.query(AnnualFeeRule).filter_by(id=card.annual_fee_rule_id).first()
            if not rule:
                continue
            
            # 为每张卡生成最近2年的年费记录
            for year in [2023, 2024]:
                due_date = date(year, rule.annual_fee_month or 12, rule.annual_fee_day or 31)
                
                # 随机选择年费状态
                waiver_status = random.choices(
                    [WaiverStatus.PENDING, WaiverStatus.WAIVED, WaiverStatus.OVERDUE, WaiverStatus.PAID],
                    weights=[20, 40, 20, 20]
                )[0]
                
                # 支付日期
                payment_date = None
                if waiver_status == WaiverStatus.PAID:
                    payment_date = due_date + timedelta(days=random.randint(1, 30))
                
                record = AnnualFeeRecord(
                    card_id=card.id,
                    fee_year=year,
                    due_date=due_date,
                    fee_amount=rule.base_fee,
                    waiver_status=waiver_status,
                    payment_date=payment_date,
                    notes=f"{year}年度年费记录"
                )
                
                records.append(record)
                self.db.add(record)
        
        self.db.commit()
        print(f"成功生成 {len(records)} 条年费记录")
        return records

    def _generate_card_number(self) -> str:
        """生成信用卡号"""
        # 生成16位信用卡号
        first_part = str(random.randint(4000, 5999))  # Visa/MasterCard前缀
        second_part = "".join([str(random.randint(0, 9)) for _ in range(12)])
        return first_part + second_part

    def update_card_used_amounts(self):
        """根据交易记录更新信用卡已使用额度"""
        print("正在更新信用卡已使用额度...")
        
        for card in self.cards:
            if card.status == "cancelled":
                continue
            
            # 计算该卡的总消费金额（未还款部分）
            total_expense = self.db.query(Transaction).filter(
                Transaction.card_id == card.id,
                Transaction.transaction_type == TransactionType.EXPENSE,
                Transaction.status == TransactionStatus.COMPLETED
            ).count()
            
            # 模拟已使用额度（基于交易数量）
            if total_expense > 0:
                # 根据交易数量调整已使用额度
                used_ratio = min(0.8, total_expense / 100)  # 最高80%使用率
                card.used_amount = card.credit_limit * Decimal(used_ratio)
            
        self.db.commit()
        print("信用卡已使用额度更新完成")

    def generate_all_test_data(self):
        """生成所有测试数据"""
        print("=" * 50)
        print("开始生成信用卡管理系统测试数据")
        print("=" * 50)
        
        try:
            # 0. 清理现有测试数据
            self.clear_test_data()
            
            # 1. 生成用户
            users = self.generate_users(5)
            
            # 2. 生成年费规则
            annual_fee_rules = self.generate_annual_fee_rules()
            
            # 3. 生成信用卡
            cards = self.generate_credit_cards(users)
            
            # 4. 生成交易记录
            transactions = self.generate_transactions(cards)
            
            # 5. 生成年费记录
            annual_fee_records = self.generate_annual_fee_records(cards)
            
            # 6. 更新信用卡已使用额度
            self.update_card_used_amounts()
            
            print("=" * 50)
            print("测试数据生成完成！")
            print(f"生成统计:")
            print(f"  用户数量: {len(users)}")
            print(f"  年费规则: {len(annual_fee_rules)}")
            print(f"  信用卡数量: {len(cards)}")
            print(f"  交易记录: {len(transactions)}")
            print(f"  年费记录: {len(annual_fee_records)}")
            print("=" * 50)
            
            # 显示测试用户信息
            print("\n测试用户登录信息:")
            for i, user in enumerate(users, 1):
                print(f"  用户{i}: {user.username} / TestPass123456")
            
            print("\n现在可以使用这些账号登录系统测试统计功能！")
            
        except Exception as e:
            print(f"生成测试数据时出错: {str(e)}")
            self.db.rollback()
            raise
        finally:
            self.db.close()

    def clear_test_data(self):
        """清理现有测试数据"""
        print("正在清理现有测试数据...")
        
        try:
            # 删除测试用户的所有关联数据
            test_users = self.db.query(User).filter(
                User.username.like('testuser%')
            ).all()
            
            if test_users:
                user_ids = [user.id for user in test_users]
                
                # 删除交易记录
                deleted_transactions = self.db.query(Transaction).filter(
                    Transaction.user_id.in_(user_ids)
                ).delete(synchronize_session=False)
                
                # 删除年费记录
                cards = self.db.query(CreditCard).filter(
                    CreditCard.user_id.in_(user_ids)
                ).all()
                card_ids = [card.id for card in cards]
                
                if card_ids:
                    deleted_annual_fees = self.db.query(AnnualFeeRecord).filter(
                        AnnualFeeRecord.card_id.in_(card_ids)
                    ).delete(synchronize_session=False)
                else:
                    deleted_annual_fees = 0
                
                # 删除信用卡
                deleted_cards = self.db.query(CreditCard).filter(
                    CreditCard.user_id.in_(user_ids)
                ).delete(synchronize_session=False)
                
                # 删除用户
                deleted_users = self.db.query(User).filter(
                    User.username.like('testuser%')
                ).delete(synchronize_session=False)
                
                # 删除年费规则（测试相关的）
                deleted_rules = self.db.query(AnnualFeeRule).filter(
                    AnnualFeeRule.description.like('%年费规则%')
                ).delete(synchronize_session=False)
                
                self.db.commit()
                
                print(f"清理完成：")
                print(f"  删除用户: {deleted_users}")
                print(f"  删除信用卡: {deleted_cards}")
                print(f"  删除交易记录: {deleted_transactions}")
                print(f"  删除年费记录: {deleted_annual_fees}")
                print(f"  删除年费规则: {deleted_rules}")
            else:
                print("没有找到需要清理的测试数据")
                
        except Exception as e:
            print(f"清理数据时出错: {str(e)}")
            self.db.rollback()
            raise

def main():
    """主函数"""
    import sys
    
    generator = TestDataGenerator()
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        generator.clear_test_data()
        generator.db.close()
        print("测试数据清理完成！")
    else:
        generator.generate_all_test_data()

if __name__ == "__main__":
    main() 