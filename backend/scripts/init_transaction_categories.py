#!/usr/bin/env python3
"""
初始化交易分类数据
创建系统默认的交易分类，包括餐饮、购物、交通等常用分类
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.database.transaction import TransactionCategory
from app.core.logging.logger import app_logger as logger


def init_transaction_categories():
    """初始化交易分类数据"""
    db: Session = SessionLocal()
    
    try:
        # 检查是否已经有分类数据
        existing_count = db.query(TransactionCategory).count()
        if existing_count > 0:
            logger.info(f"交易分类已存在 {existing_count} 个，跳过初始化")
            return
        
        # 定义系统默认分类
        categories = [
            # 一级分类
            {
                "name": "餐饮美食",
                "icon": "restaurant",
                "color": "#FF6B6B",
                "is_system": True,
                "sort_order": 1
            },
            {
                "name": "购物消费",
                "icon": "shopping_cart",
                "color": "#4ECDC4",
                "is_system": True,
                "sort_order": 2
            },
            {
                "name": "交通出行",
                "icon": "directions_car",
                "color": "#45B7D1",
                "is_system": True,
                "sort_order": 3
            },
            {
                "name": "生活服务",
                "icon": "home",
                "color": "#96CEB4",
                "is_system": True,
                "sort_order": 4
            },
            {
                "name": "娱乐休闲",
                "icon": "movie",
                "color": "#FFEAA7",
                "is_system": True,
                "sort_order": 5
            },
            {
                "name": "医疗健康",
                "icon": "local_hospital",
                "color": "#DDA0DD",
                "is_system": True,
                "sort_order": 6
            },
            {
                "name": "教育培训",
                "icon": "school",
                "color": "#98D8C8",
                "is_system": True,
                "sort_order": 7
            },
            {
                "name": "旅游度假",
                "icon": "flight",
                "color": "#F7DC6F",
                "is_system": True,
                "sort_order": 8
            },
            {
                "name": "投资理财",
                "icon": "trending_up",
                "color": "#BB8FCE",
                "is_system": True,
                "sort_order": 9
            },
            {
                "name": "转账汇款",
                "icon": "account_balance",
                "color": "#85C1E9",
                "is_system": True,
                "sort_order": 10
            },
            {
                "name": "信用卡还款",
                "icon": "credit_card",
                "color": "#F8C471",
                "is_system": True,
                "sort_order": 11
            },
            {
                "name": "其他支出",
                "icon": "more_horiz",
                "color": "#D5DBDB",
                "is_system": True,
                "sort_order": 99
            }
        ]
        
        # 创建分类
        created_categories = []
        for cat_data in categories:
            category = TransactionCategory(**cat_data)
            db.add(category)
            created_categories.append(category)
        
        db.commit()
        
        # 刷新对象以获取ID
        for category in created_categories:
            db.refresh(category)
        
        logger.info(f"成功创建 {len(created_categories)} 个交易分类")
        
        # 创建二级分类（子分类）
        subcategories = []
        
        # 餐饮美食子分类
        restaurant_parent = next(cat for cat in created_categories if cat.name == "餐饮美食")
        restaurant_subs = [
            {"name": "正餐", "parent_id": restaurant_parent.id, "icon": "restaurant", "color": "#FF6B6B"},
            {"name": "快餐", "parent_id": restaurant_parent.id, "icon": "fastfood", "color": "#FF6B6B"},
            {"name": "咖啡茶饮", "parent_id": restaurant_parent.id, "icon": "local_cafe", "color": "#FF6B6B"},
            {"name": "零食小食", "parent_id": restaurant_parent.id, "icon": "cake", "color": "#FF6B6B"},
        ]
        
        # 购物消费子分类
        shopping_parent = next(cat for cat in created_categories if cat.name == "购物消费")
        shopping_subs = [
            {"name": "服装鞋帽", "parent_id": shopping_parent.id, "icon": "checkroom", "color": "#4ECDC4"},
            {"name": "数码电器", "parent_id": shopping_parent.id, "icon": "devices", "color": "#4ECDC4"},
            {"name": "日用百货", "parent_id": shopping_parent.id, "icon": "shopping_basket", "color": "#4ECDC4"},
            {"name": "美妆护肤", "parent_id": shopping_parent.id, "icon": "face", "color": "#4ECDC4"},
        ]
        
        # 交通出行子分类
        transport_parent = next(cat for cat in created_categories if cat.name == "交通出行")
        transport_subs = [
            {"name": "公共交通", "parent_id": transport_parent.id, "icon": "directions_bus", "color": "#45B7D1"},
            {"name": "打车出行", "parent_id": transport_parent.id, "icon": "local_taxi", "color": "#45B7D1"},
            {"name": "加油费用", "parent_id": transport_parent.id, "icon": "local_gas_station", "color": "#45B7D1"},
            {"name": "停车费用", "parent_id": transport_parent.id, "icon": "local_parking", "color": "#45B7D1"},
        ]
        
        # 合并所有子分类
        all_subcategories = restaurant_subs + shopping_subs + transport_subs
        
        # 创建子分类
        created_subcategories = []
        for subcat_data in all_subcategories:
            subcat_data.update({
                "is_system": True,
                "is_active": True,
                "sort_order": 0
            })
            subcategory = TransactionCategory(**subcat_data)
            db.add(subcategory)
            created_subcategories.append(subcategory)
        
        db.commit()
        
        logger.info(f"成功创建 {len(created_subcategories)} 个交易子分类")
        logger.info("交易分类初始化完成")
        
    except Exception as e:
        db.rollback()
        logger.error(f"初始化交易分类失败: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_transaction_categories() 