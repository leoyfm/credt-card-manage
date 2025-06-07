-- 信用卡管理系统数据库初始化脚本

-- 创建数据库扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 银行表
CREATE TABLE IF NOT EXISTS banks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) UNIQUE NOT NULL,
    logo_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 年费规则表
CREATE TABLE IF NOT EXISTS annual_fee_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_name VARCHAR(100) NOT NULL,
    fee_type VARCHAR(20) NOT NULL CHECK (fee_type IN ('rigid', 'transaction_count', 'points_exchange', 'transaction_amount')),
    base_fee DECIMAL(10,2) NOT NULL DEFAULT 0,
    waiver_condition_value DECIMAL(15,2), -- 减免条件的数值（次数、积分数、金额等）
    waiver_period_months INTEGER DEFAULT 12, -- 考核周期（月）
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 信用卡表
CREATE TABLE IF NOT EXISTS credit_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    bank_id UUID REFERENCES banks(id),
    card_name VARCHAR(100) NOT NULL,
    card_number_last_four VARCHAR(4) NOT NULL,
    credit_limit DECIMAL(15,2) NOT NULL,
    available_limit DECIMAL(15,2) NOT NULL,
    annual_fee_rule_id UUID REFERENCES annual_fee_rules(id),
    billing_day INTEGER CHECK (billing_day >= 1 AND billing_day <= 31),
    due_day INTEGER CHECK (due_day >= 1 AND due_day <= 31),
    card_activation_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 年费记录表
CREATE TABLE IF NOT EXISTS annual_fee_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    card_id UUID REFERENCES credit_cards(id) ON DELETE CASCADE,
    fee_year INTEGER NOT NULL, -- 年费所属年份
    due_date DATE NOT NULL, -- 年费到期日期
    fee_amount DECIMAL(10,2) NOT NULL, -- 应付年费金额
    waiver_status VARCHAR(20) DEFAULT 'pending' CHECK (waiver_status IN ('pending', 'waived', 'paid', 'overdue')),
    waiver_condition_met BOOLEAN DEFAULT FALSE, -- 是否满足减免条件
    current_progress DECIMAL(15,2) DEFAULT 0, -- 当前进度（刷卡次数、金额、积分等）
    payment_date DATE, -- 实际支付日期
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(card_id, fee_year)
);

-- 还款记录表
CREATE TABLE IF NOT EXISTS payment_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    card_id UUID REFERENCES credit_cards(id) ON DELETE CASCADE,
    amount DECIMAL(15,2) NOT NULL,
    payment_date DATE NOT NULL,
    due_date DATE NOT NULL,
    is_full_payment BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 还款提醒表
CREATE TABLE IF NOT EXISTS payment_reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    card_id UUID REFERENCES credit_cards(id) ON DELETE CASCADE,
    reminder_date DATE NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    is_sent BOOLEAN DEFAULT FALSE,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 消费记录表
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    card_id UUID REFERENCES credit_cards(id) ON DELETE CASCADE,
    amount DECIMAL(15,2) NOT NULL,
    merchant VARCHAR(255),
    category VARCHAR(100),
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 插入示例银行数据
INSERT INTO banks (name, code) VALUES 
('中国银行', 'BOC'),
('工商银行', 'ICBC'),
('建设银行', 'CCB'),
('农业银行', 'ABC'),
('招商银行', 'CMB'),
('交通银行', 'COMM'),
('浦发银行', 'SPDB'),
('中信银行', 'CITIC')
ON CONFLICT (code) DO NOTHING;

-- 插入示例年费规则数据
INSERT INTO annual_fee_rules (rule_name, fee_type, base_fee, waiver_condition_value, waiver_period_months, description) VALUES 
('刚性年费-标准卡', 'rigid', 200.00, NULL, 12, '普通信用卡年费，无减免条件'),
('刚性年费-金卡', 'rigid', 600.00, NULL, 12, '金卡年费，无减免条件'),
('刚性年费-白金卡', 'rigid', 2000.00, NULL, 12, '白金卡年费，无减免条件'),
('刷卡次数减免-标准', 'transaction_count', 200.00, 12, 12, '年内刷卡满12次可减免年费'),
('刷卡次数减免-金卡', 'transaction_count', 600.00, 18, 12, '年内刷卡满18次可减免年费'),
('刷卡金额减免-标准', 'transaction_amount', 200.00, 50000, 12, '年内刷卡满5万元可减免年费'),
('刷卡金额减免-金卡', 'transaction_amount', 600.00, 100000, 12, '年内刷卡满10万元可减免年费'),
('积分兑换减免-标准', 'points_exchange', 200.00, 20000, 12, '可用2万积分兑换年费'),
('积分兑换减免-金卡', 'points_exchange', 600.00, 60000, 12, '可用6万积分兑换年费'),
('免年费卡', 'rigid', 0.00, NULL, 12, '终身免年费信用卡')
ON CONFLICT DO NOTHING;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_credit_cards_user_id ON credit_cards(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_cards_annual_fee_rule ON credit_cards(annual_fee_rule_id);
CREATE INDEX IF NOT EXISTS idx_annual_fee_records_card_id ON annual_fee_records(card_id);
CREATE INDEX IF NOT EXISTS idx_annual_fee_records_year ON annual_fee_records(fee_year);
CREATE INDEX IF NOT EXISTS idx_annual_fee_records_due_date ON annual_fee_records(due_date);
CREATE INDEX IF NOT EXISTS idx_annual_fee_records_status ON annual_fee_records(waiver_status);
CREATE INDEX IF NOT EXISTS idx_payment_records_card_id ON payment_records(card_id);
CREATE INDEX IF NOT EXISTS idx_payment_reminders_card_id ON payment_reminders(card_id);
CREATE INDEX IF NOT EXISTS idx_transactions_card_id ON transactions(card_id);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_credit_cards_updated_at BEFORE UPDATE ON credit_cards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_annual_fee_records_updated_at BEFORE UPDATE ON annual_fee_records
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 创建年费记录的函数
CREATE OR REPLACE FUNCTION create_annual_fee_record(
    p_card_id UUID,
    p_fee_year INTEGER
) RETURNS UUID AS $$
DECLARE
    v_record_id UUID;
    v_rule_id UUID;
    v_base_fee DECIMAL(10,2);
    v_activation_date DATE;
    v_due_date DATE;
BEGIN
    -- 获取信用卡的年费规则和激活日期
    SELECT annual_fee_rule_id, card_activation_date 
    INTO v_rule_id, v_activation_date
    FROM credit_cards 
    WHERE id = p_card_id;
    
    -- 获取年费金额
    SELECT base_fee 
    INTO v_base_fee
    FROM annual_fee_rules 
    WHERE id = v_rule_id;
    
    -- 计算年费到期日期（激活日期周年）
    v_due_date := v_activation_date + INTERVAL '1 year' * (p_fee_year - EXTRACT(YEAR FROM v_activation_date));
    
    -- 创建年费记录
    INSERT INTO annual_fee_records (card_id, fee_year, due_date, fee_amount)
    VALUES (p_card_id, p_fee_year, v_due_date, v_base_fee)
    RETURNING id INTO v_record_id;
    
    RETURN v_record_id;
END;
$$ LANGUAGE plpgsql;

-- 检查年费减免条件的函数
CREATE OR REPLACE FUNCTION check_annual_fee_waiver(
    p_card_id UUID,
    p_fee_year INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    v_rule_id UUID;
    v_fee_type VARCHAR(20);
    v_waiver_value DECIMAL(15,2);
    v_current_progress DECIMAL(15,2) := 0;
    v_start_date DATE;
    v_end_date DATE;
BEGIN
    -- 获取年费规则
    SELECT r.id, r.fee_type, r.waiver_condition_value
    INTO v_rule_id, v_fee_type, v_waiver_value
    FROM credit_cards c
    JOIN annual_fee_rules r ON c.annual_fee_rule_id = r.id
    WHERE c.id = p_card_id;
    
    -- 如果是刚性年费，直接返回FALSE
    IF v_fee_type = 'rigid' THEN
        RETURN FALSE;
    END IF;
    
    -- 计算考核周期
    v_start_date := DATE(p_fee_year || '-01-01');
    v_end_date := DATE(p_fee_year || '-12-31');
    
    -- 根据不同类型计算当前进度
    IF v_fee_type = 'transaction_count' THEN
        -- 计算刷卡次数
        SELECT COUNT(*)
        INTO v_current_progress
        FROM transactions
        WHERE card_id = p_card_id
        AND transaction_date BETWEEN v_start_date AND v_end_date;
        
    ELSIF v_fee_type = 'transaction_amount' THEN
        -- 计算刷卡金额
        SELECT COALESCE(SUM(amount), 0)
        INTO v_current_progress
        FROM transactions
        WHERE card_id = p_card_id
        AND transaction_date BETWEEN v_start_date AND v_end_date;
        
    ELSIF v_fee_type = 'points_exchange' THEN
        -- 积分兑换逻辑（这里假设用户主动兑换，需要额外的积分表来跟踪）
        v_current_progress := v_waiver_value; -- 临时逻辑，实际需要积分系统
    END IF;
    
    -- 更新年费记录的当前进度
    UPDATE annual_fee_records 
    SET current_progress = v_current_progress,
        waiver_condition_met = (v_current_progress >= v_waiver_value)
    WHERE card_id = p_card_id AND fee_year = p_fee_year;
    
    RETURN v_current_progress >= v_waiver_value;
END;
$$ LANGUAGE plpgsql; 