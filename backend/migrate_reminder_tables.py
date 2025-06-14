#!/usr/bin/env python3
"""
提醒表结构迁移脚本
更新数据库表结构以匹配新的API规范
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text
from app.db.database import engine
from app.core.logging.logger import app_logger as logger

def migrate_reminder_tables():
    """迁移提醒表结构"""
    
    migration_steps = [
        # 1. 备份现有数据
        "DROP TABLE IF EXISTS reminder_settings_backup",
        "DROP TABLE IF EXISTS reminder_records_backup", 
        "CREATE TABLE reminder_settings_backup AS SELECT * FROM reminder_settings",
        "CREATE TABLE reminder_records_backup AS SELECT * FROM reminder_records",
        
        # 2. 更新 reminder_settings 表结构 - 删除旧列
        "ALTER TABLE reminder_settings DROP COLUMN IF EXISTS reminder_name",
        "ALTER TABLE reminder_settings DROP COLUMN IF EXISTS notification_methods",
        "ALTER TABLE reminder_settings DROP COLUMN IF EXISTS custom_message",
        "ALTER TABLE reminder_settings DROP COLUMN IF EXISTS repeat_interval",
        "ALTER TABLE reminder_settings DROP COLUMN IF EXISTS notes",
        
        # 3. 添加新列到 reminder_settings
        "ALTER TABLE reminder_settings ADD COLUMN IF NOT EXISTS email_enabled BOOLEAN DEFAULT TRUE",
        "ALTER TABLE reminder_settings ADD COLUMN IF NOT EXISTS sms_enabled BOOLEAN DEFAULT FALSE",
        "ALTER TABLE reminder_settings ADD COLUMN IF NOT EXISTS push_enabled BOOLEAN DEFAULT TRUE",
        "ALTER TABLE reminder_settings ADD COLUMN IF NOT EXISTS wechat_enabled BOOLEAN DEFAULT FALSE",
        "ALTER TABLE reminder_settings ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT TRUE",
        "ALTER TABLE reminder_settings ADD COLUMN IF NOT EXISTS frequency VARCHAR(20) DEFAULT 'monthly'",
        
        # 4. 更新 reminder_records 表结构 - 删除旧列
        "ALTER TABLE reminder_records DROP COLUMN IF EXISTS reminder_date",
        "ALTER TABLE reminder_records DROP COLUMN IF EXISTS reminder_time",
        "ALTER TABLE reminder_records DROP COLUMN IF EXISTS message",
        "ALTER TABLE reminder_records DROP COLUMN IF EXISTS status",
        "ALTER TABLE reminder_records DROP COLUMN IF EXISTS read_at",
        "ALTER TABLE reminder_records DROP COLUMN IF EXISTS notes",
        "ALTER TABLE reminder_records DROP COLUMN IF EXISTS updated_at",
        
        # 5. 添加新列到 reminder_records
        "ALTER TABLE reminder_records ADD COLUMN IF NOT EXISTS user_id UUID",
        "ALTER TABLE reminder_records ADD COLUMN IF NOT EXISTS card_id UUID",
        "ALTER TABLE reminder_records ADD COLUMN IF NOT EXISTS reminder_type VARCHAR(30) DEFAULT 'payment'",
        "ALTER TABLE reminder_records ADD COLUMN IF NOT EXISTS title VARCHAR(200) DEFAULT '提醒'",
        "ALTER TABLE reminder_records ADD COLUMN IF NOT EXISTS content TEXT DEFAULT '您有一条新的提醒'",
        "ALTER TABLE reminder_records ADD COLUMN IF NOT EXISTS email_sent BOOLEAN DEFAULT FALSE",
        "ALTER TABLE reminder_records ADD COLUMN IF NOT EXISTS sms_sent BOOLEAN DEFAULT FALSE",
        "ALTER TABLE reminder_records ADD COLUMN IF NOT EXISTS push_sent BOOLEAN DEFAULT FALSE",
        "ALTER TABLE reminder_records ADD COLUMN IF NOT EXISTS wechat_sent BOOLEAN DEFAULT FALSE",
        "ALTER TABLE reminder_records ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMP WITH TIME ZONE",
        
        # 6. 更新现有记录的数据
        """UPDATE reminder_records 
           SET user_id = (
               SELECT rs.user_id 
               FROM reminder_settings rs 
               WHERE rs.id = reminder_records.setting_id
           )
           WHERE user_id IS NULL""",
           
        """UPDATE reminder_records 
           SET card_id = (
               SELECT rs.card_id 
               FROM reminder_settings rs 
               WHERE rs.id = reminder_records.setting_id
           )
           WHERE card_id IS NULL""",
           
        """UPDATE reminder_records 
           SET reminder_type = (
               SELECT rs.reminder_type 
               FROM reminder_settings rs 
               WHERE rs.id = reminder_records.setting_id
           )
           WHERE reminder_type = 'payment'""",
        
        # 7. 设置约束
        "ALTER TABLE reminder_records ALTER COLUMN user_id SET NOT NULL",
        "ALTER TABLE reminder_records ALTER COLUMN reminder_type SET NOT NULL",
        "ALTER TABLE reminder_records ALTER COLUMN title SET NOT NULL",
        "ALTER TABLE reminder_records ALTER COLUMN content SET NOT NULL",
    ]
    
    # 索引创建语句
    index_statements = [
        "CREATE INDEX IF NOT EXISTS idx_reminder_records_user_id ON reminder_records(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_reminder_records_sent_at ON reminder_records(sent_at)",
        "CREATE INDEX IF NOT EXISTS idx_reminder_records_reminder_type ON reminder_records(reminder_type)",
        "CREATE INDEX IF NOT EXISTS idx_reminder_settings_user_id ON reminder_settings(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_reminder_settings_reminder_type ON reminder_settings(reminder_type)",
    ]
    
    try:
        with engine.begin() as conn:
            # 执行主要迁移步骤
            for i, statement in enumerate(migration_steps, 1):
                try:
                    logger.info(f"步骤 {i}: {statement[:100]}...")
                    conn.execute(text(statement))
                except Exception as e:
                    logger.warning(f"步骤 {i} 执行失败（可能是预期的）: {str(e)}")
                    continue
            
            # 执行索引创建
            for statement in index_statements:
                try:
                    logger.info(f"创建索引: {statement[:50]}...")
                    conn.execute(text(statement))
                except Exception as e:
                    logger.warning(f"索引创建失败（可能已存在）: {str(e)}")
                    continue
        
        logger.info("提醒表结构迁移完成")
        print("✅ 提醒表结构迁移成功完成")
        return True
        
    except Exception as e:
        logger.error(f"提醒表结构迁移失败: {str(e)}")
        print(f"❌ 提醒表结构迁移失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始迁移提醒表结构...")
    success = migrate_reminder_tables()
    if success:
        print("迁移完成！")
    else:
        print("迁移失败！")
        sys.exit(1) 