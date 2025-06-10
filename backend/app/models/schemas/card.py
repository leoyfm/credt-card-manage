"""
信用卡管理相关的数据模型

本模块定义了信用卡管理功能所需的所有Pydantic模型，包括：
- 信用卡创建、更新、查询请求模型
- 信用卡响应模型
- 银行信息模型
- 统计分析模型

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
class CardType(str, Enum):
    """信用卡类型"""
    credit = "credit"
    debit = "debit"

class CardNetwork(str, Enum):
    """卡组织"""
    visa = "VISA"
    mastercard = "MasterCard"
    unionpay = "银联"
    amex = "American Express"
    jcb = "JCB"

class CardLevel(str, Enum):
    """卡片等级"""
    regular = "普卡"
    gold = "金卡"
    platinum = "白金卡"
    diamond = "钻石卡"
    infinite = "无限卡"

class CardStatus(str, Enum):
    """卡片状态"""
    active = "active"
    frozen = "frozen"
    closed = "closed"

# 银行相关模型
class BankInfo(BaseModel):
    """银行信息"""
    id: UUID = Field(..., description="银行ID")
    bank_code: str = Field(..., description="银行代码")
    bank_name: str = Field(..., description="银行名称")
    bank_logo: Optional[str] = Field(None, description="银行logo URL")
    is_active: bool = Field(True, description="是否激活")
    sort_order: int = Field(0, description="排序")

    class Config:
        from_attributes = True

# 信用卡创建请求
class CardCreateRequest(BaseModel):
    """创建信用卡请求"""
    card_number: str = Field(..., min_length=13, max_length=19, description="卡号", example="6225881234567890")
    card_name: str = Field(..., min_length=1, max_length=100, description="卡片名称", example="我的招商银行信用卡")
    bank_name: str = Field(..., min_length=1, max_length=100, description="银行名称", example="招商银行")
    card_type: CardType = Field(CardType.credit, description="卡片类型")
    card_network: Optional[CardNetwork] = Field(None, description="卡组织")
    card_level: Optional[CardLevel] = Field(None, description="卡片等级")
    credit_limit: Decimal = Field(..., gt=0, le=9999999, description="信用额度", example=50000.00)
    expiry_month: int = Field(..., ge=1, le=12, description="有效期月份", example=12)
    expiry_year: int = Field(..., ge=2024, le=2050, description="有效期年份", example=2027)
    billing_date: Optional[int] = Field(None, ge=1, le=31, description="账单日", example=5)
    due_date: Optional[int] = Field(None, ge=1, le=31, description="还款日", example=25)
    annual_fee: Decimal = Field(Decimal("0"), ge=0, le=99999, description="年费金额", example=200.00)
    fee_waivable: bool = Field(False, description="年费是否可减免")
    fee_auto_deduct: bool = Field(False, description="是否自动扣费")
    fee_due_month: Optional[int] = Field(None, ge=1, le=12, description="年费到期月份")
    features: List[str] = Field(default_factory=list, description="特色功能", example=["免年费", "全球免费取现"])
    points_rate: Decimal = Field(Decimal("1.0"), ge=0, le=100, description="积分倍率", example=1.5)
    cashback_rate: Decimal = Field(Decimal("0.0"), ge=0, le=100, description="返现比例", example=0.5)
    notes: Optional[str] = Field(None, max_length=500, description="备注", example="主要用于日常消费")

    @validator('expiry_year')
    def validate_expiry_year(cls, v):
        """验证有效期年份不能是过去的年份"""
        current_year = datetime.now().year
        if v < current_year:
            raise ValueError("有效期年份不能是过去的年份")
        return v

    @validator('card_number')
    def validate_card_number(cls, v):
        """验证卡号格式"""
        # 移除空格和连字符
        card_number = v.replace(' ', '').replace('-', '')
        # 检查是否只包含数字
        if not card_number.isdigit():
            raise ValueError("卡号只能包含数字")
        # 检查长度
        if len(card_number) < 13 or len(card_number) > 19:
            raise ValueError("卡号长度必须在13-19位之间")
        return card_number

# 信用卡更新请求
class CardUpdateRequest(BaseModel):
    """更新信用卡请求"""
    card_name: Optional[str] = Field(None, min_length=1, max_length=100, description="卡片名称")
    card_network: Optional[CardNetwork] = Field(None, description="卡组织")
    card_level: Optional[CardLevel] = Field(None, description="卡片等级")
    credit_limit: Optional[Decimal] = Field(None, gt=0, le=9999999, description="信用额度")
    available_limit: Optional[Decimal] = Field(None, ge=0, description="可用额度")
    billing_date: Optional[int] = Field(None, ge=1, le=31, description="账单日")
    due_date: Optional[int] = Field(None, ge=1, le=31, description="还款日")
    annual_fee: Optional[Decimal] = Field(None, ge=0, le=99999, description="年费金额")
    fee_waivable: Optional[bool] = Field(None, description="年费是否可减免")
    fee_auto_deduct: Optional[bool] = Field(None, description="是否自动扣费")
    fee_due_month: Optional[int] = Field(None, ge=1, le=12, description="年费到期月份")
    features: Optional[List[str]] = Field(None, description="特色功能")
    points_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="积分倍率")
    cashback_rate: Optional[Decimal] = Field(None, ge=0, le=100, description="返现比例")
    notes: Optional[str] = Field(None, max_length=500, description="备注")

    @validator('available_limit')
    def validate_available_limit(cls, v, values):
        """验证可用额度不能超过信用额度"""
        credit_limit = values.get('credit_limit')
        if credit_limit and v and v > credit_limit:
            raise ValueError("可用额度不能超过信用额度")
        return v

# 信用卡状态更新请求
class CardStatusUpdateRequest(BaseModel):
    """信用卡状态更新请求"""
    status: CardStatus = Field(..., description="卡片状态")
    reason: Optional[str] = Field(None, max_length=200, description="状态变更原因")

# 信用卡响应模型
class CardResponse(BaseModel):
    """信用卡信息响应"""
    id: UUID = Field(..., description="信用卡ID")
    user_id: UUID = Field(..., description="用户ID")
    card_number_masked: str = Field(..., description="卡号（脱敏）", example="6225 88** **** 7890")
    card_name: str = Field(..., description="卡片名称")
    bank_name: str = Field(..., description="银行名称")
    card_type: CardType = Field(..., description="卡片类型")
    card_network: Optional[CardNetwork] = Field(None, description="卡组织")
    card_level: Optional[CardLevel] = Field(None, description="卡片等级")
    credit_limit: Decimal = Field(..., description="信用额度")
    available_limit: Optional[Decimal] = Field(None, description="可用额度")
    used_limit: Decimal = Field(..., description="已用额度")
    expiry_month: int = Field(..., description="有效期月份")
    expiry_year: int = Field(..., description="有效期年份")
    expiry_display: str = Field(..., description="有效期显示", example="12/27")
    billing_date: Optional[int] = Field(None, description="账单日")
    due_date: Optional[int] = Field(None, description="还款日")
    annual_fee: Decimal = Field(..., description="年费金额")
    fee_waivable: bool = Field(..., description="年费是否可减免")
    fee_auto_deduct: bool = Field(..., description="是否自动扣费")
    fee_due_month: Optional[int] = Field(None, description="年费到期月份")
    features: List[str] = Field(..., description="特色功能")
    points_rate: Decimal = Field(..., description="积分倍率")
    cashback_rate: Decimal = Field(..., description="返现比例")
    status: CardStatus = Field(..., description="卡片状态")
    is_primary: bool = Field(..., description="是否主卡")
    is_expired: bool = Field(..., description="是否已过期")
    expires_soon: bool = Field(..., description="是否即将过期（3个月内）")
    credit_utilization: Optional[Decimal] = Field(None, description="信用利用率（百分比）", example=25.5)
    notes: Optional[str] = Field(None, description="备注")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True

# 信用卡详细信息响应
class CardDetailResponse(CardResponse):
    """信用卡详细信息响应（包含敏感信息）"""
    card_number: str = Field(..., description="完整卡号（仅所有者可见）", example="6225881234567890")
    bank_info: Optional[BankInfo] = Field(None, description="银行详细信息")
    recent_transactions_count: int = Field(0, description="最近30天交易笔数")
    recent_spending: Decimal = Field(Decimal("0"), description="最近30天消费金额")
    annual_fee_status: str = Field("未设置", description="年费状态", example="已减免")
    next_bill_date: Optional[date] = Field(None, description="下次账单日")
    next_due_date: Optional[date] = Field(None, description="下次还款日")

# 信用卡列表查询参数
class CardListQuery(BaseModel):
    """信用卡列表查询参数"""
    keyword: str = Field("", description="搜索关键词，支持卡片名称、银行名称模糊搜索")
    status: Optional[CardStatus] = Field(None, description="卡片状态筛选")
    card_type: Optional[CardType] = Field(None, description="卡片类型筛选")
    bank_name: Optional[str] = Field(None, description="银行名称筛选")
    is_primary: Optional[bool] = Field(None, description="是否主卡筛选")
    expires_soon: Optional[bool] = Field(None, description="是否即将过期筛选")
    sort_by: str = Field("created_at", description="排序字段：created_at, credit_limit, card_name")
    sort_order: str = Field("desc", description="排序方向：asc, desc")

# 信用卡统计信息
class CardStatistics(BaseModel):
    """信用卡统计信息"""
    total_cards: int = Field(0, description="信用卡总数")
    active_cards: int = Field(0, description="激活的信用卡数")
    total_credit_limit: Decimal = Field(Decimal("0"), description="总信用额度")
    total_available_limit: Decimal = Field(Decimal("0"), description="总可用额度")
    total_used_limit: Decimal = Field(Decimal("0"), description="总已用额度")
    average_credit_utilization: Decimal = Field(Decimal("0"), description="平均信用利用率")
    cards_by_status: Dict[str, int] = Field(default_factory=dict, description="按状态分组的卡片数量")
    cards_by_bank: Dict[str, int] = Field(default_factory=dict, description="按银行分组的卡片数量")
    cards_by_network: Dict[str, int] = Field(default_factory=dict, description="按卡组织分组的卡片数量")
    expiring_soon_count: int = Field(0, description="即将过期的卡片数量")
    annual_fee_total: Decimal = Field(Decimal("0"), description="年费总额")
    annual_fee_waivable_count: int = Field(0, description="可减免年费的卡片数量")

# 银行列表响应
class BankListResponse(BaseModel):
    """银行列表响应"""
    banks: List[BankInfo] = Field(..., description="银行列表")
    total: int = Field(..., description="银行总数")

# 批量操作请求
class CardBatchUpdateRequest(BaseModel):
    """批量更新信用卡请求"""
    card_ids: List[UUID] = Field(..., min_items=1, max_items=50, description="信用卡ID列表")
    operation: str = Field(..., description="操作类型：status_update, bank_update")
    data: Dict[str, Any] = Field(..., description="更新数据")

# 批量操作响应
class CardBatchUpdateResponse(BaseModel):
    """批量更新响应"""
    success_count: int = Field(..., description="成功更新的数量")
    failed_count: int = Field(..., description="更新失败的数量")
    failed_items: List[Dict[str, Any]] = Field(default_factory=list, description="失败的项目详情")
    message: str = Field(..., description="操作结果消息")

# 信用卡导入请求
class CardImportRequest(BaseModel):
    """信用卡批量导入请求"""
    cards: List[CardCreateRequest] = Field(..., min_items=1, max_items=100, description="信用卡列表")
    overwrite_existing: bool = Field(False, description="是否覆盖现有卡片")

# 信用卡导入响应
class CardImportResponse(BaseModel):
    """信用卡导入响应"""
    total_count: int = Field(..., description="总数量")
    success_count: int = Field(..., description="成功导入数量")
    failed_count: int = Field(..., description="导入失败数量")
    skipped_count: int = Field(..., description="跳过数量")
    failed_items: List[Dict[str, Any]] = Field(default_factory=list, description="失败项目详情")
    message: str = Field(..., description="导入结果消息") 