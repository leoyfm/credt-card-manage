"""
分页工具模块

提供数据库查询分页功能
"""

from typing import Tuple, List, Any
from sqlalchemy.orm import Query


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
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 20
    if page_size > 100:
        page_size = 100
    
    # 获取总记录数
    total = query.count()
    
    # 计算偏移量
    offset = (page - 1) * page_size
    
    # 获取分页数据
    items = query.offset(offset).limit(page_size).all()
    
    return items, total


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