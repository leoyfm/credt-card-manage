 # API 统一响应格式文档

## 概述

本文档描述了信用卡管理系统后端API的统一响应格式，确保所有接口返回一致的数据结构。

## 响应格式结构

### 基础响应格式

```json
{
    "success": true,
    "code": 200,
    "message": "操作成功",
    "data": null,
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 分页参数规范

所有列表型接口统一使用以下分页参数：

| 参数 | 类型 | 默认值 | 范围 | 说明 |
|------|------|--------|------|------|
| page | integer | 1 | ≥1 | 页码，从1开始 |
| page_size | integer | 20 | 1-100 | 每页数量，最大100 |

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| success | boolean | 请求是否成功，true表示成功，false表示失败 |
| code | integer | HTTP状态码 |
| message | string | 响应消息，用于描述操作结果 |
| data | any | 实际数据，根据接口不同而变化 |
| timestamp | string | 响应时间戳，ISO 8601格式 |

### 分页响应格式

对于需要分页的接口，使用以下格式：

```json
{
    "success": true,
    "code": 200,
    "message": "获取成功",
    "data": {
        "items": [],
        "pagination": {
            "total": 100,
            "page": 1,
            "size": 20,
            "pages": 5
        }
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 响应示例

### 1. 成功响应

#### 创建成功 (201)
```json
{
    "success": true,
    "code": 201,
    "message": "年费规则创建成功",
    "data": {
        "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "rule_name": "刷卡次数减免-标准",
        "fee_type": "transaction_count",
        "base_fee": 200.00,
        "waiver_condition_value": 12,
        "created_at": "2024-01-15T10:30:00.000Z"
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 查询成功 (200)
```json
{
    "success": true,
    "code": 200,
    "message": "获取年费规则列表成功",
    "data": [
        {
            "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "rule_name": "刷卡次数减免-标准",
            "fee_type": "transaction_count",
            "base_fee": 200.00
        }
    ],
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 删除成功 (204)
```json
{
    "success": true,
    "code": 204,
    "message": "年费规则删除成功",
    "data": null,
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 2. 错误响应

#### 资源不存在 (404)
```json
{
    "success": false,
    "code": 404,
    "message": "年费规则不存在",
    "data": null,
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 参数验证错误 (422)
```json
{
    "success": false,
    "code": 422,
    "message": "参数验证失败",
    "data": null,
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

#### 服务器错误 (500)
```json
{
    "success": false,
    "code": 500,
    "message": "服务器内部错误",
    "data": null,
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 3. 批量操作响应

```json
{
    "success": true,
    "code": 200,
    "message": "批量创建完成：成功3个，失败1个",
    "data": {
        "success_count": 3,
        "error_count": 1,
        "results": [
            {
                "card_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "record_id": "a1b2c3d4-5e6f-7890-abcd-ef1234567890"
            }
        ],
        "errors": [
            {
                "card_id": "12345678-1234-1234-1234-123456789012",
                "error": "信用卡不存在"
            }
        ]
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 响应工具类

### ResponseUtil 方法

| 方法 | 说明 | HTTP状态码 |
|------|------|-----------|
| success() | 成功响应 | 200 |
| created() | 创建成功响应 | 201 |
| deleted() | 删除成功响应 | 204 |
| error() | 通用错误响应 | 400 |
| not_found() | 资源不存在 | 404 |
| unauthorized() | 未授权 | 401 |
| forbidden() | 禁止访问 | 403 |
| validation_error() | 参数验证失败 | 422 |
| server_error() | 服务器错误 | 500 |
| paginated() | 分页响应 | 200 |

### 使用示例

```python
from utils.response import ResponseUtil

# 成功响应
return ResponseUtil.success(
    data=user_data,
    message="用户信息获取成功"
)

# 错误响应
return ResponseUtil.error(
    message="用户名或密码错误",
    code=401
)

# 分页响应
return ResponseUtil.paginated(
    items=users,
    total=100,
    page=1,
    page_size=20,
    message="用户列表获取成功"
)

# 计算跳过的记录数
skip = ResponseUtil.calculate_skip(page, page_size)
```

## 分页接口调用示例

### 基本调用
```bash
# 获取第1页，每页20条记录（默认值）
GET /api/annual-fees/rules

# 获取第2页，每页10条记录
GET /api/annual-fees/rules?page=2&page_size=10

# 带筛选条件的分页
GET /api/annual-fees/rules?page=1&page_size=20&fee_type=transaction_count
```

## 前端处理

### JavaScript/TypeScript 示例

```typescript
interface ApiResponse<T> {
    success: boolean;
    code: number;
    message: string;
    data: T | null;
    timestamp: string;
}

interface ApiPagedResponse<T> {
    success: boolean;
    code: number;
    message: string;
    data: {
        items: T[];
        pagination: {
            total: number;
            page: number;
            size: number;
            pages: number;
        };
    } | null;
    timestamp: string;
}

// 分页数据请求处理
async function fetchPagedData<T>(url: string, page: number = 1, pageSize: number = 20): Promise<{items: T[], pagination: any}> {
    const response = await fetch(`${url}?page=${page}&page_size=${pageSize}`);
    const result: ApiPagedResponse<T> = await response.json();
    
    if (result.success && result.data) {
        return result.data;
    } else {
        throw new Error(result.message);
    }
}

// 使用示例
try {
    const {items: rules, pagination} = await fetchPagedData<AnnualFeeRule>('/api/annual-fees/rules', 1, 20);
    console.log('年费规则:', rules);
    console.log('分页信息:', pagination);
} catch (error) {
    console.error('获取失败:', error.message);
}
```

## 优势

### 1. 一致性
- 所有API接口返回相同的数据结构
- 前端可以统一处理响应

### 2. 可读性
- 明确的成功/失败标识
- 详细的错误消息
- 标准的HTTP状态码

### 3. 可维护性
- 使用统一的响应工具类
- 便于后续扩展和修改

### 4. 开发效率
- 前端开发者无需关心不同接口的响应格式差异
- 减少调试时间

## 注意事项

1. **timestamp 字段**：始终使用ISO 8601格式的UTC时间
2. **message 字段**：提供清晰、有意义的消息，支持国际化
3. **data 字段**：可以是任意类型，包括null、对象、数组等
4. **分页信息**：统一使用pagination对象包装分页信息
5. **错误处理**：优先返回具体的错误响应而不是抛出异常

## 迁移指南

### 现有API迁移

1. 导入响应工具类：
```python
from utils.response import ResponseUtil
from models.response import ApiResponse
```

2. 更新路由装饰器：
```python
@router.get("/items", response_model=ApiResponse[List[Item]])
```

3. 修改返回语句：
```python
# 修改前
return items

# 修改后
return ResponseUtil.success(data=items, message="获取成功")
```

4. 统一错误处理：
```python
# 修改前
raise HTTPException(status_code=404, detail="资源不存在")

# 修改后
return ResponseUtil.not_found(message="资源不存在")
```