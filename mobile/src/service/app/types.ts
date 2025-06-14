/* eslint-disable */
// @ts-ignore

export type AccountDeletionRequest = {
  /** Password 确认密码 */
  password: string;
  /** Reason 注销原因 */
  reason?: string | null;
};

export type ApiPagedResponse = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** Data 响应数据列表 */
  data?: unknown[];
  /** 分页信息 */
  pagination: PaginationInfo;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiPagedResponseLoginLogResponse_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** Data 响应数据列表 */
  data?: LoginLogResponse[];
  /** 分页信息 */
  pagination: PaginationInfo;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiPagedResponseReminderRecordResponse_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** Data 响应数据列表 */
  data?: ReminderRecordResponse[];
  /** 分页信息 */
  pagination: PaginationInfo;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiPagedResponseReminderSettingResponse_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** Data 响应数据列表 */
  data?: ReminderSettingResponse[];
  /** 分页信息 */
  pagination: PaginationInfo;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiResponse = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** Data 响应数据 */
  data?: unknown | null;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiResponseBool_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** Data 响应数据 */
  data?: boolean | null;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiResponseDict_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** Data 响应数据 */
  data?: Record<string, unknown> | null;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiResponseListReminderRecordResponse_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** Data 响应数据 */
  data?: ReminderRecordResponse[] | null;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiResponseListWechatBindingResponse_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** Data 响应数据 */
  data?: WechatBindingResponse[] | null;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiResponseMarkAllReadResponse_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** 响应数据 */
  data?: MarkAllReadResponse | null;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiResponseReminderRecordResponse_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** 响应数据 */
  data?: ReminderRecordResponse | null;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiResponseReminderSettingResponse_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** 响应数据 */
  data?: ReminderSettingResponse | null;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiResponseReminderStatisticsResponse_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** 响应数据 */
  data?: ReminderStatisticsResponse | null;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiResponseUnreadRemindersCountResponse_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** 响应数据 */
  data?: UnreadRemindersCountResponse | null;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiResponseUpcomingRemindersResponse_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** 响应数据 */
  data?: UpcomingRemindersResponse | null;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiResponseUserProfileResponse_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** 响应数据 */
  data?: UserProfileResponse | null;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type ApiResponseUserStatisticsResponse_ = {
  /** Success 操作是否成功 */
  success?: boolean;
  /** Code 响应状态码 */
  code?: number;
  /** Message 响应消息 */
  message?: string;
  /** 响应数据 */
  data?: UserStatisticsResponse | null;
  /** Timestamp 响应时间戳 */
  timestamp: string;
};

export type AuthResponse = {
  /** User Id 用户ID */
  user_id: string;
  /** Username 用户名 */
  username: string;
  /** Email 邮箱 */
  email: string;
  /** Nickname 昵称 */
  nickname?: string | null;
  /** Phone 手机号 */
  phone?: string | null;
  /** Avatar Url 头像URL */
  avatar_url?: string | null;
  /** Is Active 是否激活 */
  is_active?: boolean;
  /** Is Verified 是否已验证 */
  is_verified?: boolean;
  /** Is Admin 是否管理员 */
  is_admin?: boolean;
  /** Timezone 时区 */
  timezone?: string | null;
  /** Language 语言偏好 */
  language?: string | null;
  /** Currency 默认货币 */
  currency?: string | null;
  /** Last Login At 最后登录时间 */
  last_login_at?: string | null;
  /** Email Verified At 邮箱验证时间 */
  email_verified_at?: string | null;
  /** Created At 创建时间 */
  created_at?: string | null;
  /** Updated At 更新时间 */
  updated_at?: string | null;
  /** Access Token 访问令牌 */
  access_token: string;
  /** Refresh Token 刷新令牌 */
  refresh_token: string;
  /** Token Type 令牌类型 */
  token_type?: string;
};

export type ChangePasswordRequest = {
  /** Current Password 当前密码 */
  current_password: string;
  /** New Password 新密码 */
  new_password: string;
  /** Confirm Password 确认新密码 */
  confirm_password: string;
};

export type CreditCardCreate = {
  /** Card Name 卡片名称 */
  card_name: string;
  /** Card Number 卡号 */
  card_number: string;
  /** Card Type 卡片类型 */
  card_type?: string;
  /** Card Network 卡组织 */
  card_network?: string | null;
  /** Card Level 卡片等级 */
  card_level?: string | null;
  /** Credit Limit 信用额度 */
  credit_limit: number | string;
  /** Expiry Month 有效期月份 */
  expiry_month: number;
  /** Expiry Year 有效期年份 */
  expiry_year: number;
  /** Billing Date 账单日 */
  billing_date?: number | null;
  /** Due Date 还款日 */
  due_date?: number | null;
  /** Annual Fee 年费金额 */
  annual_fee?: number | string;
  /** Fee Waivable 年费是否可减免 */
  fee_waivable?: boolean;
  /** Fee Auto Deduct 是否自动扣费 */
  fee_auto_deduct?: boolean;
  /** Fee Due Month 年费到期月份 */
  fee_due_month?: number | null;
  /** Features 特色功能 */
  features?: string[];
  /** Points Rate 积分倍率 */
  points_rate?: number | string;
  /** Cashback Rate 返现比例 */
  cashback_rate?: number | string;
  /** Is Primary 是否主卡 */
  is_primary?: boolean;
  /** Notes 备注 */
  notes?: string | null;
  /** Bank Id 银行ID */
  bank_id?: string | null;
  /** Bank Name 银行名称（如果不提供bank_id） */
  bank_name?: string | null;
};

export type CreditCardStatusUpdate = {
  /** Status 状态 */
  status: string;
  /** Reason 状态变更原因 */
  reason?: string | null;
};

export type CreditCardUpdate = {
  /** Card Name 卡片名称 */
  card_name?: string | null;
  /** Card Type 卡片类型 */
  card_type?: string | null;
  /** Card Network 卡组织 */
  card_network?: string | null;
  /** Card Level 卡片等级 */
  card_level?: string | null;
  /** Credit Limit 信用额度 */
  credit_limit?: number | string | null;
  /** Available Limit 可用额度 */
  available_limit?: number | string | null;
  /** Used Limit 已用额度 */
  used_limit?: number | string | null;
  /** Expiry Month 有效期月份 */
  expiry_month?: number | null;
  /** Expiry Year 有效期年份 */
  expiry_year?: number | null;
  /** Billing Date 账单日 */
  billing_date?: number | null;
  /** Due Date 还款日 */
  due_date?: number | null;
  /** Annual Fee 年费金额 */
  annual_fee?: number | string | null;
  /** Fee Waivable 年费是否可减免 */
  fee_waivable?: boolean | null;
  /** Fee Auto Deduct 是否自动扣费 */
  fee_auto_deduct?: boolean | null;
  /** Fee Due Month 年费到期月份 */
  fee_due_month?: number | null;
  /** Features 特色功能 */
  features?: string[] | null;
  /** Points Rate 积分倍率 */
  points_rate?: number | string | null;
  /** Cashback Rate 返现比例 */
  cashback_rate?: number | string | null;
  /** Status 状态 */
  status?: string | null;
  /** Is Primary 是否主卡 */
  is_primary?: boolean | null;
  /** Notes 备注 */
  notes?: string | null;
};

export type deleteCreditCardApiV1UserCardsCardIdDeleteParams = {
  /** 信用卡ID */
  card_id: string;
};

export type deleteReminderSettingApiV1UserRemindersSettingsSettingIdDeleteParams =
  {
    /** 提醒设置ID */
    setting_id: string;
  };

export type deleteUserApiV1AdminUsersUserIdDeleteDeleteParams = {
  /** 用户ID */
  user_id: string;
};

export type getAnnualFeeSummaryApiV1AdminCardsAnnualFeeSummaryGetParams = {
  /** 指定年份，默认当前年份 */
  year?: number | null;
};

export type getBanksApiV1UserCardsBanksListGetParams = {
  /** 是否只返回激活的银行 */
  active_only?: boolean;
};

export type getCardTrendsApiV1AdminCardsTrendsGetParams = {
  /** 分析月数，1-24个月 */
  months?: number;
};

export type getCreditCardApiV1UserCardsCardIdGetParams = {
  /** 信用卡ID */
  card_id: string;
};

export type getCreditCardsApiV1UserCardsGetParams = {
  /** 搜索关键词，支持卡片名称、银行名称模糊搜索 */
  keyword?: string;
  /** 状态筛选 */
  status?: string | null;
  /** 银行ID筛选 */
  bank_id?: string | null;
  /** 卡片类型筛选 */
  card_type?: string | null;
  /** 是否主卡筛选 */
  is_primary?: boolean | null;
  /** 是否即将过期 */
  expiring_soon?: boolean | null;
  /** 页码，从1开始 */
  page?: number;
  /** 每页数量，最大100 */
  page_size?: number;
};

export type getExpiryAlertsApiV1AdminCardsExpiryAlertsGetParams = {
  /** 提前月数，1-12个月 */
  months_ahead?: number;
};

export type getLoginLogsApiV1UserProfileLoginLogsGetParams = {
  page?: number;
  page_size?: number;
};

export type getRecentRemindersApiV1UserRemindersRecentGetParams = {
  /** 返回数量限制，最大50 */
  limit?: number;
};

export type getReminderRecordApiV1UserRemindersRecordsRecordIdGetParams = {
  /** 提醒记录ID */
  record_id: string;
};

export type getReminderRecordsApiV1UserRemindersRecordsGetParams = {
  /** 页码，从1开始 */
  page?: number;
  /** 每页数量，最大100 */
  page_size?: number;
  /** 提醒设置ID筛选 */
  setting_id?: string | null;
  /** 状态筛选: pending, sent, read, cancelled */
  status?: string | null;
  /** 开始日期筛选 (YYYY-MM-DD) */
  start_date?: string | null;
  /** 结束日期筛选 (YYYY-MM-DD) */
  end_date?: string | null;
};

export type getReminderSettingApiV1UserRemindersSettingsSettingIdGetParams = {
  /** 提醒设置ID */
  setting_id: string;
};

export type getReminderSettingsApiV1UserRemindersSettingsGetParams = {
  /** 页码，从1开始 */
  page?: number;
  /** 每页数量，最大100 */
  page_size?: number;
  /** 信用卡ID筛选 */
  card_id?: string | null;
  /** 提醒类型筛选 */
  reminder_type?: string | null;
  /** 启用状态筛选 */
  is_enabled?: boolean | null;
};

export type getUpcomingRemindersApiV1UserRemindersUpcomingGetParams = {
  /** 查看未来天数，最大30天 */
  days_ahead?: number;
};

export type getUserDetailsApiV1AdminUsersUserIdDetailsGetParams = {
  /** 用户ID */
  user_id: string;
};

export type getUserLoginLogsApiV1AdminUsersUserIdLoginLogsGetParams = {
  /** 用户ID */
  user_id: string;
  /** 页码，从1开始 */
  page?: number;
  /** 每页数量，最大100 */
  page_size?: number;
};

export type getUsersListApiV1AdminUsersListGetParams = {
  /** 页码，从1开始 */
  page?: number;
  /** 每页数量，最大100 */
  page_size?: number;
  /** 搜索关键词（用户名、邮箱、昵称） */
  search?: string | null;
  /** 过滤用户状态：true=激活，false=禁用 */
  is_active?: boolean | null;
  /** 过滤管理员：true=管理员，false=普通用户 */
  is_admin?: boolean | null;
  /** 过滤验证状态：true=已验证，false=未验证 */
  is_verified?: boolean | null;
};

export type HTTPValidationError = {
  /** Detail */
  detail?: ValidationError[];
};

export type LoginLogResponse = {
  /** Id 日志ID */
  id: string;
  /** Login Type 登录类型 */
  login_type: string;
  /** Login Method 登录方式 */
  login_method: string;
  /** Ip Address IP地址 */
  ip_address?: string | null;
  /** User Agent 用户代理 */
  user_agent?: string | null;
  /** Location 地理位置 */
  location?: string | null;
  /** Is Success 是否成功 */
  is_success: boolean;
  /** Failure Reason 失败原因 */
  failure_reason?: string | null;
  /** Created At 创建时间 */
  created_at: string;
};

export type LoginRequest = {
  /** Username 用户名 */
  username: string;
  /** Password 密码 */
  password: string;
};

export type MarkAllReadResponse = {
  /** Marked Count 标记为已读的提醒数量 */
  marked_count: number;
  /** Marked At 标记时间 */
  marked_at: string;
  /** Message 操作结果消息 */
  message: string;
};

export type markReminderAsReadApiV1UserRemindersRecordsRecordIdReadPostParams =
  {
    /** 提醒记录ID */
    record_id: string;
  };

export type PaginationInfo = {
  /** Current Page 当前页码 */
  current_page: number;
  /** Page Size 每页数量 */
  page_size: number;
  /** Total 总记录数 */
  total: number;
  /** Total Pages 总页数 */
  total_pages: number;
  /** Has Next 是否有下一页 */
  has_next: boolean;
  /** Has Prev 是否有上一页 */
  has_prev: boolean;
};

export type RefreshTokenRequest = {
  /** Refresh Token 刷新令牌 */
  refresh_token: string;
};

export type RegisterRequest = {
  /** Username 用户名 */
  username: string;
  /** Email 邮箱 */
  email: string;
  /** Password 密码 */
  password: string;
  /** Nickname 昵称 */
  nickname?: string | null;
};

export type ReminderRecordCreate = {
  /** Setting Id 提醒设置ID */
  setting_id: string;
  /** Card Id 信用卡ID */
  card_id?: string | null;
  /** Reminder Type 提醒类型 */
  reminder_type: string;
  /** Title 提醒标题 */
  title: string;
  /** Content 提醒内容 */
  content: string;
  /** Email Sent 邮件是否发送 */
  email_sent?: boolean;
  /** Sms Sent 短信是否发送 */
  sms_sent?: boolean;
  /** Push Sent 推送是否发送 */
  push_sent?: boolean;
  /** Wechat Sent 微信是否发送 */
  wechat_sent?: boolean;
  /** Scheduled At 计划发送时间 */
  scheduled_at?: string | null;
};

export type ReminderRecordResponse = object;

export type ReminderSettingCreate = {
  /** Card Id 信用卡ID，NULL表示全局提醒 */
  card_id?: string | null;
  /** Reminder Type 提醒类型: payment, annual_fee, card_expiry, custom */
  reminder_type: string;
  /** Advance Days 提前天数 */
  advance_days?: number;
  /** Reminder Time 提醒时间 */
  reminder_time?: string | null;
  /** Email Enabled 邮件提醒 */
  email_enabled?: boolean;
  /** Sms Enabled 短信提醒 */
  sms_enabled?: boolean;
  /** Push Enabled 推送提醒 */
  push_enabled?: boolean;
  /** Wechat Enabled 微信提醒 */
  wechat_enabled?: boolean;
  /** Is Recurring 是否循环 */
  is_recurring?: boolean;
  /** Frequency 频率: daily, weekly, monthly, yearly */
  frequency?: string;
  /** Is Enabled 是否启用 */
  is_enabled?: boolean;
};

export type ReminderSettingResponse = object;

export type ReminderSettingUpdate = {
  /** Advance Days 提前天数 */
  advance_days?: number | null;
  /** Reminder Time 提醒时间 */
  reminder_time?: string | null;
  /** Email Enabled 邮件提醒 */
  email_enabled?: boolean | null;
  /** Sms Enabled 短信提醒 */
  sms_enabled?: boolean | null;
  /** Push Enabled 推送提醒 */
  push_enabled?: boolean | null;
  /** Wechat Enabled 微信提醒 */
  wechat_enabled?: boolean | null;
  /** Is Recurring 是否循环 */
  is_recurring?: boolean | null;
  /** Frequency 频率 */
  frequency?: string | null;
  /** Is Enabled 是否启用 */
  is_enabled?: boolean | null;
};

export type ReminderStatisticsResponse = {
  /** Total Settings 总设置数 */
  total_settings: number;
  /** Active Settings 活跃设置数 */
  active_settings: number;
  /** Total Reminders 30Days 30天内提醒总数 */
  total_reminders_30days: number;
  /** Pending Reminders 待处理提醒数 */
  pending_reminders: number;
  /** Read Rate 阅读率 */
  read_rate: number;
  /** Type Distribution 类型分布 */
  type_distribution: Record<string, unknown>;
  /** Recent Reminders 最近提醒 */
  recent_reminders: ReminderRecordResponse[];
};

export type TokenResponse = {
  /** Access Token 访问令牌 */
  access_token: string;
  /** Refresh Token 刷新令牌 */
  refresh_token: string;
  /** Token Type 令牌类型 */
  token_type?: string;
};

export type UnreadRemindersCountResponse = {
  /** Total Unread 未读提醒总数 */
  total_unread: number;
  /** Type Breakdown 按类型分布的未读提醒数 */
  type_breakdown: Record<string, unknown>;
  /** Last Check Time 最后检查时间 */
  last_check_time: string;
};

export type UpcomingRemindersResponse = {
  /** Total Upcoming 即将到来的提醒总数 */
  total_upcoming: number;
  /** High Priority Count 高优先级提醒数 */
  high_priority_count: number;
  /** Medium Priority Count 中优先级提醒数 */
  medium_priority_count: number;
  /** Low Priority Count 低优先级提醒数 */
  low_priority_count: number;
  /** Analysis Period 分析周期 */
  analysis_period: string;
  /** Reminders 提醒列表 */
  reminders: Record<string, unknown>[];
};

export type updateCardStatusApiV1UserCardsCardIdStatusPatchParams = {
  /** 信用卡ID */
  card_id: string;
};

export type updateCreditCardApiV1UserCardsCardIdPutParams = {
  /** 信用卡ID */
  card_id: string;
};

export type updateReminderSettingApiV1UserRemindersSettingsSettingIdPutParams =
  {
    /** 提醒设置ID */
    setting_id: string;
  };

export type updateUserPermissionsApiV1AdminUsersUserIdPermissionsPutParams = {
  /** 用户ID */
  user_id: string;
};

export type updateUserStatusApiV1AdminUsersUserIdStatusPutParams = {
  /** 用户ID */
  user_id: string;
};

export type UserDeletionRequest = {
  /** Reason 删除原因 */
  reason: string;
  /** Confirm Username 确认用户名 */
  confirm_username: string;
};

export type UserPermissionsUpdateRequest = {
  /** Is Admin 是否管理员 */
  is_admin: boolean;
  /** Is Verified 是否已验证 */
  is_verified: boolean;
  /** Reason 操作原因 */
  reason?: string | null;
};

export type UserProfileResponse = {
  /** Id 用户ID */
  id: string;
  /** Username 用户名 */
  username: string;
  /** Email 邮箱地址 */
  email: string;
  /** Nickname 昵称 */
  nickname?: string | null;
  /** Phone 手机号 */
  phone?: string | null;
  /** Avatar Url 头像URL */
  avatar_url?: string | null;
  /** Is Active 是否激活 */
  is_active: boolean;
  /** Is Verified 是否已验证 */
  is_verified: boolean;
  /** Timezone 时区 */
  timezone: string;
  /** Language 语言偏好 */
  language: string;
  /** Currency 默认货币 */
  currency: string;
  /** Last Login At 最后登录时间 */
  last_login_at?: string | null;
  /** Email Verified At 邮箱验证时间 */
  email_verified_at?: string | null;
  /** Created At 创建时间 */
  created_at: string;
};

export type UserProfileUpdateRequest = {
  /** Nickname 昵称 */
  nickname?: string | null;
  /** Phone 手机号 */
  phone?: string | null;
  /** Avatar Url 头像URL */
  avatar_url?: string | null;
  /** Timezone 时区 */
  timezone?: string | null;
  /** Language 语言偏好 */
  language?: string | null;
  /** Currency 默认货币 */
  currency?: string | null;
};

export type UserStatisticsResponse = {
  /** Total Cards 信用卡总数 */
  total_cards: number;
  /** Active Cards 活跃信用卡数 */
  active_cards: number;
  /** Total Credit Limit 总信用额度 */
  total_credit_limit: number;
  /** Total Used Limit 总已用额度 */
  total_used_limit: number;
  /** Credit Utilization 信用利用率(%) */
  credit_utilization: number;
  /** Total Transactions 总交易笔数 */
  total_transactions: number;
  /** Total Spending 总支出金额 */
  total_spending: number;
  /** This Month Spending 本月支出金额 */
  this_month_spending: number;
  /** Total Income 总收入金额 */
  total_income: number;
  /** Avg Transaction 平均交易金额 */
  avg_transaction: number;
  /** Total Annual Fees 总年费金额 */
  total_annual_fees: number;
  /** Waived Fees 已减免年费 */
  waived_fees: number;
  /** Pending Fees 待缴年费 */
  pending_fees: number;
  /** Total Points Earned 总获得积分 */
  total_points_earned: number;
  /** Total Cashback Earned 总获得返现 */
  total_cashback_earned: number;
  /** Active Reminders 活跃提醒数 */
  active_reminders: number;
  /** Account Age Days 账户天数 */
  account_age_days: number;
  /** Last Transaction Date 最后交易时间 */
  last_transaction_date?: string | null;
};

export type UserStatusUpdateRequest = {
  /** Is Active 是否激活 */
  is_active: boolean;
  /** Reason 操作原因 */
  reason?: string | null;
};

export type ValidationError = {
  /** Location */
  loc: (string | number)[];
  /** Message */
  msg: string;
  /** Error Type */
  type: string;
};

export type WechatBindingResponse = {
  /** Id 绑定ID */
  id: string;
  /** Openid 微信OpenID */
  openid: string;
  /** Unionid 微信UnionID */
  unionid?: string | null;
  /** Nickname 微信昵称 */
  nickname?: string | null;
  /** Avatar Url 微信头像 */
  avatar_url?: string | null;
  /** Is Active 是否激活 */
  is_active: boolean;
  /** Bound At 绑定时间 */
  bound_at: string;
};
