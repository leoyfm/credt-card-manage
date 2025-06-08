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
    # 直接使用SQL查询，避免ORM关系问题
    result = db.execute(text("SELECT id, bank_name, card_name, card_type FROM credit_cards WHERE is_deleted = false"))
    cards = result.fetchall()
    
    print(f'找到 {len(cards)} 张信用卡')
    for card in cards:
        print(f'ID: {card.id}, 银行: {card.bank_name}, 卡名: {card.card_name}, 类型: {card.card_type}')
        
finally:
    db.close() 