"""
年费管理相关的数据模型

本模块定义了年费管理功能所需的所有Pydantic模型，包括：
- 年费规则创建、更新、查询请求模型
- 年费记录响应模型
- 年费统计分析模型
- 减免规则模型

作者: LEO
邮箱: leoyfm@gmail.com
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Any, Dict
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum

# 枚举定义
class AnnualFeeType(str, Enum):
    """年费类型"""
    rigid = "rigid"                    # 刚性年费（必须支付）
    waiver_by_transactions = "waiver_by_transactions"  # 刷卡次数减免
    waiver_by_amount = "waiver_by_amount"              # 刷卡金额减免
    waiver_by_points = "waiver_by_points"              # 积分兑换减免

class FeeStatus(str, Enum):
    """年费状态"""
    pending = "pending"        # 待缴费
    paid = "paid"             # 已缴费
    waived = "waived"         # 已减免
    overdue = "overdue"       # 逾期未缴

class WaiverStatus(str, Enum):
    """减免状态"""
    not_applicable = "not_applicable"  # 不适用
    in_progress = "in_progress"        # 进行中
    completed = "completed"            # 已完成
    failed = "failed"                  # 减免失败

# 年费规则创建请求
class AnnualFeeRuleCreateRequest(BaseModel):
    """创建年费规则请求"""
    card_id: UUID = Field(..., description="信用卡ID")
    fee_type: AnnualFeeType = Field(..., description="年费类型")
    base_fee: Decimal = Field(..., gt=0, le=99999, description="基础年费金额", example=300.00)
    currency: str = Field("CNY", description="货币类型", example="CNY")
    waiver_condition: Optional[Dict[str, Any]] = Field(None, description="减免条件配置")
    effective_date: date = Field(..., description="生效日期")
    expiry_date: Optional[date] = Field(None, description="失效日期（可选）")
    auto_renewal: bool = Field(True, description="是否自动续费")
    reminder_days: int = Field(30, ge=1, le=365, description="提前提醒天数")
    description: Optional[str] = Field(None, max_length=200, description="规则描述")
    is_active: bool = Field(True, description="是否启用")

    @validator('waiver_condition')
    def validate_waiver_condition(cls, v, values):
        """验证减免条件"""
        fee_type = values.get('fee_type')
        if not fee_type:
            return v
        
        if fee_type == AnnualFeeType.waiver_by_transactions:
            if not v or 'min_transactions' not in v:
                raise ValueError("刷卡次数减免类型必须设置min_transactions条件")
            if not isinstance(v['min_transactions'], int) or v['min_transactions'] <= 0:
                raise ValueError("min_transactions必须为正整数")
        
        elif fee_type == AnnualFeeType.waiver_by_amount:
            if not v or 'min_amount' not in v:
                raise ValueError("刷卡金额减免类型必须设置min_amount条件")
            if not isinstance(v['min_amount'], (int, float)) or v['min_amount'] <= 0:
                raise ValueError("min_amount必须为正数")
        
        elif fee_type == AnnualFeeType.waiver_by_points:
            if not v or 'required_points' not in v:
                raise ValueError("积分兑换减免类型必须设置required_points条件")
            if not isinstance(v['required_points'], int) or v['required_points'] <= 0:
                raise ValueError("required_points必须为正整数")
        
        return v

    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        """验证失效日期"""
        effective_date = values.get('effective_date')
        if v and effective_date and v <= effective_date:
            raise ValueError("失效日期必须晚于生效日期")
        return v

# 年费规则更新请求
class AnnualFeeRuleUpdateRequest(BaseModel):
    """更新年费规则请求"""
    fee_type: Optional[AnnualFeeType] = Field(None, description="年费类型")
    base_fee: Optional[Decimal] = Field(None, gt=0, le=99999, description="基础年费金额")
    currency: Optional[str] = Field(None, description="货币类型")
    waiver_condition: Optional[Dict[str, Any]] = Field(None, description="减免条件配置")
    effective_date: Optional[date] = Field(None, description="生效日期")
    expiry_date: Optional[date] = Field(None, description="失效日期")
    auto_renewal: Optional[bool] = Field(None, description="是否自动续费")
    reminder_days: Optional[int] = Field(None, ge=1, le=365, description="提前提醒天数")
    description: Optional[str] = Field(None, max_length=200, description="规则描述")
    is_active: Optional[bool] = Field(None, description="是否启用")

# 年费规则响应模型
class AnnualFeeRuleResponse(BaseModel):
    """年费规则响应"""
    id: UUID = Field(..., description="规则ID")
    user_id: UUID = Field(..., description="用户ID")
    card_id: UUID = Field(..., description="信用卡ID")
    card_name: str = Field(..., description="信用卡名称")
    bank_name: str = Field(..., description="银行名称")
    fee_type: AnnualFeeType = Field(..., description="年费类型")
    base_fee: Decimal = Field(..., description="基础年费金额")
    currency: str = Field(..., description="货币类型")
    waiver_condition: Optional[Dict[str, Any]] = Field(None, description="减免条件配置")
    effective_date: date = Field(..., description="生效日期")
    expiry_date: Optional[date] = Field(None, description="失效日期")
    auto_renewal: bool = Field(..., description="是否自动续费")
    reminder_days: int = Field(..., description="提前提醒天数")
    description: Optional[str] = Field(None, description="规则描述")
    is_active: bool = Field(..., description="是否启用")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True

# 年费记录创建请求
class AnnualFeeRecordCreateRequest(BaseModel):
    """创建年费记录请求"""
    rule_id: UUID = Field(..., description="年费规则ID")
    fee_year: int = Field(..., ge=2020, le=2050, description="年费年度", example=2024)
    due_date: date = Field(..., description="到期日期")
    actual_fee: Optional[Decimal] = Field(None, gt=0, le=99999, description="实际年费金额（可能有优惠）")
    notes: Optional[str] = Field(None, max_length=500, description="备注说明")

    @validator('due_date')
    def validate_due_date(cls, v):
        """验证到期日期"""
        if v < date.today():
            raise ValueError("到期日期不能是过去时间")
        return v

# 年费记录更新请求
class AnnualFeeRecordUpdateRequest(BaseModel):
    """更新年费记录请求"""
    status: Optional[FeeStatus] = Field(None, description="年费状态")
    actual_fee: Optional[Decimal] = Field(None, gt=0, le=99999, description="实际年费金额")
    paid_date: Optional[date] = Field(None, description="缴费日期")
    waiver_reason: Optional[str] = Field(None, max_length=200, description="减免原因")
    notes: Optional[str] = Field(None, max_length=500, description="备注说明")

# 年费记录响应模型
class AnnualFeeRecordResponse(BaseModel):
    """年费记录响应"""
    id: UUID = Field(..., description="记录ID")
    user_id: UUID = Field(..., description="用户ID")
    rule_id: UUID = Field(..., description="年费规则ID")
    card_id: UUID = Field(..., description="信用卡ID")
    card_name: str = Field(..., description="信用卡名称")
    bank_name: str = Field(..., description="银行名称")
    fee_year: int = Field(..., description="年费年度")
    fee_type: AnnualFeeType = Field(..., description="年费类型")
    base_fee: Decimal = Field(..., description="基础年费金额")
    actual_fee: Decimal = Field(..., description="实际年费金额")
    currency: str = Field(..., description="货币类型")
    status: FeeStatus = Field(..., description="年费状态")
    due_date: date = Field(..., description="到期日期")
    paid_date: Optional[date] = Field(None, description="缴费日期")
    waiver_progress: Optional[Dict[str, Any]] = Field(None, description="减免进度")
    waiver_status: WaiverStatus = Field(..., description="减免状态")
    waiver_reason: Optional[str] = Field(None, description="减免原因")
    is_overdue: bool = Field(..., description="是否逾期")
    days_until_due: int = Field(..., description="距离到期天数")
    notes: Optional[str] = Field(None, description="备注说明")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True

# 年费记录详细信息响应
class AnnualFeeRecordDetailResponse(AnnualFeeRecordResponse):
    """年费记录详细信息响应"""
    rule_info: AnnualFeeRuleResponse = Field(..., description="关联的年费规则详情")
    waiver_analysis: Optional[Dict[str, Any]] = Field(None, description="减免条件分析")
    payment_history: List[Dict[str, Any]] = Field(default_factory=list, description="缴费历史")
    related_transactions: List[Dict[str, Any]] = Field(default_factory=list, description="相关交易")

# 年费列表查询参数
class AnnualFeeListQuery(BaseModel):
    """年费列表查询参数"""
    keyword: str = Field("", description="搜索关键词，支持卡片名称、银行名称模糊搜索")
    fee_type: Optional[AnnualFeeType] = Field(None, description="年费类型筛选")
    status: Optional[FeeStatus] = Field(None, description="年费状态筛选")
    card_id: Optional[UUID] = Field(None, description="信用卡筛选")
    fee_year: Optional[int] = Field(None, description="年费年度筛选")
    waiver_status: Optional[WaiverStatus] = Field(None, description="减免状态筛选")
    is_overdue: Optional[bool] = Field(None, description="是否逾期筛选")
    due_soon: Optional[bool] = Field(None, description="是否即将到期筛选（30天内）")
    sort_by: str = Field("due_date", description="排序字段：due_date, fee_year, created_at, actual_fee")
    sort_order: str = Field("asc", description="排序方向：asc, desc")

# 年费统计信息
class AnnualFeeStatistics(BaseModel):
    """年费统计信息"""
    total_rules: int = Field(0, description="年费规则总数")
    active_rules: int = Field(0, description="活跃规则数")
    total_records: int = Field(0, description="年费记录总数")
    pending_records: int = Field(0, description="待缴费记录数")
    paid_records: int = Field(0, description="已缴费记录数")
    waived_records: int = Field(0, description="已减免记录数")
    overdue_records: int = Field(0, description="逾期记录数")
    total_fees_due: Decimal = Field(Decimal("0"), description="应缴费总额")
    total_fees_paid: Decimal = Field(Decimal("0"), description="已缴费总额")
    total_fees_waived: Decimal = Field(Decimal("0"), description="已减免总额")
    average_fee: Decimal = Field(Decimal("0"), description="平均年费")
    fees_by_type: Dict[str, int] = Field(default_factory=dict, description="按类型分组的年费数")
    fees_by_status: Dict[str, int] = Field(default_factory=dict, description="按状态分组的年费数")
    fees_by_bank: Dict[str, Decimal] = Field(default_factory=dict, description="按银行分组的年费")
    waiver_success_rate: float = Field(0.0, description="减免成功率")
    upcoming_due_dates: List[Dict[str, Any]] = Field(default_factory=list, description="即将到期的年费")

# 年费提醒设置
class AnnualFeeReminderSettings(BaseModel):
    """年费提醒设置"""
    rule_id: UUID = Field(..., description="年费规则ID")
    reminder_enabled: bool = Field(True, description="是否启用提醒")
    reminder_days: List[int] = Field([30, 15, 7, 1], description="提醒天数列表")
    email_reminder: bool = Field(True, description="是否邮件提醒")
    sms_reminder: bool = Field(False, description="是否短信提醒")
    push_reminder: bool = Field(True, description="是否推送提醒")
    reminder_message: Optional[str] = Field(None, max_length=200, description="自定义提醒消息")

# 年费减免进度
class WaiverProgress(BaseModel):
    """年费减免进度"""
    record_id: UUID = Field(..., description="年费记录ID")
    waiver_type: AnnualFeeType = Field(..., description="减免类型")
    current_progress: Dict[str, Any] = Field(..., description="当前进度")
    required_target: Dict[str, Any] = Field(..., description="目标要求")
    progress_percentage: float = Field(..., ge=0, le=100, description="完成百分比")
    is_completed: bool = Field(False, description="是否已完成")
    completion_date: Optional[date] = Field(None, description="完成日期")
    estimated_completion: Optional[date] = Field(None, description="预计完成日期")
    suggestions: List[str] = Field(default_factory=list, description="完成建议")

# 批量处理年费请求
class AnnualFeeBatchRequest(BaseModel):
    """批量处理年费请求"""
    record_ids: List[UUID] = Field(..., min_items=1, max_items=50, description="年费记录ID列表")
    operation: str = Field(..., description="操作类型：pay, waive, extend_due_date")
    data: Dict[str, Any] = Field(..., description="操作数据")

# 批量处理响应
class AnnualFeeBatchResponse(BaseModel):
    """批量处理响应"""
    success_count: int = Field(..., description="成功处理的数量")
    failed_count: int = Field(..., description="处理失败的数量")
    failed_items: List[Dict[str, Any]] = Field(default_factory=list, description="失败的项目详情")
    message: str = Field(..., description="处理结果消息")

# 年费分析报告
class AnnualFeeAnalysisReport(BaseModel):
    """年费分析报告"""
    period: str = Field(..., description="分析期间", example="2024")
    summary: AnnualFeeStatistics = Field(..., description="统计摘要")
    cost_analysis: Dict[str, Any] = Field(..., description="成本分析")
    waiver_analysis: Dict[str, Any] = Field(..., description="减免分析")
    recommendations: List[str] = Field(default_factory=list, description="优化建议")
    forecast: Dict[str, Any] = Field(..., description="下年度预测")

# 年费优化建议
class AnnualFeeOptimization(BaseModel):
    """年费优化建议"""
    user_id: UUID = Field(..., description="用户ID")
    optimization_type: str = Field(..., description="优化类型")
    current_cost: Decimal = Field(..., description="当前年费成本")
    optimized_cost: Decimal = Field(..., description="优化后成本")
    potential_savings: Decimal = Field(..., description="潜在节省金额")
    recommendations: List[Dict[str, Any]] = Field(..., description="具体建议")
    implementation_steps: List[str] = Field(default_factory=list, description="实施步骤")
    risk_assessment: str = Field(..., description="风险评估")
    confidence_score: float = Field(..., ge=0, le=1, description="建议置信度")

# 年费提醒响应
class AnnualFeeReminder(BaseModel):
    """年费提醒"""
    record_id: UUID = Field(..., description="年费记录ID")
    card_name: str = Field(..., description="信用卡名称")
    bank_name: str = Field(..., description="银行名称")
    fee_amount: Decimal = Field(..., description="年费金额")
    due_date: date = Field(..., description="到期日期")
    days_until_due: int = Field(..., description="距离到期天数")
    reminder_type: str = Field(..., description="提醒类型：due_soon, overdue, waiver_opportunity")
    message: str = Field(..., description="提醒消息")
    action_required: bool = Field(False, description="是否需要用户操作")
    action_url: Optional[str] = Field(None, description="操作链接")
    priority: str = Field("medium", description="优先级：low, medium, high, urgent")
    created_at: datetime = Field(..., description="提醒创建时间")

# 减免分析模型
class WaiverAnalysis(BaseModel):
    """减免分析"""
    card_id: UUID = Field(..., description="信用卡ID")
    fee_year: int = Field(..., description="年费年度")
    base_fee: Decimal = Field(..., description="基础年费")
    waiver_eligible: bool = Field(..., description="是否符合减免条件")
    waiver_amount: Decimal = Field(Decimal("0"), description="减免金额")
    final_fee: Decimal = Field(..., description="最终年费")
    analysis_details: Dict[str, Any] = Field(default_factory=dict, description="分析详情")

# 年费提醒设置模型
class FeeReminderSettings(BaseModel):
    """年费提醒设置"""
    rule_id: UUID = Field(..., description="年费规则ID")
    enabled: bool = Field(True, description="是否启用")
    advance_days: int = Field(30, description="提前天数")
    reminder_types: List[str] = Field(default_factory=list, description="提醒类型")

# 年费类型别名（兼容旧代码）
FeeType = AnnualFeeType

# 条件类型枚举
class ConditionType(str, Enum):
    """条件类型"""
    amount = "amount"      # 金额条件
    count = "count"        # 次数条件
    points = "points"      # 积分条件

# 基础年费规则模型（用于服务层）
class AnnualFeeRule(AnnualFeeRuleResponse):
    """基础年费规则模型（继承自AnnualFeeRuleResponse）"""
    pass

# 基础年费记录模型（用于服务层）
class AnnualFeeRecord(AnnualFeeRecordResponse):
    """基础年费记录模型（继承自AnnualFeeRecordResponse）"""
    pass

# 别名定义
AnnualFeeRuleCreate = AnnualFeeRuleCreateRequest
AnnualFeeRuleUpdate = AnnualFeeRuleUpdateRequest
AnnualFeeRecordCreate = AnnualFeeRecordCreateRequest
AnnualFeeRecordUpdate = AnnualFeeRecordUpdateRequest
AnnualFeeQueryFilter = AnnualFeeListQuery
AnnualFeeBatchOperation = AnnualFeeBatchRequest
AnnualFeeStats = AnnualFeeStatistics 