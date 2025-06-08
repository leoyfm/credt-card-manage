import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 加载环境变量
load_dotenv()

# 创建数据库连接
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()
try:
    # 检查年费规则表结构
    print("=== 年费规则表结构 ===")
    result = db.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'annual_fee_rules' 
        ORDER BY ordinal_position
    """))
    for row in result.fetchall():
        print(f"{row.column_name}: {row.data_type} {'NULL' if row.is_nullable == 'YES' else 'NOT NULL'} {row.column_default or ''}")
    
    print("\n=== 年费记录表结构 ===")
    result = db.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'annual_fee_records' 
        ORDER BY ordinal_position
    """))
    for row in result.fetchall():
        print(f"{row.column_name}: {row.data_type} {'NULL' if row.is_nullable == 'YES' else 'NOT NULL'} {row.column_default or ''}")
    
    print("\n=== 信用卡表结构 ===")
    result = db.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'credit_cards' 
        ORDER BY ordinal_position
    """))
    for row in result.fetchall():
        print(f"{row.column_name}: {row.data_type} {'NULL' if row.is_nullable == 'YES' else 'NOT NULL'} {row.column_default or ''}")
        
finally:
    db.close() 