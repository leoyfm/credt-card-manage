"""
用户功能区 - 交易管理接口

本模块提供用户个人交易管理的所有接口：
- 交易CRUD操作
- 交易分类管理
- 交易统计分析
- 批量导入导出

权限等级: Level 2 (用户认证)
数据范围: 仅自有交易数据

作者: LEO
邮箱: leoyfm@gmail.com
"""

from typing import Optional, List
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Query, File, UploadFile
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.api.dependencies.auth import get_current_user
from app.api.dependencies.database import get_db
from app.models.schemas.user import UserProfile
from app.models.schemas.transaction import (
    TransactionCreateRequest, TransactionUpdateRequest, TransactionStatusUpdateRequest,
    TransactionResponse, TransactionDetailResponse, TransactionStatistics,
    TransactionListQuery, TransactionImportRequest, TransactionImportResponse,
    TransactionBatchRequest, TransactionBatchResponse, TransactionAnalysisReport,
    TransactionCategorySuggestion, ExpenseBudget, ExpenseAlert,
    TransactionCategoryResponse, MonthlyTransactionStats
)
from app.models.schemas.common import ApiResponse, ApiPagedResponse, SuccessMessage
from app.services.transactions_service import TransactionsService
from app.utils.response import ResponseUtil

# 配置日志和路由
logger = get_logger(__name__)
router = APIRouter(
    prefix="/transactions",
    tags=["v1-用户-交易管理"]
)

@router.get(
    "/list",
    response_model=ApiPagedResponse[TransactionResponse],
    summary="获取我的交易列表",
    response_description="返回当前用户的交易列表"
)
async def get_my_transactions(
    page: int = Query(1, ge=1, description="页码，从1开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大100"),
    keyword: str = Query("", description="搜索关键词，支持交易描述、商户名称模糊搜索"),
    transaction_type: Optional[str] = Query(None, description="交易类型筛选：expense, income, transfer"),
    status: Optional[str] = Query(None, description="交易状态筛选：pending, completed, failed, refunded"),
    card_id: Optional[UUID] = Query(None, description="信用卡筛选"),
    category_id: Optional[UUID] = Query(None, description="交易分类筛选"),
    merchant_name: Optional[str] = Query(None, description="商户名称筛选"),
    currency: Optional[str] = Query(None, description="货币类型筛选：CNY, USD, HKD, EUR, JPY"),
    min_amount: Optional[float] = Query(None, ge=0, description="最小金额筛选"),
    max_amount: Optional[float] = Query(None, ge=0, description="最大金额筛选"),
    start_date: Optional[date] = Query(None, description="开始日期筛选"),
    end_date: Optional[date] = Query(None, description="结束日期筛选"),
    tags: Optional[str] = Query(None, description="标签筛选，多个标签用逗号分隔"),
    sort_by: str = Query("transaction_date", description="排序字段：transaction_date, amount, created_at"),
    sort_order: str = Query("desc", description="排序方向：asc, desc"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的交易列表
    
    支持丰富的筛选和排序功能：
    - 关键词模糊搜索（交易描述、商户名称）
    - 按交易类型、状态、卡片、分类筛选
    - 按金额范围、日期范围筛选
    - 按标签筛选（支持多标签）
    - 灵活的排序选项
    
    返回分页数据，包含完整的交易信息
    """
    try:
        logger.info("用户查询交易列表", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   page=page, 
                   page_size=page_size,
                   keyword=keyword)
        
        transactions_service = TransactionsService(db)
        
        # 构建查询参数
        tag_list = tags.split(",") if tags else []
        query_params = TransactionListQuery(
            keyword=keyword,
            transaction_type=transaction_type,
            status=status,
            card_id=card_id,
            category_id=category_id,
            merchant_name=merchant_name,
            currency=currency,
            min_amount=min_amount,
            max_amount=max_amount,
            start_date=start_date,
            end_date=end_date,
            tags=tag_list,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # 获取用户交易列表
        transactions, total = transactions_service.get_user_transactions_list(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            query_params=query_params
        )
        
        return ResponseUtil.paginated(
            items=transactions,
            total=total,
            page=page,
            page_size=page_size,
            message="获取交易列表成功"
        )
        
    except Exception as e:
        logger.error("获取交易列表异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取交易列表失败，请稍后重试")


@router.post(
    "/create",
    response_model=ApiResponse[TransactionResponse],
    summary="创建新交易",
    response_description="返回新创建的交易信息"
)
async def create_transaction(
    transaction_data: TransactionCreateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新的交易记录
    
    用户可以手动添加交易：
    - 支持支出、收入、转账等交易类型
    - 自动计算积分和返现奖励
    - 支持自定义标签和备注
    - 可选择交易分类，提供个性化分析
    
    系统会根据交易金额和卡片规则自动计算奖励
    """
    try:
        logger.info("用户创建交易", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   card_id=transaction_data.card_id,
                   amount=transaction_data.amount,
                   description=transaction_data.description)
        
        transactions_service = TransactionsService(db)
        
        # 验证信用卡归属
        card_belongs = transactions_service.verify_card_ownership(
            user_id=current_user.id,
            card_id=transaction_data.card_id
        )
        if not card_belongs:
            return ResponseUtil.validation_error("信用卡不存在或无权访问")
        
        # 创建交易
        new_transaction = transactions_service.create_user_transaction(
            user_id=current_user.id,
            transaction_data=transaction_data
        )
        
        if not new_transaction:
            return ResponseUtil.error("创建交易失败")
        
        logger.info("用户创建交易成功", 
                   user_id=current_user.id, 
                   transaction_id=new_transaction.id,
                   amount=new_transaction.amount)
        
        return ResponseUtil.created(
            data=new_transaction,
            message="交易创建成功"
        )
        
    except ValueError as e:
        logger.warning("创建交易参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("创建交易异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("创建交易失败，请稍后重试")


@router.get(
    "/{transaction_id}/details",
    response_model=ApiResponse[TransactionDetailResponse],
    summary="获取交易详情",
    response_description="返回指定交易的详细信息"
)
async def get_transaction_details(
    transaction_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取指定交易的详细信息
    
    包含完整的交易详情：
    - 交易基本信息和状态
    - 关联的分类和卡片信息
    - 积分和返现计算详情
    - 外币交易的汇率信息
    - 相关联的其他交易
    
    只能查看自己的交易详情
    """
    try:
        logger.info("用户查看交易详情", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   transaction_id=transaction_id)
        
        transactions_service = TransactionsService(db)
        
        # 获取交易详情
        transaction_detail = transactions_service.get_user_transaction_detail(
            user_id=current_user.id,
            transaction_id=transaction_id
        )
        
        if not transaction_detail:
            return ResponseUtil.not_found("交易不存在或无权访问")
        
        return ResponseUtil.success(
            data=transaction_detail,
            message="获取交易详情成功"
        )
        
    except Exception as e:
        logger.error("获取交易详情异常", error=str(e), user_id=current_user.id, transaction_id=transaction_id)
        return ResponseUtil.error("获取交易详情失败，请稍后重试")


@router.put(
    "/{transaction_id}/update",
    response_model=ApiResponse[TransactionResponse],
    summary="更新交易信息",
    response_description="返回更新后的交易信息"
)
async def update_transaction(
    transaction_id: UUID,
    transaction_data: TransactionUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新交易信息
    
    用户可以修改自己的交易：
    - 更新交易金额、描述、分类
    - 修改商户信息和地点
    - 调整标签和备注
    - 重新计算积分和返现
    
    系统会重新验证和计算相关奖励
    """
    try:
        logger.info("用户更新交易信息", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   transaction_id=transaction_id)
        
        transactions_service = TransactionsService(db)
        
        # 更新交易信息
        updated_transaction = transactions_service.update_user_transaction(
            user_id=current_user.id,
            transaction_id=transaction_id,
            transaction_data=transaction_data
        )
        
        if not updated_transaction:
            return ResponseUtil.not_found("交易不存在或无权访问")
        
        logger.info("用户更新交易成功", 
                   user_id=current_user.id, 
                   transaction_id=transaction_id)
        
        return ResponseUtil.success(
            data=updated_transaction,
            message="交易信息更新成功"
        )
        
    except ValueError as e:
        logger.warning("更新交易参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("更新交易异常", error=str(e), user_id=current_user.id, transaction_id=transaction_id)
        return ResponseUtil.error("更新交易失败，请稍后重试")


@router.put(
    "/{transaction_id}/status",
    response_model=ApiResponse[SuccessMessage],
    summary="更新交易状态",
    response_description="返回状态更新结果"
)
async def update_transaction_status(
    transaction_id: UUID,
    status_data: TransactionStatusUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新交易状态
    
    用户可以更改交易状态：
    - pending: 待处理状态
    - completed: 完成状态
    - failed: 失败状态  
    - refunded: 已退款状态
    
    状态变更会影响统计和奖励计算
    """
    try:
        logger.info("用户更新交易状态", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   transaction_id=transaction_id,
                   new_status=status_data.status,
                   reason=status_data.reason)
        
        transactions_service = TransactionsService(db)
        
        # 更新交易状态
        success = transactions_service.update_user_transaction_status(
            user_id=current_user.id,
            transaction_id=transaction_id,
            status=status_data.status,
            reason=status_data.reason
        )
        
        if not success:
            return ResponseUtil.not_found("交易不存在或无权访问")
        
        status_text = {
            "pending": "待处理",
            "completed": "已完成",
            "failed": "失败",
            "refunded": "已退款"
        }.get(status_data.status, "未知")
        
        logger.info("用户更新交易状态成功", 
                   user_id=current_user.id, 
                   transaction_id=transaction_id,
                   status=status_data.status)
        
        return ResponseUtil.success(
            data={"message": f"交易状态已更新为{status_text}", "timestamp": None},
            message=f"交易状态更新成功，已标记为{status_text}"
        )
        
    except ValueError as e:
        logger.warning("更新交易状态参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("更新交易状态异常", error=str(e), user_id=current_user.id, transaction_id=transaction_id)
        return ResponseUtil.error("更新交易状态失败，请稍后重试")


@router.delete(
    "/{transaction_id}/delete",
    response_model=ApiResponse[SuccessMessage],
    summary="删除交易",
    response_description="返回删除结果"
)
async def delete_transaction(
    transaction_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除交易记录
    
    用户可以删除自己的交易：
    - 删除后会重新计算相关统计
    - 删除操作不可逆转
    - 会影响积分和返现统计
    
    ⚠️ 注意：删除交易会影响历史统计数据
    """
    try:
        logger.warning("用户请求删除交易", 
                      user_id=current_user.id, 
                      username=current_user.username,
                      transaction_id=transaction_id)
        
        transactions_service = TransactionsService(db)
        
        # 删除交易
        success = transactions_service.delete_user_transaction(
            user_id=current_user.id,
            transaction_id=transaction_id
        )
        
        if not success:
            return ResponseUtil.not_found("交易不存在或无权访问")
        
        logger.warning("用户删除交易成功", 
                      user_id=current_user.id, 
                      transaction_id=transaction_id)
        
        return ResponseUtil.success(
            data={"message": "交易已删除", "timestamp": None},
            message="交易删除成功"
        )
        
    except Exception as e:
        logger.error("删除交易异常", error=str(e), user_id=current_user.id, transaction_id=transaction_id)
        return ResponseUtil.error("删除交易失败，请稍后重试")


@router.get(
    "/statistics",
    response_model=ApiResponse[TransactionStatistics],
    summary="获取我的交易统计",
    response_description="返回当前用户的交易统计数据"
)
async def get_my_transaction_statistics(
    start_date: Optional[date] = Query(None, description="统计开始日期"),
    end_date: Optional[date] = Query(None, description="统计结束日期"),
    card_id: Optional[UUID] = Query(None, description="指定信用卡筛选"),
    category_id: Optional[UUID] = Query(None, description="指定分类筛选"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的交易统计数据
    
    提供全面的交易分析：
    - 支出、收入、净额统计
    - 按分类、商户、卡片分组
    - 月度趋势分析
    - 积分和返现汇总
    - 货币分布统计
    
    支持按日期范围和卡片筛选
    """
    try:
        logger.info("用户查看交易统计", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   start_date=start_date,
                   end_date=end_date)
        
        transactions_service = TransactionsService(db)
        statistics = transactions_service.get_user_transaction_statistics(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            card_id=card_id,
            category_id=category_id
        )
        
        return ResponseUtil.success(
            data=statistics,
            message="获取交易统计成功"
        )
        
    except Exception as e:
        logger.error("获取交易统计异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取交易统计失败，请稍后重试")


@router.get(
    "/analysis",
    response_model=ApiResponse[TransactionAnalysisReport],
    summary="获取交易分析报告",
    response_description="返回详细的交易分析报告"
)
async def get_transaction_analysis(
    period: str = Query("current_month", description="分析期间：current_month, last_month, current_year, last_year, custom"),
    start_date: Optional[date] = Query(None, description="自定义开始日期（period=custom时必需）"),
    end_date: Optional[date] = Query(None, description="自定义结束日期（period=custom时必需）"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取详细的交易分析报告
    
    提供深度分析：
    - 期间统计和趋势对比
    - 消费习惯分析
    - 分类支出排名
    - 智能洞察和建议
    - 预算使用分析
    
    支持多种时间范围分析
    """
    try:
        logger.info("用户查看交易分析报告", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   period=period)
        
        transactions_service = TransactionsService(db)
        analysis_report = transactions_service.get_user_transaction_analysis(
            user_id=current_user.id,
            period=period,
            start_date=start_date,
            end_date=end_date
        )
        
        return ResponseUtil.success(
            data=analysis_report,
            message="获取交易分析报告成功"
        )
        
    except ValueError as e:
        logger.warning("获取交易分析参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("获取交易分析异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取交易分析失败，请稍后重试")


@router.get(
    "/categories",
    response_model=ApiResponse[List[TransactionCategoryResponse]],
    summary="获取交易分类列表",
    response_description="返回可用的交易分类列表"
)
async def get_transaction_categories(
    parent_id: Optional[UUID] = Query(None, description="父分类ID，为空返回顶级分类"),
    include_system: bool = Query(True, description="是否包含系统分类"),
    include_user: bool = Query(True, description="是否包含用户自定义分类"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取交易分类列表
    
    返回分层的分类结构：
    - 系统预设分类
    - 用户自定义分类
    - 支持父子级关系
    - 包含分类图标和颜色
    
    用于交易创建时的分类选择
    """
    try:
        logger.info("用户查询交易分类", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   parent_id=parent_id)
        
        transactions_service = TransactionsService(db)
        categories = transactions_service.get_user_transaction_categories(
            user_id=current_user.id,
            parent_id=parent_id,
            include_system=include_system,
            include_user=include_user
        )
        
        return ResponseUtil.success(
            data=categories,
            message="获取交易分类成功"
        )
        
    except Exception as e:
        logger.error("获取交易分类异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取交易分类失败，请稍后重试")


@router.post(
    "/import",
    response_model=ApiResponse[TransactionImportResponse],
    summary="批量导入交易",
    response_description="返回导入结果"
)
async def import_transactions(
    import_data: TransactionImportRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量导入交易记录
    
    支持批量导入功能：
    - 一次最多导入1000笔交易
    - 自动检测重复交易
    - 智能分类匹配
    - 详细的导入报告
    
    适用于银行账单批量导入
    """
    try:
        logger.info("用户批量导入交易", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   transaction_count=len(import_data.transactions))
        
        transactions_service = TransactionsService(db)
        
        # 执行批量导入
        import_result = transactions_service.import_user_transactions(
            user_id=current_user.id,
            import_data=import_data
        )
        
        logger.info("用户批量导入交易完成", 
                   user_id=current_user.id,
                   success_count=import_result.success_count,
                   failed_count=import_result.failed_count)
        
        return ResponseUtil.success(
            data=import_result,
            message=f"导入完成，成功{import_result.success_count}笔，失败{import_result.failed_count}笔"
        )
        
    except ValueError as e:
        logger.warning("批量导入交易参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("批量导入交易异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("批量导入交易失败，请稍后重试")


@router.post(
    "/batch",
    response_model=ApiResponse[TransactionBatchResponse],
    summary="批量操作交易",
    response_description="返回批量操作结果"
)
async def batch_update_transactions(
    batch_data: TransactionBatchRequest,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量操作交易
    
    支持多种批量操作：
    - 批量删除交易
    - 批量更新分类
    - 批量更新状态
    - 批量添加标签
    
    一次最多操作100笔交易
    """
    try:
        logger.info("用户批量操作交易", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   transaction_count=len(batch_data.transaction_ids),
                   operation=batch_data.operation)
        
        transactions_service = TransactionsService(db)
        
        # 执行批量操作
        batch_result = transactions_service.batch_update_user_transactions(
            user_id=current_user.id,
            batch_data=batch_data
        )
        
        logger.info("用户批量操作交易完成", 
                   user_id=current_user.id,
                   success_count=batch_result.success_count,
                   failed_count=batch_result.failed_count)
        
        return ResponseUtil.success(
            data=batch_result,
            message=f"批量操作完成，成功{batch_result.success_count}个，失败{batch_result.failed_count}个"
        )
        
    except ValueError as e:
        logger.warning("批量操作交易参数错误", error=str(e), user_id=current_user.id)
        return ResponseUtil.validation_error(str(e))
    except Exception as e:
        logger.error("批量操作交易异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("批量操作交易失败，请稍后重试")


@router.get(
    "/{transaction_id}/suggestions",
    response_model=ApiResponse[TransactionCategorySuggestion],
    summary="获取交易分类建议",
    response_description="返回智能分类建议"
)
async def get_transaction_suggestions(
    transaction_id: UUID,
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取交易智能分类建议
    
    基于机器学习提供分类建议：
    - 分析交易描述和商户信息
    - 参考历史分类习惯
    - 提供置信度评分
    - 支持一键应用建议
    
    帮助用户快速准确分类交易
    """
    try:
        logger.info("用户获取交易分类建议", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   transaction_id=transaction_id)
        
        transactions_service = TransactionsService(db)
        
        # 获取分类建议
        suggestions = transactions_service.get_transaction_category_suggestions(
            user_id=current_user.id,
            transaction_id=transaction_id
        )
        
        if not suggestions:
            return ResponseUtil.not_found("交易不存在或无权访问")
        
        return ResponseUtil.success(
            data=suggestions,
            message="获取分类建议成功"
        )
        
    except Exception as e:
        logger.error("获取交易分类建议异常", error=str(e), user_id=current_user.id, transaction_id=transaction_id)
        return ResponseUtil.error("获取分类建议失败，请稍后重试")


@router.get(
    "/budgets",
    response_model=ApiResponse[List[ExpenseBudget]],
    summary="获取支出预算",
    response_description="返回当前用户的支出预算信息"
)
async def get_expense_budgets(
    period_type: str = Query("monthly", description="预算周期：monthly, yearly"),
    period_value: Optional[str] = Query(None, description="周期值，如'2024-12'，默认当前周期"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取支出预算信息
    
    显示预算执行情况：
    - 总预算和分类预算
    - 已用金额和剩余金额
    - 使用百分比和超支提醒
    - 按月度或年度周期统计
    
    帮助用户控制支出和预算管理
    """
    try:
        logger.info("用户查看支出预算", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   period_type=period_type,
                   period_value=period_value)
        
        transactions_service = TransactionsService(db)
        budgets = transactions_service.get_user_expense_budgets(
            user_id=current_user.id,
            period_type=period_type,
            period_value=period_value
        )
        
        return ResponseUtil.success(
            data=budgets,
            message="获取支出预算成功"
        )
        
    except Exception as e:
        logger.error("获取支出预算异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取支出预算失败，请稍后重试")


@router.get(
    "/alerts",
    response_model=ApiResponse[List[ExpenseAlert]],
    summary="获取支出预警",
    response_description="返回当前用户的支出预警信息"
)
async def get_expense_alerts(
    severity: Optional[str] = Query(None, description="预警级别筛选：low, medium, high"),
    unread_only: bool = Query(False, description="是否仅显示未读预警"),
    current_user: UserProfile = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取支出预警信息
    
    提供智能预警：
    - 预算超支预警
    - 异常消费预警
    - 分类支出异常预警
    - 按严重程度分级
    
    帮助用户及时发现和控制支出异常
    """
    try:
        logger.info("用户查看支出预警", 
                   user_id=current_user.id, 
                   username=current_user.username,
                   severity=severity,
                   unread_only=unread_only)
        
        transactions_service = TransactionsService(db)
        alerts = transactions_service.get_user_expense_alerts(
            user_id=current_user.id,
            severity=severity,
            unread_only=unread_only
        )
        
        return ResponseUtil.success(
            data=alerts,
            message="获取支出预警成功"
        )
        
    except Exception as e:
        logger.error("获取支出预警异常", error=str(e), user_id=current_user.id)
        return ResponseUtil.error("获取支出预警失败，请稍后重试") 