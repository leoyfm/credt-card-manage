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
    print("=== 信用卡表完整结构 ===")
    result = db.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'credit_cards' 
        ORDER BY ordinal_position
    """))
    for row in result.fetchall():
        print(f"{row.column_name}: {row.data_type} {'NULL' if row.is_nullable == 'YES' else 'NOT NULL'} {row.column_default or ''}")
        
    print("\n=== 检查外键约束 ===")
    result = db.execute(text("""
        SELECT 
            tc.constraint_name, 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name 
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
        WHERE constraint_type = 'FOREIGN KEY' 
        AND (tc.table_name = 'credit_cards' OR tc.table_name = 'annual_fee_records')
    """))
    for row in result.fetchall():
        print(f"{row.table_name}.{row.column_name} -> {row.foreign_table_name}.{row.foreign_column_name}")
        
finally:
    db.close() 