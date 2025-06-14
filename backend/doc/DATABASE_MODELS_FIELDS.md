# 信用卡管理系统 - 数据库模型字段列表

**版本**: v1.0  
**作者**: LEO  
**邮箱**: leoyfm@gmail.com  

## 1. 用户模块

### 1.1 用户表 (users)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 用户ID |
| username | VARCHAR(50) | NOT NULL, UNIQUE | - | 用户名 |
| email | VARCHAR(100) | NOT NULL, UNIQUE | - | 邮箱地址 |
| password_hash | VARCHAR(255) | NOT NULL | - | 密码哈希 |
| nickname | VARCHAR(50) | - | NULL | 昵称 |
| phone | VARCHAR(20) | - | NULL | 手机号 |
| avatar_url | VARCHAR(500) | - | NULL | 头像URL |
| is_active | BOOLEAN | - | true | 是否激活 |
| is_verified | BOOLEAN | - | false | 是否已验证 |
| is_admin | BOOLEAN | - | false | 是否管理员 |
| timezone | VARCHAR(50) | - | 'Asia/Shanghai' | 时区 |
| language | VARCHAR(10) | - | 'zh-CN' | 语言偏好 |
| currency | VARCHAR(10) | - | 'CNY' | 默认货币 |
| last_login_at | TIMESTAMP WITH TIME ZONE | - | NULL | 最后登录时间 |
| email_verified_at | TIMESTAMP WITH TIME ZONE | - | NULL | 邮箱验证时间 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 更新时间 |

### 1.2 验证码表 (verification_codes)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 验证码ID |
| user_id | UUID | REFERENCES users(id) ON DELETE CASCADE | - | 用户ID |
| code | VARCHAR(10) | NOT NULL | - | 验证码 |
| code_type | VARCHAR(20) | NOT NULL | - | 验证码类型 |
| expires_at | TIMESTAMP WITH TIME ZONE | NOT NULL | - | 过期时间 |
| is_used | BOOLEAN | - | false | 是否已使用 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |

**code_type 枚举值**: `email_verify`, `password_reset`, `phone_verify`

### 1.3 登录日志表 (login_logs)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 日志ID |
| user_id | UUID | REFERENCES users(id) ON DELETE SET NULL | - | 用户ID |
| login_type | VARCHAR(20) | NOT NULL | - | 登录类型 |
| login_method | VARCHAR(20) | NOT NULL | - | 登录方式 |
| ip_address | INET | - | NULL | IP地址 |
| user_agent | TEXT | - | NULL | 用户代理 |
| location | VARCHAR(100) | - | NULL | 地理位置 |
| is_success | BOOLEAN | - | true | 是否成功 |
| failure_reason | VARCHAR(100) | - | NULL | 失败原因 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |

**login_type 枚举值**: `username`, `phone`, `wechat`  
**login_method 枚举值**: `password`, `code`, `oauth`

### 1.4 微信绑定表 (wechat_bindings)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 绑定ID |
| user_id | UUID | REFERENCES users(id) ON DELETE CASCADE | - | 用户ID |
| openid | VARCHAR(100) | NOT NULL, UNIQUE | - | 微信OpenID |
| unionid | VARCHAR(100) | - | NULL | 微信UnionID |
| nickname | VARCHAR(100) | - | NULL | 微信昵称 |
| avatar_url | VARCHAR(500) | - | NULL | 微信头像 |
| is_active | BOOLEAN | - | true | 是否激活 |
| bound_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 绑定时间 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 更新时间 |

## 2. 银行和信用卡模块

### 2.1 银行表 (banks)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 银行ID |
| bank_code | VARCHAR(20) | NOT NULL, UNIQUE | - | 银行代码 |
| bank_name | VARCHAR(100) | NOT NULL | - | 银行名称 |
| bank_logo | VARCHAR(500) | - | NULL | 银行logo |
| is_active | BOOLEAN | - | true | 是否激活 |
| sort_order | INTEGER | - | 0 | 排序 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 更新时间 |

### 2.2 信用卡表 (credit_cards)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 信用卡ID |
| user_id | UUID | NOT NULL, REFERENCES users(id) ON DELETE CASCADE | - | 用户ID |
| bank_id | UUID | REFERENCES banks(id) | - | 银行ID |
| card_number | VARCHAR(100) | NOT NULL | - | 卡号(加密存储) |
| card_name | VARCHAR(100) | NOT NULL | - | 卡片名称 |
| card_type | VARCHAR(20) | - | 'credit' | 卡片类型 |
| card_network | VARCHAR(20) | - | NULL | 卡组织 |
| card_level | VARCHAR(20) | - | NULL | 卡片等级 |
| credit_limit | DECIMAL(15,2) | NOT NULL | - | 信用额度 |
| available_limit | DECIMAL(15,2) | - | NULL | 可用额度 |
| used_limit | DECIMAL(15,2) | - | 0 | 已用额度 |
| expiry_month | INTEGER | NOT NULL | - | 有效期月份 |
| expiry_year | INTEGER | NOT NULL | - | 有效期年份 |
| billing_date | INTEGER | - | NULL | 账单日 |
| due_date | INTEGER | - | NULL | 还款日 |
| annual_fee | DECIMAL(10,2) | - | 0 | 年费金额 |
| fee_waivable | BOOLEAN | - | false | 年费是否可减免 |
| fee_auto_deduct | BOOLEAN | - | false | 是否自动扣费 |
| fee_due_month | INTEGER | - | NULL | 年费到期月份 |
| features | JSONB | - | '[]' | 特色功能 |
| points_rate | DECIMAL(4,2) | - | 1.00 | 积分倍率 |
| cashback_rate | DECIMAL(4,2) | - | 0.00 | 返现比例 |
| status | VARCHAR(20) | - | 'active' | 状态 |
| is_primary | BOOLEAN | - | false | 是否主卡 |
| notes | TEXT | - | NULL | 备注 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 更新时间 |

**card_type 枚举值**: `credit`, `debit`  
**card_network 枚举值**: `VISA`, `MasterCard`, `银联`, `American Express`, `JCB`  
**card_level 枚举值**: `普卡`, `金卡`, `白金卡`, `钻石卡`, `无限卡`  
**status 枚举值**: `active`, `frozen`, `closed`

## 3. 年费管理模块

### 3.1 年费减免规则表 (fee_waiver_rules)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 规则ID |
| card_id | UUID | NOT NULL, REFERENCES credit_cards(id) ON DELETE CASCADE | - | 信用卡ID |
| rule_group_id | UUID | - | NULL | 规则组ID(同组规则用AND连接) |
| rule_name | VARCHAR(100) | NOT NULL | - | 规则名称 |
| condition_type | VARCHAR(20) | NOT NULL | - | 条件类型 |
| condition_value | DECIMAL(15,2) | - | NULL | 条件数值 |
| condition_count | INTEGER | - | NULL | 条件次数 |
| condition_period | VARCHAR(20) | - | 'yearly' | 统计周期 |
| logical_operator | VARCHAR(10) | - | NULL | 逻辑操作符 |
| priority | INTEGER | - | 1 | 优先级 |
| is_enabled | BOOLEAN | - | true | 是否启用 |
| effective_from | DATE | - | NULL | 生效日期 |
| effective_to | DATE | - | NULL | 失效日期 |
| description | TEXT | - | NULL | 规则说明 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 更新时间 |

**condition_type 枚举值**: `spending_amount`, `transaction_count`, `points_redeem`, `specific_category`  
**condition_period 枚举值**: `monthly`, `quarterly`, `yearly`  
**logical_operator 枚举值**: `AND`, `OR`, `NULL`

**logical_operator 使用规则**:
- `NULL`: 单个规则时使用，无需逻辑操作符
- `AND`: 多个规则且需要同时满足时使用
- `OR`: 多个规则且满足任一即可时使用

### 3.2 年费记录表 (annual_fee_records)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 记录ID |
| card_id | UUID | NOT NULL, REFERENCES credit_cards(id) ON DELETE CASCADE | - | 信用卡ID |
| fee_year | INTEGER | NOT NULL | - | 年费年份 |
| base_fee | DECIMAL(10,2) | NOT NULL | - | 基础年费 |
| actual_fee | DECIMAL(10,2) | NOT NULL | - | 实际年费 |
| waiver_amount | DECIMAL(10,2) | - | 0 | 减免金额 |
| waiver_rules_applied | JSONB | - | '[]' | 应用的减免规则 |
| rule_evaluation_result | JSONB | - | NULL | 规则评估结果 |
| waiver_reason | VARCHAR(100) | - | NULL | 减免原因 |
| calculation_details | JSONB | - | NULL | 计算详情 |
| status | VARCHAR(20) | - | 'pending' | 状态 |
| due_date | DATE | - | NULL | 应缴日期 |
| paid_date | DATE | - | NULL | 实际缴费日期 |
| payment_method | VARCHAR(20) | - | NULL | 支付方式 |
| notes | TEXT | - | NULL | 备注 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 更新时间 |

**status 枚举值**: `pending`, `paid`, `waived`, `overdue`  
**payment_method 枚举值**: `auto_deduct`, `manual`, `points`, `waived`

## 4. 交易管理模块

### 4.1 交易分类表 (transaction_categories)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 分类ID |
| name | VARCHAR(50) | NOT NULL | - | 分类名称 |
| icon | VARCHAR(50) | - | NULL | 图标 |
| color | VARCHAR(20) | - | NULL | 颜色 |
| parent_id | UUID | REFERENCES transaction_categories(id) | - | 父分类ID |
| is_system | BOOLEAN | - | false | 是否系统分类 |
| is_active | BOOLEAN | - | true | 是否激活 |
| sort_order | INTEGER | - | 0 | 排序 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |

### 4.2 交易记录表 (transactions)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 交易ID |
| user_id | UUID | NOT NULL, REFERENCES users(id) ON DELETE CASCADE | - | 用户ID |
| card_id | UUID | NOT NULL, REFERENCES credit_cards(id) ON DELETE CASCADE | - | 信用卡ID |
| category_id | UUID | REFERENCES transaction_categories(id) | - | 分类ID |
| transaction_type | VARCHAR(20) | NOT NULL | - | 交易类型 |
| amount | DECIMAL(15,2) | NOT NULL | - | 交易金额 |
| currency | VARCHAR(10) | - | 'CNY' | 货币类型 |
| description | VARCHAR(200) | - | NULL | 交易描述 |
| merchant_name | VARCHAR(100) | - | NULL | 商户名称 |
| merchant_category | VARCHAR(50) | - | NULL | 商户类别 |
| location | VARCHAR(200) | - | NULL | 交易地点 |
| points_earned | INTEGER | - | 0 | 获得积分 |
| cashback_earned | DECIMAL(10,2) | - | 0 | 获得返现 |
| status | VARCHAR(20) | - | 'completed' | 状态 |
| transaction_date | TIMESTAMP WITH TIME ZONE | - | NULL | 交易时间 |
| notes | TEXT | - | NULL | 备注 |
| tags | JSONB | - | '[]' | 标签 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 更新时间 |

**transaction_type 枚举值**: `expense`, `income`, `transfer`  
**status 枚举值**: `pending`, `completed`, `failed`, `refunded`

## 5. 还款提醒模块

### 5.1 提醒设置表 (reminder_settings)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 设置ID |
| user_id | UUID | NOT NULL, REFERENCES users(id) ON DELETE CASCADE | - | 用户ID |
| card_id | UUID | REFERENCES credit_cards(id) ON DELETE CASCADE | - | 信用卡ID(NULL表示全局) |
| reminder_type | VARCHAR(30) | NOT NULL | - | 提醒类型 |
| advance_days | INTEGER | - | 3 | 提前天数 |
| reminder_time | TIME | - | '09:00:00' | 提醒时间 |
| email_enabled | BOOLEAN | - | true | 邮件提醒 |
| sms_enabled | BOOLEAN | - | false | 短信提醒 |
| push_enabled | BOOLEAN | - | true | 推送提醒 |
| wechat_enabled | BOOLEAN | - | false | 微信提醒 |
| is_recurring | BOOLEAN | - | true | 是否循环 |
| frequency | VARCHAR(20) | - | 'monthly' | 频率 |
| is_enabled | BOOLEAN | - | true | 是否启用 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 更新时间 |

**reminder_type 枚举值**: `payment_due`, `annual_fee`, `balance_alert`  
**frequency 枚举值**: `daily`, `weekly`, `monthly`

### 5.2 提醒记录表 (reminder_logs)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 记录ID |
| setting_id | UUID | NOT NULL, REFERENCES reminder_settings(id) ON DELETE CASCADE | - | 设置ID |
| user_id | UUID | NOT NULL, REFERENCES users(id) ON DELETE CASCADE | - | 用户ID |
| card_id | UUID | REFERENCES credit_cards(id) ON DELETE SET NULL | - | 信用卡ID |
| reminder_type | VARCHAR(30) | NOT NULL | - | 提醒类型 |
| title | VARCHAR(200) | NOT NULL | - | 提醒标题 |
| content | TEXT | NOT NULL | - | 提醒内容 |
| email_sent | BOOLEAN | - | false | 邮件是否发送 |
| sms_sent | BOOLEAN | - | false | 短信是否发送 |
| push_sent | BOOLEAN | - | false | 推送是否发送 |
| wechat_sent | BOOLEAN | - | false | 微信是否发送 |
| scheduled_at | TIMESTAMP WITH TIME ZONE | - | NULL | 计划发送时间 |
| sent_at | TIMESTAMP WITH TIME ZONE | - | NULL | 实际发送时间 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |

## 6. 统计分析模块

### 6.1 用户统计表 (user_statistics)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 统计ID |
| user_id | UUID | NOT NULL, REFERENCES users(id) ON DELETE CASCADE | - | 用户ID |
| stat_date | DATE | NOT NULL | - | 统计日期 |
| stat_type | VARCHAR(20) | NOT NULL | - | 统计类型 |
| total_transactions | INTEGER | - | 0 | 总交易笔数 |
| total_spending | DECIMAL(15,2) | - | 0 | 总支出 |
| total_income | DECIMAL(15,2) | - | 0 | 总收入 |
| avg_transaction | DECIMAL(15,2) | - | 0 | 平均交易额 |
| active_cards | INTEGER | - | 0 | 活跃卡片数 |
| total_credit_limit | DECIMAL(15,2) | - | 0 | 总信用额度 |
| total_used_limit | DECIMAL(15,2) | - | 0 | 总已用额度 |
| credit_utilization | DECIMAL(5,2) | - | 0 | 信用利用率 |
| category_spending | JSONB | - | '{}' | 分类支出统计 |
| total_points_earned | INTEGER | - | 0 | 总获得积分 |
| total_cashback_earned | DECIMAL(10,2) | - | 0 | 总获得返现 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 更新时间 |

**stat_type 枚举值**: `daily`, `monthly`, `yearly`

**约束**: UNIQUE(user_id, stat_date, stat_type)

## 7. 系统配置模块

### 7.1 系统配置表 (system_configs)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 配置ID |
| config_key | VARCHAR(100) | NOT NULL, UNIQUE | - | 配置键 |
| config_value | TEXT | - | NULL | 配置值 |
| config_type | VARCHAR(20) | - | 'string' | 配置类型 |
| description | TEXT | - | NULL | 配置描述 |
| is_public | BOOLEAN | - | false | 是否公开配置 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 更新时间 |

**config_type 枚举值**: `string`, `integer`, `boolean`, `json`

### 7.2 通知模板表 (notification_templates)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 模板ID |
| template_code | VARCHAR(50) | NOT NULL, UNIQUE | - | 模板代码 |
| template_name | VARCHAR(100) | NOT NULL | - | 模板名称 |
| template_type | VARCHAR(20) | NOT NULL | - | 模板类型 |
| subject | VARCHAR(200) | - | NULL | 主题(邮件) |
| content | TEXT | NOT NULL | - | 内容 |
| variables | JSONB | - | '[]' | 变量列表 |
| is_active | BOOLEAN | - | true | 是否激活 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 更新时间 |

**template_type 枚举值**: `email`, `sms`, `push`, `wechat`

## 8. 智能推荐模块

### 8.1 推荐规则表 (recommendation_rules)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 规则ID |
| rule_name | VARCHAR(100) | NOT NULL | - | 规则名称 |
| rule_type | VARCHAR(30) | NOT NULL | - | 规则类型 |
| conditions | JSONB | NOT NULL | - | 规则条件 |
| recommendation_title | VARCHAR(200) | - | NULL | 推荐标题 |
| recommendation_content | TEXT | - | NULL | 推荐内容 |
| action_type | VARCHAR(30) | - | NULL | 行动类型 |
| priority | INTEGER | - | 1 | 优先级 |
| is_active | BOOLEAN | - | true | 是否激活 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 更新时间 |

**rule_type 枚举值**: `card_usage`, `fee_optimization`, `category_analysis`  
**action_type 枚举值**: `card_switch`, `fee_waiver`, `spending_adjust`

### 8.2 推荐记录表 (recommendation_records)
| 字段名 | 类型 | 约束 | 默认值 | 描述 |
|--------|------|------|--------|------|
| id | UUID | PRIMARY KEY | gen_random_uuid() | 记录ID |
| user_id | UUID | NOT NULL, REFERENCES users(id) ON DELETE CASCADE | - | 用户ID |
| rule_id | UUID | REFERENCES recommendation_rules(id) | - | 规则ID |
| recommendation_type | VARCHAR(30) | NOT NULL | - | 推荐类型 |
| title | VARCHAR(200) | NOT NULL | - | 标题 |
| content | TEXT | NOT NULL | - | 内容 |
| action_data | JSONB | - | NULL | 行动数据 |
| user_action | VARCHAR(20) | - | NULL | 用户行动 |
| feedback | TEXT | - | NULL | 用户反馈 |
| status | VARCHAR(20) | - | 'pending' | 状态 |
| created_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 创建时间 |
| updated_at | TIMESTAMP WITH TIME ZONE | - | NOW() | 更新时间 |

**user_action 枚举值**: `viewed`, `accepted`, `rejected`, `ignored`  
**status 枚举值**: `pending`, `sent`, `read`, `acted`

## 字段统计汇总

| 模块 | 表数量 | 总字段数 |
|------|--------|----------|
| 用户模块 | 4 | 47 |
| 银行和信用卡模块 | 2 | 35 |
| 年费管理模块 | 2 | 33 |
| 交易管理模块 | 2 | 23 |
| 还款提醒模块 | 2 | 28 |
| 统计分析模块 | 1 | 16 |
| 系统配置模块 | 2 | 16 |
| 智能推荐模块 | 2 | 22 |
| **总计** | **17** | **220** |

---
**联系**: LEO (leoyfm@gmail.com) 