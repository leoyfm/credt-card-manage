"""
分页工具模块

提供数据库查询分页功能
"""

from typing import Tuple, List, Any, Dict
from sqlalchemy.orm import Query


def validate_pagination_params(page: int, page_size: int, max_page_size: int = 100) -> Tuple[int, int]:
    """
    验证并修正分页参数
    
    Args:
        page: 页码
        page_size: 每页大小
        max_page_size: 最大每页大小
        
    Returns:
        Tuple[int, int]: (修正后的页码, 修正后的每页大小)
    """
    # 修正页码
    if page < 1:
        page = 1
    
    # 修正每页大小
    if page_size < 1:
        page_size = 20
    elif page_size > max_page_size:
        page_size = max_page_size
    
    return page, page_size


def calculate_skip(page: int, page_size: int) -> int:
    """
    计算分页偏移量
    
    Args:
        page: 页码（从1开始）
        page_size: 每页大小
        
    Returns:
        int: 偏移量
    """
    return (page - 1) * page_size


def calculate_pagination_info(total: int, page: int, page_size: int) -> Dict[str, Any]:
    """
    计算分页信息
    
    Args:
        total: 总记录数
        page: 当前页码
        page_size: 每页大小
        
    Returns:
        Dict[str, Any]: 分页信息字典
    """
    # 验证参数
    page, page_size = validate_pagination_params(page, page_size)
    
    # 计算总页数
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    
    # 计算是否有上一页/下一页
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "current_page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev
    }


def paginate(query: Query, page: int, page_size: int) -> Tuple[List[Any], int]:
    """
    对SQLAlchemy查询进行分页处理
    
    Args:
        query: SQLAlchemy查询对象
        page: 页码（从1开始）
        page_size: 每页大小
        
    Returns:
        Tuple[List[Any], int]: (分页数据列表, 总记录数)
    """
    # 验证分页参数
    page, page_size = validate_pagination_params(page, page_size)
    
    # 获取总记录数
    total = query.count()
    
    # 计算偏移量
    offset = calculate_skip(page, page_size)
    
    # 获取分页数据
    items = query.offset(offset).limit(page_size).all()
    
    return items, total


def paginate_with_info(query: Query, page: int, page_size: int) -> Tuple[List[Any], Dict[str, Any]]:
    """
    对SQLAlchemy查询进行分页并返回完整分页信息
    
    Args:
        query: SQLAlchemy查询对象
        page: 页码（从1开始）
        page_size: 每页大小
        
    Returns:
        Tuple[List[Any], Dict[str, Any]]: (分页结果列表, 分页信息字典)
    """
    items, total = paginate(query, page, page_size)
    page, page_size = validate_pagination_params(page, page_size)
    pagination_info = calculate_pagination_info(total, page, page_size)
    
    return items, pagination_info


def apply_service_pagination(
    query: Query, 
    page: int, 
    page_size: int,
    order_by=None
) -> Tuple[List[Any], int]:
    """
    服务层统一分页方法
    
    Args:
        query: SQLAlchemy查询对象
        page: 页码（从1开始）
        page_size: 每页大小
        order_by: 排序字段（可选，支持单个字段或字段列表）
        
    Returns:
        Tuple[List[Any], int]: (分页结果列表, 总记录数)
    """
    # 验证分页参数
    page, page_size = validate_pagination_params(page, page_size)
    
    # 应用排序
    if order_by is not None:
        if isinstance(order_by, list):
            query = query.order_by(*order_by)
        else:
            query = query.order_by(order_by)
    
    # 获取总数
    total = query.count()
    
    # 计算偏移量并执行分页查询
    skip = calculate_skip(page, page_size)
    items = query.offset(skip).limit(page_size).all()
    
    return items, total 