# 异常处理指南

## 概述

本项目采用统一的异常管理系统，所有API接口都应该使用自定义异常类，而不是直接使用FastAPI的`HTTPException`。

## 为什么不使用HTTPException

1. **缺乏统一性**: `HTTPException`没有统一的错误格式和错误码
2. **难以维护**: 错误信息分散在各个文件中，难以统一管理
3. **缺乏日志**: 没有自动的错误日志记录
4. **不利于监控**: 无法进行统一的错误监控和告警

## 自定义异常系统的优势

1. **统一格式**: 所有错误响应都有统一的JSON格式
2. **自动日志**: 异常抛出时自动记录日志
3. **错误码管理**: 统一的错误码便于前端处理
4. **监控友好**: 便于错误监控和告警

## 异常类层次结构

```python
APIException (基础异常类)
├── AuthenticationError (认证失败)
├── AuthorizationError (权限不足)
├── ValidationError (数据验证失败)
├── BusinessRuleError (业务规则违反)
├── ResourceNotFoundError (资源不存在)
├── ResourceConflictError (资源冲突)
├── DatabaseError (数据库错误)
├── ExternalServiceError (外部服务错误)
└── RateLimitError (请求限流)
```

## 使用示例

### ❌ 错误的做法 (使用HTTPException)

```python
from fastapi import HTTPException, status

@router.get("/recommendations/{recommendation_id}")
async def get_recommendation(recommendation_id: UUID):
    try:
        recommendation = service.get_recommendation(recommendation_id)
        if not recommendation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="推荐记录不存在"
            )
        return recommendation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取推荐失败: {str(e)}"
        )
```

### ✅ 正确的做法 (使用自定义异常)

```python
from app.core.exceptions import ResourceNotFoundError, DatabaseError

@router.get("/recommendations/{recommendation_id}")
async def get_recommendation(recommendation_id: UUID):
    try:
        recommendation = service.get_recommendation(recommendation_id)
        if not recommendation:
            raise ResourceNotFoundError(
                message="推荐记录不存在",
                error_detail=f"推荐ID: {recommendation_id}"
            )
        return recommendation
    except (ResourceNotFoundError, BusinessRuleError):
        raise  # 重新抛出业务异常
    except Exception as e:
        raise DatabaseError(
            message="获取推荐失败",
            error_detail=str(e)
        )
```

## 异常处理最佳实践

### 1. 导入异常类

```python
# 推荐的导入方式
from app.core.exceptions import (
    ResourceNotFoundError,
    DatabaseError,
    BusinessRuleError,
    ValidationError
)
```

### 2. 异常捕获顺序

```python
try:
    # 业务逻辑
    pass
except (ResourceNotFoundError, ValidationError, BusinessRuleError):
    # 重新抛出已知的业务异常
    raise
except Exception as e:
    # 捕获未知异常，转换为系统异常
    raise DatabaseError(
        message="操作失败",
        error_detail=str(e)
    )
```

### 3. 异常信息设计

```python
# 好的异常信息
raise ResourceNotFoundError(
    message="用户不存在",  # 用户友好的错误描述
    error_detail=f"用户ID: {user_id}"  # 技术细节，便于调试
)

# 避免的异常信息
raise ResourceNotFoundError("用户不存在")  # 缺少技术细节
```

### 4. 业务逻辑验证

```python
# 资源存在性检查
if not user:
    raise ResourceNotFoundError(
        message="用户不存在",
        error_detail=f"用户ID: {user_id}"
    )

# 权限检查
if user.id != current_user.id and not current_user.is_admin:
    raise AuthorizationError(
        message="权限不足",
        error_detail="只能访问自己的资源"
    )

# 业务规则检查
if card.status == "closed":
    raise BusinessRuleError(
        message="无法操作已关闭的信用卡",
        error_detail=f"卡片状态: {card.status}"
    )
```

## 错误响应格式

使用自定义异常后，所有错误响应都会有统一的格式：

```json
{
    "success": false,
    "code": 404,
    "message": "推荐记录不存在",
    "error_detail": "推荐ID: 123e4567-e89b-12d3-a456-426614174000",
    "error_code": "RESOURCE_NOT_FOUND",
    "timestamp": "2024-12-01T10:00:00Z"
}
```

## 迁移指南

如果现有代码使用了`HTTPException`，请按以下步骤迁移：

1. **移除HTTPException导入**
   ```python
   # 删除
   from fastapi import HTTPException, status
   
   # 添加
   from app.core.exceptions import ResourceNotFoundError, DatabaseError
   ```

2. **替换异常抛出**
   ```python
   # 替换前
   raise HTTPException(status_code=404, detail="资源不存在")
   
   # 替换后
   raise ResourceNotFoundError(message="资源不存在")
   ```

3. **更新异常捕获**
   ```python
   # 替换前
   except HTTPException:
       raise
   
   # 替换后
   except (ResourceNotFoundError, BusinessRuleError):
       raise
   ```

## 常见异常使用场景

| 异常类 | 使用场景 | HTTP状态码 |
|--------|----------|------------|
| `ResourceNotFoundError` | 资源不存在 | 404 |
| `ValidationError` | 数据验证失败 | 422 |
| `BusinessRuleError` | 业务规则违反 | 400 |
| `AuthorizationError` | 权限不足 | 403 |
| `AuthenticationError` | 认证失败 | 401 |
| `ResourceConflictError` | 资源冲突 | 409 |
| `DatabaseError` | 数据库错误 | 500 |
| `ExternalServiceError` | 外部服务错误 | 503 |
| `RateLimitError` | 请求限流 | 429 |

---

**注意**: 所有新的API接口都必须使用自定义异常系统，现有接口也应该逐步迁移。 