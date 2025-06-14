#!/usr/bin/env python3
"""
创建管理员用户脚本
"""
from app.models.database.user import User
from app.db.database import SessionLocal
import bcrypt
import uuid

def create_admin_user():
    """创建管理员用户"""
    db = SessionLocal()
    
    # 检查是否已存在管理员
    existing_admin = db.query(User).filter(User.username == "admin").first()
    if existing_admin:
        print("管理员用户已存在")
        # 设置为管理员
        existing_admin.is_admin = True
        db.commit()
        print(f"已将用户 {existing_admin.username} 设置为管理员")
        return existing_admin
    
    # 创建新的管理员用户
    password = "Admin123456"
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    admin_user = User(
        id=uuid.uuid4(),
        username="admin",
        email="admin@example.com",
        password_hash=password_hash,
        nickname="系统管理员",
        is_active=True,
        is_verified=True,
        is_admin=True,
        timezone="Asia/Shanghai",
        language="zh-CN",
        currency="CNY"
    )
    
    try:
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("管理员用户创建成功!")
        print(f"用户名: {admin_user.username}")
        print(f"密码: {password}")
        print(f"邮箱: {admin_user.email}")
        print(f"用户ID: {admin_user.id}")
        
        return admin_user
        
    except Exception as e:
        db.rollback()
        print(f"创建管理员用户失败: {e}")
        return None
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user() 