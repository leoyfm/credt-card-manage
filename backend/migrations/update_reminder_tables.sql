-- 更新提醒表结构以匹配新的API规范
-- 执行时间: 2025-06-14

-- 1. 备份现有数据
CREATE TABLE reminder_settings_backup AS SELECT * FROM reminder_settings;
CREATE TABLE reminder_records_backup AS SELECT * FROM reminder_records;

-- 2. 更新 reminder_settings 表结构
ALTER TABLE reminder_settings 
DROP COLUMN IF EXISTS reminder_name,
DROP COLUMN IF EXISTS notification_methods,
DROP COLUMN IF EXISTS custom_message,
DROP COLUMN IF EXISTS repeat_interval,
DROP COLUMN IF EXISTS notes;

ALTER TABLE reminder_settings 
ADD COLUMN IF NOT EXISTS email_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS sms_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS push_enabled BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS wechat_enabled BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS is_recurring BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS frequency VARCHAR(20) DEFAULT 'monthly';

-- 3. 更新 reminder_records 表结构
ALTER TABLE reminder_records 
DROP COLUMN IF EXISTS reminder_date,
DROP COLUMN IF EXISTS reminder_time,
DROP COLUMN IF EXISTS message,
DROP COLUMN IF EXISTS status,
DROP COLUMN IF EXISTS read_at,
DROP COLUMN IF EXISTS notes,
DROP COLUMN IF EXISTS updated_at;

ALTER TABLE reminder_records 
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS card_id UUID REFERENCES credit_cards(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS reminder_type VARCHAR(30) NOT NULL DEFAULT 'payment',
ADD COLUMN IF NOT EXISTS title VARCHAR(200) NOT NULL DEFAULT '提醒',
ADD COLUMN IF NOT EXISTS content TEXT NOT NULL DEFAULT '您有一条新的提醒',
ADD COLUMN IF NOT EXISTS email_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS sms_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS push_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS wechat_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMP WITH TIME ZONE;

-- 4. 更新现有记录的 user_id（从关联的 setting 获取）
UPDATE reminder_records 
SET user_id = (
    SELECT rs.user_id 
    FROM reminder_settings rs 
    WHERE rs.id = reminder_records.setting_id
)
WHERE user_id IS NULL;

-- 5. 更新现有记录的 card_id（从关联的 setting 获取）
UPDATE reminder_records 
SET card_id = (
    SELECT rs.card_id 
    FROM reminder_settings rs 
    WHERE rs.id = reminder_records.setting_id
)
WHERE card_id IS NULL;

-- 6. 更新现有记录的 reminder_type（从关联的 setting 获取）
UPDATE reminder_records 
SET reminder_type = (
    SELECT rs.reminder_type 
    FROM reminder_settings rs 
    WHERE rs.id = reminder_records.setting_id
)
WHERE reminder_type = 'payment';

-- 7. 设置 user_id 为 NOT NULL
ALTER TABLE reminder_records ALTER COLUMN user_id SET NOT NULL;

-- 8. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_reminder_records_user_id ON reminder_records(user_id);
CREATE INDEX IF NOT EXISTS idx_reminder_records_sent_at ON reminder_records(sent_at);
CREATE INDEX IF NOT EXISTS idx_reminder_records_reminder_type ON reminder_records(reminder_type);
CREATE INDEX IF NOT EXISTS idx_reminder_settings_user_id ON reminder_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_reminder_settings_reminder_type ON reminder_settings(reminder_type);

-- 9. 添加注释
COMMENT ON COLUMN reminder_settings.email_enabled IS '邮件提醒';
COMMENT ON COLUMN reminder_settings.sms_enabled IS '短信提醒';
COMMENT ON COLUMN reminder_settings.push_enabled IS '推送提醒';
COMMENT ON COLUMN reminder_settings.wechat_enabled IS '微信提醒';
COMMENT ON COLUMN reminder_settings.is_recurring IS '是否循环';
COMMENT ON COLUMN reminder_settings.frequency IS '频率';

COMMENT ON COLUMN reminder_records.user_id IS '用户ID';
COMMENT ON COLUMN reminder_records.card_id IS '信用卡ID';
COMMENT ON COLUMN reminder_records.reminder_type IS '提醒类型';
COMMENT ON COLUMN reminder_records.title IS '提醒标题';
COMMENT ON COLUMN reminder_records.content IS '提醒内容';
COMMENT ON COLUMN reminder_records.email_sent IS '邮件是否发送';
COMMENT ON COLUMN reminder_records.sms_sent IS '短信是否发送';
COMMENT ON COLUMN reminder_records.push_sent IS '推送是否发送';
COMMENT ON COLUMN reminder_records.wechat_sent IS '微信是否发送';
COMMENT ON COLUMN reminder_records.scheduled_at IS '计划发送时间';

COMMIT; 