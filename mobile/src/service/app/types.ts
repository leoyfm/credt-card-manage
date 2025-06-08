/* eslint-disable */
// @ts-ignore

export type AnnualFeeRecord = {
  /** Card Id 信用卡ID */
  card_id: string;
  /** Fee Year 年费所属年份 */
  fee_year: number;
  /** Due Date 年费到期日期 */
  due_date: string;
  /** Fee Amount 应付年费金额 */
  fee_amount: string;
  /** 减免状态 */
  waiver_status?: WaiverStatus;
  /** Waiver Condition Met 是否满足减免条件 */
  waiver_condition_met?: boolean;
  /** Current Progress 当前进度 */
  current_progress?: string;
  /** Payment Date 实际支付日期 */
  payment_date?: string | null;
  /** Notes 备注 */
  notes?: string | null;
  /** Id */
  id: string;
  /** Created At */
  created_at: string;
  /** Updated At */
  updated_at: string;
};

export type AnnualFeeRecordCreate = {
  /** Card Id 信用卡ID */
  card_id: string;
  /** Fee Year 年费所属年份 */
  fee_year: number;
  /** Due Date 年费到期日期 */
  due_date: string;
  /** Fee Amount 应付年费金额 */
  fee_amount: number | string;
  /** 减免状态 */
  waiver_status?: WaiverStatus;
  /** Waiver Condition Met 是否满足减免条件 */
  waiver_condition_met?: boolean;
  /** Current Progress 当前进度 */
  current_progress?: number | string;
  /** Payment Date 实际支付日期 */
  payment_date?: string | null;
  /** Notes 备注 */
  notes?: string | null;
};

export type AnnualFeeRecordUpdate = {
  waiver_status?: WaiverStatus | null;
  /** Waiver Condition Met */
  waiver_condition_met?: boolean | null;
  /** Current Progress */
  current_progress?: number | string | null;
  /** Payment Date */
  payment_date?: string | null;
  /** Notes */
  notes?: string | null;
};

export type AnnualFeeRule = {
  /** 年费类型，决定减免条件的计算方式 */
  fee_type: FeeType;
  /** Base Fee 基础年费金额，单位：元 */
  base_fee: string;
  /** Waiver Condition Value 减免条件数值，如刷卡次数12或消费金额50000 */
  waiver_condition_value?: string | null;
  /** Points Per Yuan 积分兑换比例：1元对应的积分数，如1元=0.1积分。仅当fee_type为points_exchange时有效 */
  points_per_yuan?: string | null;
  /** Annual Fee Month 年费扣除月份，1-12月。如每年2月扣费则填2 */
  annual_fee_month?: number | null;
  /** Annual Fee Day 年费扣除日期，1-31日。如每年2月18日扣费则填18 */
  annual_fee_day?: number | null;
  /** Description 规则描述，详细说明减免条件 */
  description?: string | null;
  /** Id 规则ID，系统自动生成的唯一标识 */
  id: string;
  /** Created At 创建时间 */
  created_at: string;
};

export type AnnualFeeRuleCreate = {
  /** 年费类型，决定减免条件的计算方式 */
  fee_type: FeeType;
  /** Base Fee 基础年费金额，单位：元 */
  base_fee: number | string;
  /** Waiver Condition Value 减免条件数值，如刷卡次数12或消费金额50000 */
  waiver_condition_value?: number | string | null;
  /** Points Per Yuan 积分兑换比例：1元对应的积分数，如1元=0.1积分。仅当fee_type为points_exchange时有效 */
  points_per_yuan?: number | string | null;
  /** Annual Fee Month 年费扣除月份，1-12月。如每年2月扣费则填2 */
  annual_fee_month?: number | null;
  /** Annual Fee Day 年费扣除日期，1-31日。如每年2月18日扣费则填18 */
  annual_fee_day?: number | null;
  /** Description 规则描述，详细说明减免条件 */
  description?: string | null;
};

export type AnnualFeeRuleUpdate = {
  /** 年费类型 */
  fee_type?: FeeType | null;
  /** Base Fee 基础年费金额 */
  base_fee?: number | string | null;
  /** Waiver Condition Value 减免条件数值 */
  waiver_condition_value?: number | string | null;
  /** Points Per Yuan 积分兑换比例 */
  points_per_yuan?: number | string | null;
  /** Annual Fee Month 年费扣除月份 */
  annual_fee_month?: number | null;
  /** Annual Fee Day 年费扣除日期 */
  annual_fee_day?: number | null;
  /** Description 规则描述 */
  description?: string | null;
};

export type AnnualFeeStatistics = {
  /** Total Cards 信用卡总数 */
  total_cards: number;
  /** Total Annual Fees 年费总金额 */
  total_annual_fees: string;
  /** Waived Fees 已减免年费金额 */
  waived_fees: string;
  /** Paid Fees 已支付年费金额 */
  paid_fees: string;
  /** Pending Fees 待处理年费金额 */
  pending_fees: string;
  /** Overdue Fees 逾期年费金额 */
  overdue_fees: string;
  /** Waiver Rate 年费减免率，百分比形式 */
  waiver_rate: number;
};

export type AnnualFeeWaiverCheck = {
  /** Card Id 信用卡ID */
  card_id: string;
  /** Fee Year 年费年份 */
  fee_year: number;
  /** Waiver Eligible 是否符合减免条件 */
  waiver_eligible: boolean;
  /** Current Progress 当前进度，如已刷卡次数或金额 */
  current_progress: string;
  /** Required Progress 要求进度，减免所需的目标值 */
  required_progress?: string | null;
  /** Progress Description 进度描述，易于理解的文字说明 */
  progress_description: string;
  /** Days Remaining 距离年费到期的剩余天数 */
  days_remaining: number;
};

export type ApiPagedResponseAnnualFeeRecord_ = {
  /** Success 请求是否成功 */
  success: boolean;
  /** Code HTTP状态码 */
  code: number;
  /** Message 响应消息 */
  message: string;
  /** 分页响应数据，包含items数组和pagination信息 */
  data?: PagedResponseAnnualFeeRecord_ | null;
  /** Timestamp 响应时间戳 */
  timestamp?: string;
};

export type ApiPagedResponseAnnualFeeRule_ = {
  /** Success 请求是否成功 */
  success: boolean;
  /** Code HTTP状态码 */
  code: number;
  /** Message 响应消息 */
  message: string;
  /** 分页响应数据，包含items数组和pagination信息 */
  data?: PagedResponseAnnualFeeRule_ | null;
  /** Timestamp 响应时间戳 */
  timestamp?: string;
};

export type ApiPagedResponseCard_ = {
  /** Success 请求是否成功 */
  success: boolean;
  /** Code HTTP状态码 */
  code: number;
  /** Message 响应消息 */
  message: string;
  /** 分页响应数据，包含items数组和pagination信息 */
  data?: PagedResponseCard_ | null;
  /** Timestamp 响应时间戳 */
  timestamp?: string;
};

export type ApiPagedResponseCardSummaryWithAnnualFee_ = {
  /** Success 请求是否成功 */
  success: boolean;
  /** Code HTTP状态码 */
  code: number;
  /** Message 响应消息 */
  message: string;
  /** 分页响应数据，包含items数组和pagination信息 */
  data?: PagedResponseCardSummaryWithAnnualFee_ | null;
  /** Timestamp 响应时间戳 */
  timestamp?: string;
};

export type ApiPagedResponseRecommendation_ = {
  /** Success 请求是否成功 */
  success: boolean;
  /** Code HTTP状态码 */
  code: number;
  /** Message 响应消息 */
  message: string;
  /** 分页响应数据，包含items数组和pagination信息 */
  data?: PagedResponseRecommendation_ | null;
  /** Timestamp 响应时间戳 */
  timestamp?: string;
};

export type ApiPagedResponseReminder_ = {
  /** Success 请求是否成功 */
  success: boolean;
  /** Code HTTP状态码 */
  code: number;
  /** Message 响应消息 */
  message: string;
  /** 分页响应数据，包含items数组和pagination信息 */
  data?: PagedResponseReminder_ | null;
  /** Timestamp 响应时间戳 */
  timestamp?: string;
};

export type ApiResponseAnnualFeeRecord_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: AnnualFeeRecord | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseAnnualFeeRule_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: AnnualFeeRule | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseAnnualFeeStatistics_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: AnnualFeeStatistics | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseAnnualFeeWaiverCheck_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: AnnualFeeWaiverCheck | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseCard_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: Card | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseCardWithAnnualFee_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: CardWithAnnualFee | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseDict_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** Data 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: Record<string, unknown> | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseDictStr_Any_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** Data 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: Record<string, unknown> | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseDictStr_bool_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** Data 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: Record<string, unknown> | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseDictStr_str_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** Data 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: Record<string, unknown> | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseListAnnualFeeWaiverCheck_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** Data 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: AnnualFeeWaiverCheck[] | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseListRecommendation_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** Data 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: Recommendation[] | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseLoginResponse_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: LoginResponse | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseNoneType_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** Data 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseRecommendation_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: Recommendation | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseReminder_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: Reminder | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseStr_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** Data 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: string | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type ApiResponseUserProfile_ = {
  /** Success 请求是否成功，true表示成功，false表示失败 */
  success: boolean;
  /** Code HTTP状态码，如200、404、500等 */
  code: number;
  /** Message 响应消息，用于描述操作结果 */
  message: string;
  /** 响应数据，根据接口不同而变化，可能为null、对象或数组 */
  data?: UserProfile | null;
  /** Timestamp 响应时间戳，ISO 8601格式 */
  timestamp?: string;
};

export type batchCheckAnnualFeeWaiversApiAnnualFeesBatchCheckWaiversPostParams =
  {
    fee_year: number;
  };

export type batchCreateAnnualFeeRecordsApiAnnualFeesBatchCreateRecordsPostParams =
  {
    fee_year: number;
  };

export type Card = {
  /** Bank Name 银行名称，如：招商银行、中国工商银行 */
  bank_name: string;
  /** Card Name 信用卡名称，如：招行经典白金卡、工行环球旅行卡 */
  card_name: string;
  /** Card Number 信用卡号，支持13-19位数字 */
  card_number: string;
  /** 信用卡组织类型 */
  card_type: CardType;
  /** Credit Limit 信用额度，单位：元 */
  credit_limit: string;
  /** Used Amount 已使用额度，单位：元 */
  used_amount?: string;
  /** Available Amount 可用额度，自动计算得出 */
  available_amount?: string | null;
  /** Billing Day 账单日，每月的哪一天生成账单 */
  billing_day: number;
  /** Due Day 还款日，每月的还款截止日期 */
  due_day: number;
  /** Expiry Month 卡片有效期月份，1-12 */
  expiry_month: number;
  /** Expiry Year 卡片有效期年份，如2024 */
  expiry_year: number;
  /** Annual Fee Rule Id 年费规则ID，关联年费规则表 */
  annual_fee_rule_id?: string | null;
  /** Card Color 卡片颜色，用于前端显示 */
  card_color?: string;
  /** 卡片状态 */
  status?: CardStatus;
  /** Is Active 是否启用此卡片 */
  is_active?: boolean;
  /** Activation Date 激活日期 */
  activation_date?: string | null;
  /** Notes 备注信息 */
  notes?: string | null;
  /** Id 信用卡ID，系统自动生成的唯一标识 */
  id: string;
  /** User Id 用户ID，卡片所属用户 */
  user_id: string;
  /** Created At 创建时间 */
  created_at: string;
  /** Updated At 最后更新时间 */
  updated_at: string;
};

export type CardCreate = {
  /** Bank Name 银行名称，如：招商银行、中国工商银行 */
  bank_name: string;
  /** Card Name 信用卡名称，如：招行经典白金卡、工行环球旅行卡 */
  card_name: string;
  /** Card Number 信用卡号，支持13-19位数字 */
  card_number: string;
  /** 信用卡组织类型 */
  card_type: CardType;
  /** Credit Limit 信用额度，单位：元 */
  credit_limit: number | string;
  /** Used Amount 已使用额度，单位：元 */
  used_amount?: number | string;
  /** Available Amount 可用额度，自动计算得出 */
  available_amount?: number | string | null;
  /** Billing Day 账单日，每月的哪一天生成账单 */
  billing_day: number;
  /** Due Day 还款日，每月的还款截止日期 */
  due_day: number;
  /** Expiry Month 卡片有效期月份，1-12 */
  expiry_month: number;
  /** Expiry Year 卡片有效期年份，如2024 */
  expiry_year: number;
  /** Annual Fee Rule Id 年费规则ID，关联年费规则表 */
  annual_fee_rule_id?: string | null;
  /** Card Color 卡片颜色，用于前端显示 */
  card_color?: string;
  /** 卡片状态 */
  status?: CardStatus;
  /** Is Active 是否启用此卡片 */
  is_active?: boolean;
  /** Activation Date 激活日期 */
  activation_date?: string | null;
  /** Notes 备注信息 */
  notes?: string | null;
};

export enum CardStatus {
  active = 'active',
  inactive = 'inactive',
  frozen = 'frozen',
  cancelled = 'cancelled',
}

export type ICardStatus = keyof typeof CardStatus;

export type CardSummaryWithAnnualFee = {
  /** Id 信用卡ID */
  id: string;
  /** Bank Name 银行名称 */
  bank_name: string;
  /** Card Name 信用卡名称 */
  card_name: string;
  /** 信用卡组织类型 */
  card_type: CardType;
  /** Credit Limit 信用额度 */
  credit_limit: string;
  /** Used Amount 已使用额度 */
  used_amount: string;
  /** Available Amount 可用额度 */
  available_amount: string;
  /** 卡片状态 */
  status: CardStatus;
  /** Card Color 卡片颜色 */
  card_color: string;
  /** Has Annual Fee 是否设置了年费规则 */
  has_annual_fee: boolean;
  /** Annual Fee Amount 年费金额 */
  annual_fee_amount?: string | null;
  /** Fee Type Display 年费类型显示名称 */
  fee_type_display?: string | null;
  /** Current Year Fee Status 当前年费状态 */
  current_year_fee_status?: string | null;
};

export enum CardType {
  visa = 'visa',
  mastercard = 'mastercard',
  unionpay = 'unionpay',
  amex = 'amex',
  jcb = 'jcb',
  discover = 'discover',
  diners = 'diners',
}

export type ICardType = keyof typeof CardType;

export type CardWithAnnualFee = {
  /** Bank Name 银行名称，如：招商银行、中国工商银行 */
  bank_name: string;
  /** Card Name 信用卡名称，如：招行经典白金卡、工行环球旅行卡 */
  card_name: string;
  /** Card Number 信用卡号，支持13-19位数字 */
  card_number: string;
  /** 信用卡组织类型 */
  card_type: CardType;
  /** Credit Limit 信用额度，单位：元 */
  credit_limit: string;
  /** Used Amount 已使用额度，单位：元 */
  used_amount?: string;
  /** Available Amount 可用额度，自动计算得出 */
  available_amount?: string | null;
  /** Billing Day 账单日，每月的哪一天生成账单 */
  billing_day: number;
  /** Due Day 还款日，每月的还款截止日期 */
  due_day: number;
  /** Expiry Month 卡片有效期月份，1-12 */
  expiry_month: number;
  /** Expiry Year 卡片有效期年份，如2024 */
  expiry_year: number;
  /** Annual Fee Rule Id 年费规则ID，关联年费规则表 */
  annual_fee_rule_id?: string | null;
  /** Card Color 卡片颜色，用于前端显示 */
  card_color?: string;
  /** 卡片状态 */
  status?: CardStatus;
  /** Is Active 是否启用此卡片 */
  is_active?: boolean;
  /** Activation Date 激活日期 */
  activation_date?: string | null;
  /** Notes 备注信息 */
  notes?: string | null;
  /** Id 信用卡ID，系统自动生成的唯一标识 */
  id: string;
  /** User Id 用户ID，卡片所属用户 */
  user_id: string;
  /** Created At 创建时间 */
  created_at: string;
  /** Updated At 最后更新时间 */
  updated_at: string;
  /** 年费规则信息，如果卡片设置了年费规则则包含完整信息 */
  annual_fee_rule?: AnnualFeeRule | null;
  /** Has Annual Fee 是否设置了年费规则 */
  has_annual_fee: boolean;
  /** Current Year Fee Status 当前年份年费状态：pending/waived/paid/overdue */
  current_year_fee_status?: string | null;
  /** Next Fee Due Date 下一次年费到期日期 */
  next_fee_due_date?: string | null;
};

export type CardWithAnnualFeeCreate = {
  /** Bank Name 银行名称，如：招商银行、中国工商银行 */
  bank_name: string;
  /** Card Name 信用卡名称，如：招行经典白金卡、工行环球旅行卡 */
  card_name: string;
  /** Card Number 信用卡号，支持13-19位数字 */
  card_number: string;
  /** 信用卡组织类型 */
  card_type: CardType;
  /** Credit Limit 信用额度，单位：元 */
  credit_limit: number | string;
  /** Used Amount 已使用额度，单位：元 */
  used_amount?: number | string;
  /** Available Amount 可用额度，自动计算得出 */
  available_amount?: number | string | null;
  /** Billing Day 账单日，每月的哪一天生成账单 */
  billing_day: number;
  /** Due Day 还款日，每月的还款截止日期 */
  due_day: number;
  /** Expiry Month 卡片有效期月份，1-12 */
  expiry_month: number;
  /** Expiry Year 卡片有效期年份，如2024 */
  expiry_year: number;
  /** Annual Fee Rule Id 年费规则ID，关联年费规则表 */
  annual_fee_rule_id?: string | null;
  /** Card Color 卡片颜色，用于前端显示 */
  card_color?: string;
  /** 卡片状态 */
  status?: CardStatus;
  /** Is Active 是否启用此卡片 */
  is_active?: boolean;
  /** Activation Date 激活日期 */
  activation_date?: string | null;
  /** Notes 备注信息 */
  notes?: string | null;
  /** Annual Fee Enabled 是否启用年费管理 */
  annual_fee_enabled?: boolean;
  /** 年费类型，启用年费管理时必填 */
  fee_type?: FeeType | null;
  /** Base Fee 基础年费金额，启用年费管理时必填 */
  base_fee?: number | string | null;
  /** Waiver Condition Value 减免条件数值，如刷卡次数12或消费金额50000 */
  waiver_condition_value?: number | string | null;
  /** Points Per Yuan 积分兑换比例：1元对应的积分数，如1元=0.1积分。仅当fee_type为points_exchange时有效 */
  points_per_yuan?: number | string | null;
  /** Annual Fee Month 年费扣除月份，1-12月。如每年2月扣费则填2 */
  annual_fee_month?: number | null;
  /** Annual Fee Day 年费扣除日期，1-31日。如每年2月18日扣费则填18 */
  annual_fee_day?: number | null;
  /** Fee Description 年费规则描述，详细说明减免条件 */
  fee_description?: string | null;
};

export type CardWithAnnualFeeUpdate = {
  /** Bank Name 银行名称 */
  bank_name?: string | null;
  /** Card Name 信用卡名称 */
  card_name?: string | null;
  /** 信用卡组织类型 */
  card_type?: CardType | null;
  /** Credit Limit 信用额度 */
  credit_limit?: number | string | null;
  /** Used Amount 已使用额度 */
  used_amount?: number | string | null;
  /** Billing Day 账单日 */
  billing_day?: number | null;
  /** Due Day 还款日 */
  due_day?: number | null;
  /** Expiry Month 卡片有效期月份 */
  expiry_month?: number | null;
  /** Expiry Year 卡片有效期年份 */
  expiry_year?: number | null;
  /** Annual Fee Rule Id 年费规则ID */
  annual_fee_rule_id?: string | null;
  /** Card Color 卡片颜色 */
  card_color?: string | null;
  /** 卡片状态 */
  status?: CardStatus | null;
  /** Is Active 是否启用此卡片 */
  is_active?: boolean | null;
  /** Activation Date 激活日期 */
  activation_date?: string | null;
  /** Notes 备注信息 */
  notes?: string | null;
  /** Annual Fee Enabled 是否启用年费管理。设为False将删除现有年费规则 */
  annual_fee_enabled?: boolean | null;
  /** 年费类型 */
  fee_type?: FeeType | null;
  /** Base Fee 基础年费金额 */
  base_fee?: number | string | null;
  /** Waiver Condition Value 减免条件数值 */
  waiver_condition_value?: number | string | null;
  /** Points Per Yuan 积分兑换比例 */
  points_per_yuan?: number | string | null;
  /** Annual Fee Month 年费扣除月份 */
  annual_fee_month?: number | null;
  /** Annual Fee Day 年费扣除日期 */
  annual_fee_day?: number | null;
  /** Fee Description 年费规则描述 */
  fee_description?: string | null;
};

export type ChangePasswordRequest = {
  /** Old Password 当前密码 */
  old_password: string;
  /** New Password 新密码，8-30位字符 */
  new_password: string;
};

export type checkAllAnnualFeeWaiversApiAnnualFeesWaiverCheckUserUserIdGetParams =
  {
    user_id: string;
    /** 年份，默认为当前年份 */
    year?: number | null;
  };

export type checkAnnualFeeWaiverApiAnnualFeesWaiverCheckCardIdFeeYearGetParams =
  {
    card_id: string;
    fee_year: number;
  };

export enum CodeType {
  login = 'login',
  register = 'register',
  reset_password = 'reset_password',
  bind_phone = 'bind_phone',
}

export type ICodeType = keyof typeof CodeType;

export type createAnnualFeeRecordAutoApiAnnualFeesRecordsAutoPostParams = {
  card_id: string;
  fee_year: number;
};

export type deleteAnnualFeeRuleApiAnnualFeesRulesRuleIdDeleteParams = {
  rule_id: string;
};

export type deleteCardApiCardsCardIdDeleteParams = {
  card_id: string;
};

export type deleteReminderApiRemindersReminderIdDeleteParams = {
  reminder_id: string;
};

export enum FeeType {
  rigid = 'rigid',
  transaction_count = 'transaction_count',
  points_exchange = 'points_exchange',
  transaction_amount = 'transaction_amount',
}

export type IFeeType = keyof typeof FeeType;

export enum Gender {
  male = 'male',
  female = 'female',
  unknown = 'unknown',
}

export type IGender = keyof typeof Gender;

export type generateRecommendationsApiRecommendationsGeneratePostParams = {
  user_id: string;
};

export type getAnnualFeeRecordApiAnnualFeesRecordsRecordIdGetParams = {
  record_id: string;
};

export type getAnnualFeeRecordsApiAnnualFeesRecordsGetParams = {
  /** 页码，从1开始 */
  page?: number;
  /** 每页数量，最大100 */
  page_size?: number;
  /** 模糊搜索关键词，支持卡片名称、银行名称搜索 */
  keyword?: string;
  /** 信用卡ID过滤 */
  card_id?: string | null;
  /** 年费年份过滤 */
  fee_year?: number | null;
  /** 减免状态过滤 */
  waiver_status?: WaiverStatus | null;
};

export type getAnnualFeeRuleApiAnnualFeesRulesRuleIdGetParams = {
  rule_id: string;
};

export type getAnnualFeeRulesApiAnnualFeesRulesGetParams = {
  /** 页码，从1开始 */
  page?: number;
  /** 每页数量，最大100 */
  page_size?: number;
  /** 模糊搜索关键词，支持规则名称、描述搜索 */
  keyword?: string;
  /** 按年费类型筛选 */
  fee_type?: FeeType | null;
};

export type getAnnualFeeStatisticsApiAnnualFeesStatisticsUserIdGetParams = {
  user_id: string;
  /** 年份，默认为当前年份 */
  year?: number | null;
};

export type getCardApiCardsCardIdGetParams = {
  card_id: string;
};

export type getCardsApiCardsGetParams = {
  /** 页码，从1开始 */
  page?: number;
  /** 每页数量，最大100 */
  page_size?: number;
  /** 模糊搜索关键词，支持银行名称、卡片名称搜索 */
  keyword?: string;
};

export type getCardsBasicApiCardsBasicGetParams = {
  /** 页码，从1开始 */
  page?: number;
  /** 每页数量，最大100 */
  page_size?: number;
  /** 模糊搜索关键词，支持银行名称、卡片名称搜索 */
  keyword?: string;
};

export type getRecommendationApiRecommendationsRecommendationIdGetParams = {
  recommendation_id: string;
};

export type getRecommendationsApiRecommendationsGetParams = {
  /** 页码，从1开始 */
  page?: number;
  /** 每页数量，最大100 */
  page_size?: number;
  /** 模糊搜索关键词，支持银行名称、卡片类型搜索 */
  keyword?: string;
};

export type getReminderApiRemindersReminderIdGetParams = {
  reminder_id: string;
};

export type getRemindersApiRemindersGetParams = {
  /** 页码，从1开始 */
  page?: number;
  /** 每页数量，最大100 */
  page_size?: number;
  /** 模糊搜索关键词，支持卡片名称、银行名称搜索 */
  keyword?: string;
};

export type HTTPValidationError = {
  /** Detail */
  detail?: ValidationError[];
};

export type LoginResponse = {
  /** Access Token JWT访问令牌，用于API认证 */
  access_token: string;
  /** Token Type 令牌类型，固定为bearer */
  token_type?: string;
  /** Expires In 令牌过期时间（秒） */
  expires_in: number;
  /** 用户详细信息 */
  user: UserProfile;
};

export type LogoutRequest = {
  /** All Devices 是否登出所有设备 */
  all_devices?: boolean;
};

export type markReminderReadApiRemindersReminderIdMarkReadPutParams = {
  reminder_id: string;
};

export type PagedResponseAnnualFeeRecord_ = {
  /** Items 当前页的数据列表 */
  items: AnnualFeeRecord[];
  /** 分页信息 */
  pagination: PaginationInfo;
};

export type PagedResponseAnnualFeeRule_ = {
  /** Items 当前页的数据列表 */
  items: AnnualFeeRule[];
  /** 分页信息 */
  pagination: PaginationInfo;
};

export type PagedResponseCard_ = {
  /** Items 当前页的数据列表 */
  items: Card[];
  /** 分页信息 */
  pagination: PaginationInfo;
};

export type PagedResponseCardSummaryWithAnnualFee_ = {
  /** Items 当前页的数据列表 */
  items: CardSummaryWithAnnualFee[];
  /** 分页信息 */
  pagination: PaginationInfo;
};

export type PagedResponseRecommendation_ = {
  /** Items 当前页的数据列表 */
  items: Recommendation[];
  /** 分页信息 */
  pagination: PaginationInfo;
};

export type PagedResponseReminder_ = {
  /** Items 当前页的数据列表 */
  items: Reminder[];
  /** 分页信息 */
  pagination: PaginationInfo;
};

export type PaginationInfo = {
  /** Total 总记录数 */
  total: number;
  /** Page 当前页码，从1开始 */
  page: number;
  /** Size 每页大小，即当前页实际返回的记录数 */
  size: number;
  /** Pages 总页数，根据总记录数和每页大小计算得出 */
  pages: number;
};

export type PhoneCodeLogin = {
  /** Phone 手机号码 */
  phone: string;
  /** Verification Code 6位数字验证码 */
  verification_code: string;
};

export type PhonePasswordLogin = {
  /** Phone 手机号码 */
  phone: string;
  /** Password 用户密码 */
  password: string;
  /** Remember Me 是否记住登录状态 */
  remember_me?: boolean;
};

export type Recommendation = {
  /** Bank Name 银行名称 */
  bank_name: string;
  /** Card Name 信用卡名称 */
  card_name: string;
  /** 推荐类型 */
  recommendation_type: RecommendationType;
  /** Title 推荐标题 */
  title: string;
  /** Description 推荐描述 */
  description: string;
  /** Features 卡片特色功能列表 */
  features?: string[];
  /** Annual Fee 年费金额，单位：元 */
  annual_fee?: string;
  /** Credit Limit Range 额度范围 */
  credit_limit_range: string;
  /** Approval Difficulty 申请难度等级，1-5分 */
  approval_difficulty: number;
  /** Recommendation Score 推荐分数，0-100分 */
  recommendation_score: string;
  /** Match Reasons 匹配原因列表 */
  match_reasons?: string[];
  /** Pros 优点列表 */
  pros?: string[];
  /** Cons 缺点列表 */
  cons?: string[];
  /** Apply Url 申请链接 */
  apply_url?: string | null;
  /** 推荐状态 */
  status?: RecommendationStatus;
  /** Expires At 推荐过期时间 */
  expires_at?: string | null;
  /** Is Featured 是否为精选推荐 */
  is_featured?: boolean;
  /** Id 推荐ID，系统自动生成的唯一标识 */
  id: string;
  /** User Id 用户ID，推荐的目标用户 */
  user_id: string;
  /** Created At 创建时间 */
  created_at: string;
  /** Updated At 最后更新时间 */
  updated_at: string;
  /** View Count 查看次数 */
  view_count?: number;
  /** Last Viewed At 最后查看时间 */
  last_viewed_at?: string | null;
};

export enum RecommendationStatus {
  active = 'active',
  expired = 'expired',
  applied = 'applied',
  rejected = 'rejected',
}

export type IRecommendationStatus = keyof typeof RecommendationStatus;

export enum RecommendationType {
  cashback = 'cashback',
  points = 'points',
  travel = 'travel',
  dining = 'dining',
  shopping = 'shopping',
  fuel = 'fuel',
}

export type IRecommendationType = keyof typeof RecommendationType;

export type RefreshTokenRequest = {
  /** Refresh Token 刷新令牌 */
  refresh_token: string;
};

export type Reminder = {
  /** Card Id 信用卡ID，关联的信用卡 */
  card_id: string;
  /** 提醒类型 */
  reminder_type: ReminderType;
  /** Title 提醒标题 */
  title: string;
  /** Message 提醒内容 */
  message: string;
  /** Reminder Date 提醒日期 */
  reminder_date: string;
  /** Due Date 到期日期（还款日或账单日） */
  due_date: string;
  /** Amount 相关金额，如还款金额、年费金额 */
  amount?: string | null;
  /** 提醒状态 */
  status?: ReminderStatus;
  /** Is Active 是否启用此提醒 */
  is_active?: boolean;
  /** Notes 备注信息 */
  notes?: string | null;
  /** Id 提醒ID，系统自动生成的唯一标识 */
  id: string;
  /** User Id 用户ID，提醒所属用户 */
  user_id: string;
  /** Created At 创建时间 */
  created_at: string;
  /** Updated At 最后更新时间 */
  updated_at: string;
  /** Sent At 发送时间 */
  sent_at?: string | null;
  /** Read At 已读时间 */
  read_at?: string | null;
};

export type ReminderCreate = {
  /** Card Id 信用卡ID，关联的信用卡 */
  card_id: string;
  /** 提醒类型 */
  reminder_type: ReminderType;
  /** Title 提醒标题 */
  title: string;
  /** Message 提醒内容 */
  message: string;
  /** Reminder Date 提醒日期 */
  reminder_date: string;
  /** Due Date 到期日期（还款日或账单日） */
  due_date: string;
  /** Amount 相关金额，如还款金额、年费金额 */
  amount?: number | string | null;
  /** 提醒状态 */
  status?: ReminderStatus;
  /** Is Active 是否启用此提醒 */
  is_active?: boolean;
  /** Notes 备注信息 */
  notes?: string | null;
};

export enum ReminderStatus {
  pending = 'pending',
  sent = 'sent',
  read = 'read',
  ignored = 'ignored',
}

export type IReminderStatus = keyof typeof ReminderStatus;

export enum ReminderType {
  payment = 'payment',
  bill = 'bill',
  annual_fee = 'annual_fee',
  overdue = 'overdue',
}

export type IReminderType = keyof typeof ReminderType;

export type ReminderUpdate = {
  /** Title 提醒标题 */
  title?: string | null;
  /** Message 提醒内容 */
  message?: string | null;
  /** Reminder Date 提醒日期 */
  reminder_date?: string | null;
  /** Due Date 到期日期 */
  due_date?: string | null;
  /** Amount 相关金额 */
  amount?: number | string | null;
  /** 提醒状态 */
  status?: ReminderStatus | null;
  /** Is Active 是否启用此提醒 */
  is_active?: boolean | null;
  /** Notes 备注信息 */
  notes?: string | null;
};

export type ResetPasswordRequest = {
  /** Phone Or Email 手机号或邮箱地址 */
  phone_or_email: string;
  /** Verification Code 6位数字验证码 */
  verification_code: string;
  /** New Password 新密码，8-30位字符 */
  new_password: string;
};

export type SendCodeRequest = {
  /** Phone Or Email 手机号或邮箱地址 */
  phone_or_email: string;
  /** 验证码类型 */
  code_type: CodeType;
};

export type submitRecommendationFeedbackApiRecommendationsRecommendationIdFeedbackPutParams =
  {
    recommendation_id: string;
    /** 用户反馈，如：interested、not_interested、applied */
    feedback: string;
  };

export type updateAnnualFeeRecordApiAnnualFeesRecordsRecordIdPutParams = {
  record_id: string;
};

export type updateAnnualFeeRuleApiAnnualFeesRulesRuleIdPutParams = {
  rule_id: string;
};

export type updateCardApiCardsCardIdPutParams = {
  card_id: string;
};

export type updateReminderApiRemindersReminderIdPutParams = {
  reminder_id: string;
};

export type UsernamePasswordLogin = {
  /** Username 用户名或邮箱地址 */
  username: string;
  /** Password 用户密码 */
  password: string;
  /** Remember Me 是否记住登录状态，影响令牌过期时间 */
  remember_me?: boolean;
};

export type UserProfile = {
  /** Id 用户唯一标识符 */
  id: string;
  /** Username 用户名 */
  username: string;
  /** Email 邮箱地址 */
  email: string;
  /** Phone 手机号码 */
  phone?: string | null;
  /** Nickname 用户昵称 */
  nickname?: string | null;
  /** Avatar Url 头像URL */
  avatar_url?: string | null;
  /** 性别 */
  gender?: Gender;
  /** Birthday 生日 */
  birthday?: string | null;
  /** Bio 个人简介 */
  bio?: string | null;
  /** Is Active 账户是否激活 */
  is_active?: boolean;
  /** Is Verified 是否已验证邮箱或手机号 */
  is_verified?: boolean;
  /** Is Admin 是否为管理员 */
  is_admin?: boolean;
  /** Login Count 登录次数 */
  login_count?: string;
  /** Last Login At 最后登录时间 */
  last_login_at?: string | null;
  /** Created At 注册时间 */
  created_at: string;
  /** Updated At 最后更新时间 */
  updated_at: string;
};

export type UserRegisterRequest = {
  /** Username 用户名，3-20位字符，支持字母、数字、下划线 */
  username: string;
  /** Email 邮箱地址，必须是有效的邮箱格式 */
  email: string;
  /** Password 密码，8-30位字符，建议包含字母、数字和特殊字符 */
  password: string;
  /** Phone 手机号码，可选，中国大陆手机号格式 */
  phone?: string | null;
  /** Nickname 昵称，可选，默认使用用户名 */
  nickname?: string | null;
  /** Verification Code 手机验证码，提供手机号时必填 */
  verification_code?: string | null;
};

export type UserUpdateRequest = {
  /** Nickname 用户昵称 */
  nickname?: string | null;
  /** Avatar Url 头像URL */
  avatar_url?: string | null;
  /** 性别 */
  gender?: Gender | null;
  /** Birthday 生日 */
  birthday?: string | null;
  /** Bio 个人简介 */
  bio?: string | null;
};

export type ValidationError = {
  /** Location */
  loc: (string | number)[];
  /** Message */
  msg: string;
  /** Error Type */
  type: string;
};

export type VerifyCodeRequest = {
  /** Phone Or Email 手机号或邮箱地址 */
  phone_or_email: string;
  /** Code 6位数字验证码 */
  code: string;
  /** 验证码类型 */
  code_type: CodeType;
};

export enum WaiverStatus {
  pending = 'pending',
  waived = 'waived',
  paid = 'paid',
  overdue = 'overdue',
}

export type IWaiverStatus = keyof typeof WaiverStatus;

export type WechatLoginRequest = {
  /** Code 微信授权码，由微信客户端获取 */
  code: string;
  /** User Info 可选的用户补充信息，如昵称等 */
  user_info?: Record<string, unknown> | null;
};
