"""
分页工具函数
"""
from typing import Dict, Any
import math


def get_pagination_info(page: int, page_size: int, total: int) -> Dict[str, Any]:
    """
    计算分页信息
    
    Args:
        page: 当前页码
        page_size: 每页大小
        total: 总记录数
        
    Returns:
        Dict[str, Any]: 分页信息
    """
    # 计算总页数
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    # 确保当前页码在有效范围内
    current_page = max(1, min(page, total_pages))
    
    # 计算偏移量
    skip = (current_page - 1) * page_size
    
    # 是否有上一页/下一页
    has_prev = current_page > 1
    has_next = current_page < total_pages
    
    # 上一页/下一页页码
    prev_page = current_page - 1 if has_prev else None
    next_page = current_page + 1 if has_next else None
    
    return {
        "page": current_page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_prev": has_prev,
        "has_next": has_next,
        "prev_page": prev_page,
        "next_page": next_page,
        "skip": skip
    }


def calculate_skip(page: int, page_size: int) -> int:
    """
    计算查询偏移量
    
    Args:
        page: 页码
        page_size: 每页大小
        
    Returns:
        int: 偏移量
    """
    return (page - 1) * page_size 