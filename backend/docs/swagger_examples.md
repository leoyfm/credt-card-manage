# Swagger 文档示例说明

## 概述

本文档说明了信用卡管理系统API的Swagger文档特性和示例内容。

## 文档特性

### 🎯 自动分组
- **系统**：基础接口，健康检查、状态监控
- **年费管理**：年费规则、记录管理、减免检查
- **信用卡**：卡片管理、额度监控、状态管理
- **还款提醒**：提醒设置、通知管理、账单提醒
- **智能推荐**：个性化推荐、用户画像、反馈收集

### 📝 完整字段说明
所有模型字段都包含：
- **description**：详细的中文字段说明
- **example**：实际的示例值
- **validation**：数据验证规则（长度、范围等）

### 🔧 统一响应格式
- 成功响应：`ApiResponse<T>`
- 分页响应：`ApiPagedResponse<T>`
- 错误处理：统一的错误响应格式

## 模型示例

### 年费规则创建请求
```json
{
  "rule_name": "刷卡次数减免-标准",
  "fee_type": "transaction_count",
  "base_fee": 200.00,
  "waiver_condition_value": 12,
  "waiver_period_months": 12,
  "description": "年内刷卡满12次可减免年费"
}
```

### 年费规则响应
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
    "waiver_period_months": 12,
    "description": "年内刷卡满12次可减免年费",
    "created_at": "2024-01-15T10:30:00.000Z"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 分页列表响应
```json
{
  "success": true,
  "code": 200,
  "message": "获取年费规则列表成功",
  "data": {
    "items": [
      {
        "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
        "rule_name": "刷卡次数减免-标准",
        "fee_type": "transaction_count",
        "base_fee": 200.00
      }
    ],
    "pagination": {
      "total": 150,
      "page": 1,
      "size": 20,
      "pages": 8
    }
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## 接口分组说明

### 年费管理接口
- `POST /api/annual-fees/rules` - 创建年费规则
- `GET /api/annual-fees/rules` - 获取年费规则列表（支持搜索、分页）
- `GET /api/annual-fees/rules/{rule_id}` - 获取年费规则详情
- `PUT /api/annual-fees/rules/{rule_id}` - 更新年费规则
- `DELETE /api/annual-fees/rules/{rule_id}` - 删除年费规则

### 信用卡管理接口
- `GET /api/cards` - 获取信用卡列表（支持搜索、分页）
- `POST /api/cards` - 创建信用卡
- `GET /api/cards/{card_id}` - 获取信用卡详情
- `PUT /api/cards/{card_id}` - 更新信用卡信息
- `DELETE /api/cards/{card_id}` - 删除信用卡

### 还款提醒接口
- `GET /api/reminders` - 获取还款提醒列表（支持搜索、分页）
- `POST /api/reminders` - 创建还款提醒
- `GET /api/reminders/{reminder_id}` - 获取提醒详情
- `PUT /api/reminders/{reminder_id}` - 更新提醒信息
- `DELETE /api/reminders/{reminder_id}` - 删除提醒

### 智能推荐接口
- `GET /api/recommendations` - 获取推荐列表（支持搜索、分页）
- `GET /api/recommendations/{recommendation_id}` - 获取推荐详情
- `POST /api/recommendations/generate` - 生成个性化推荐
- `PUT /api/recommendations/{recommendation_id}/feedback` - 提交推荐反馈

## 搜索功能

所有列表接口都支持 `keyword` 参数进行模糊搜索：
- 年费规则：搜索规则名称、描述
- 年费记录：搜索卡片名称、银行名称
- 信用卡：搜索银行名称、卡片名称
- 还款提醒：搜索卡片名称、银行名称
- 智能推荐：搜索银行名称、卡片类型

## 分页参数

所有列表接口统一使用以下分页参数：
- `page`：页码，从1开始，默认1
- `page_size`：每页数量，默认20，最大100

## 访问文档

启动后端服务后，可通过以下地址访问文档：
- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc 