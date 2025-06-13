#!/usr/bin/env python3
"""
银行数据初始化脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.database.card import Bank
from app.models.database.user import User  # 确保所有模型都被导入

def init_banks():
    """初始化银行数据"""
    db: Session = SessionLocal()
    
    try:
        # 检查是否已有银行数据
        existing_count = db.query(Bank).count()
        if existing_count > 0:
            print(f"银行数据已存在 {existing_count} 条记录，跳过初始化")
            return
        
        # 中国主要银行数据
        banks_data = [
            {"bank_code": "ICBC", "bank_name": "中国工商银行", "sort_order": 1},
            {"bank_code": "ABC", "bank_name": "中国农业银行", "sort_order": 2},
            {"bank_code": "BOC", "bank_name": "中国银行", "sort_order": 3},
            {"bank_code": "CCB", "bank_name": "中国建设银行", "sort_order": 4},
            {"bank_code": "BOCOM", "bank_name": "交通银行", "sort_order": 5},
            {"bank_code": "CMB", "bank_name": "招商银行", "sort_order": 6},
            {"bank_code": "CITIC", "bank_name": "中信银行", "sort_order": 7},
            {"bank_code": "CEB", "bank_name": "光大银行", "sort_order": 8},
            {"bank_code": "CMBC", "bank_name": "中国民生银行", "sort_order": 9},
            {"bank_code": "PAB", "bank_name": "平安银行", "sort_order": 10},
            {"bank_code": "SPDB", "bank_name": "浦发银行", "sort_order": 11},
            {"bank_code": "CIB", "bank_name": "兴业银行", "sort_order": 12},
            {"bank_code": "HXB", "bank_name": "华夏银行", "sort_order": 13},
            {"bank_code": "GDB", "bank_name": "广发银行", "sort_order": 14},
            {"bank_code": "PSBC", "bank_name": "中国邮政储蓄银行", "sort_order": 15},
        ]
        
        # 创建银行记录
        for bank_data in banks_data:
            bank = Bank(**bank_data)
            db.add(bank)
        
        db.commit()
        print(f"成功初始化 {len(banks_data)} 个银行数据")
        
        # 显示创建的银行
        banks = db.query(Bank).order_by(Bank.sort_order).all()
        print("\n已创建的银行列表:")
        for bank in banks:
            print(f"- {bank.bank_code}: {bank.bank_name}")
            
    except Exception as e:
        db.rollback()
        print(f"初始化银行数据失败: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("开始初始化银行数据...")
    init_banks()
    print("银行数据初始化完成！") 