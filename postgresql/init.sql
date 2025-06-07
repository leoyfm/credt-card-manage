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

-- 信用卡表
CREATE TABLE IF NOT EXISTS credit_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    bank_id UUID REFERENCES banks(id),
    card_name VARCHAR(100) NOT NULL,
    card_number_last_four VARCHAR(4) NOT NULL,
    credit_limit DECIMAL(15,2) NOT NULL,
    available_limit DECIMAL(15,2) NOT NULL,
    annual_fee DECIMAL(10,2) DEFAULT 0,
    billing_day INTEGER CHECK (billing_day >= 1 AND billing_day <= 31),
    due_day INTEGER CHECK (due_day >= 1 AND due_day <= 31),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
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

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_credit_cards_user_id ON credit_cards(user_id);
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