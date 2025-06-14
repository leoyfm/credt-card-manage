-- 创建推荐模块相关表
-- 执行时间: 2024-12-28

-- 1. 创建推荐规则表
CREATE TABLE IF NOT EXISTS recommendation_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_name VARCHAR(100) NOT NULL,
    rule_type VARCHAR(30) NOT NULL,
    conditions JSONB NOT NULL,
    recommendation_title VARCHAR(200),
    recommendation_content TEXT,
    action_type VARCHAR(30),
    priority INTEGER DEFAULT 1 CHECK (priority >= 1 AND priority <= 10),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. 创建推荐记录表
CREATE TABLE IF NOT EXISTS recommendation_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rule_id UUID REFERENCES recommendation_rules(id) ON DELETE SET NULL,
    recommendation_type VARCHAR(30) NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    action_data JSONB,
    user_action VARCHAR(20),
    feedback TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. 创建索引
-- 推荐规则表索引
CREATE INDEX IF NOT EXISTS idx_recommendation_rules_type ON recommendation_rules(rule_type);
CREATE INDEX IF NOT EXISTS idx_recommendation_rules_active ON recommendation_rules(is_active);
CREATE INDEX IF NOT EXISTS idx_recommendation_rules_priority ON recommendation_rules(priority DESC);

-- 推荐记录表索引
CREATE INDEX IF NOT EXISTS idx_recommendation_records_user_id ON recommendation_records(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_records_rule_id ON recommendation_records(rule_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_records_type ON recommendation_records(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_recommendation_records_status ON recommendation_records(status);
CREATE INDEX IF NOT EXISTS idx_recommendation_records_user_action ON recommendation_records(user_action);
CREATE INDEX IF NOT EXISTS idx_recommendation_records_created_at ON recommendation_records(created_at DESC);

-- 4. 创建复合索引
CREATE INDEX IF NOT EXISTS idx_recommendation_records_user_status ON recommendation_records(user_id, status);
CREATE INDEX IF NOT EXISTS idx_recommendation_records_user_type ON recommendation_records(user_id, recommendation_type);

-- 5. 添加表注释
COMMENT ON TABLE recommendation_rules IS '推荐规则表 - 存储系统推荐规则配置';
COMMENT ON TABLE recommendation_records IS '推荐记录表 - 存储用户推荐记录';

-- 6. 添加字段注释
-- 推荐规则表字段注释
COMMENT ON COLUMN recommendation_rules.id IS '规则ID';
COMMENT ON COLUMN recommendation_rules.rule_name IS '规则名称';
COMMENT ON COLUMN recommendation_rules.rule_type IS '规则类型';
COMMENT ON COLUMN recommendation_rules.conditions IS '规则条件(JSON格式)';
COMMENT ON COLUMN recommendation_rules.recommendation_title IS '推荐标题';
COMMENT ON COLUMN recommendation_rules.recommendation_content IS '推荐内容';
COMMENT ON COLUMN recommendation_rules.action_type IS '行动类型';
COMMENT ON COLUMN recommendation_rules.priority IS '优先级(1-10)';
COMMENT ON COLUMN recommendation_rules.is_active IS '是否激活';
COMMENT ON COLUMN recommendation_rules.created_at IS '创建时间';
COMMENT ON COLUMN recommendation_rules.updated_at IS '更新时间';

-- 推荐记录表字段注释
COMMENT ON COLUMN recommendation_records.id IS '记录ID';
COMMENT ON COLUMN recommendation_records.user_id IS '用户ID';
COMMENT ON COLUMN recommendation_records.rule_id IS '规则ID';
COMMENT ON COLUMN recommendation_records.recommendation_type IS '推荐类型';
COMMENT ON COLUMN recommendation_records.title IS '标题';
COMMENT ON COLUMN recommendation_records.content IS '内容';
COMMENT ON COLUMN recommendation_records.action_data IS '行动数据(JSON格式)';
COMMENT ON COLUMN recommendation_records.user_action IS '用户行动';
COMMENT ON COLUMN recommendation_records.feedback IS '用户反馈';
COMMENT ON COLUMN recommendation_records.status IS '状态';
COMMENT ON COLUMN recommendation_records.created_at IS '创建时间';
COMMENT ON COLUMN recommendation_records.updated_at IS '更新时间';

-- 7. 插入示例推荐规则
INSERT INTO recommendation_rules (
    rule_name, rule_type, conditions, recommendation_title, 
    recommendation_content, action_type, priority, is_active
) VALUES 
(
    '低利用率提醒',
    'card_usage',
    '{"credit_utilization": {"max": 0.1}}',
    '信用卡利用率较低',
    '您的信用卡利用率较低，建议适当增加使用以提升信用记录',
    'increase_usage',
    8,
    true
),
(
    '高利用率警告',
    'card_usage', 
    '{"credit_utilization": {"min": 0.8}}',
    '信用卡利用率过高',
    '您的信用卡利用率过高，建议及时还款或申请提额',
    'reduce_usage',
    9,
    true
),
(
    '年费减免提醒',
    'fee_optimization',
    '{"annual_fee": {"min": 100}, "fee_waivable": true}',
    '年费减免机会',
    '您的信用卡可通过达成消费条件减免年费',
    'check_waiver_rules',
    7,
    true
),
(
    '消费类别优化',
    'category_analysis',
    '{"category_percentage": {"min": 0.3}}',
    '消费类别集中度高',
    '建议选择在您常用消费类别有优惠的信用卡',
    'optimize_card_for_category',
    6,
    true
)
ON CONFLICT DO NOTHING;

-- 10. 验证表创建
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('recommendation_rules', 'recommendation_records')
ORDER BY table_name, ordinal_position; 