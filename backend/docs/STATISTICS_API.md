# 统计分析接口文档

## 概述

信用卡管理系统的统计分析模块提供了全面的数据统计和分析功能，帮助用户了解信用卡使用情况、消费模式和财务状况。

## 功能特性

### 🎯 核心统计功能

1. **统计概览** - 一站式获取所有关键统计数据
2. **信用卡统计** - 信用卡数量和状态分布分析
3. **信用额度统计** - 额度使用情况和利用率分析
4. **交易统计** - 交易笔数、金额和积分统计
5. **年费统计** - 年费缴费情况和减免统计
6. **消费分类统计** - 按消费类别的支出分析
7. **月度趋势** - 按月份的交易趋势分析
8. **银行分布统计** - 各银行信用卡分布和使用情况

### 🔍 高级筛选功能

- **时间范围筛选** - 支持自定义开始和结束日期
- **银行筛选** - 按银行名称筛选统计数据
- **信用卡筛选** - 按特定信用卡ID筛选
- **状态筛选** - 是否包含已注销的信用卡

## API接口列表

### 1. 统计概览
```
GET /api/statistics/overview
```
**功能**: 获取包括信用卡、额度、交易、年费等全方位的统计数据

**查询参数**:
- `start_date` (可选): 开始日期，格式：YYYY-MM-DD
- `end_date` (可选): 结束日期，格式：YYYY-MM-DD
- `bank_name` (可选): 银行名称筛选
- `card_id` (可选): 信用卡ID筛选
- `include_cancelled` (可选): 是否包含已注销的信用卡，默认false

**响应数据**:
```json
{
  "success": true,
  "data": {
    "card_stats": { /* 信用卡统计 */ },
    "credit_stats": { /* 信用额度统计 */ },
    "transaction_stats": { /* 交易统计 */ },
    "annual_fee_stats": { /* 年费统计 */ },
    "top_categories": [ /* 消费分类TOP */ ],
    "monthly_trends": [ /* 月度趋势 */ ],
    "bank_distribution": [ /* 银行分布 */ ]
  }
}
```

### 2. 信用卡统计
```
GET /api/statistics/cards
```
**功能**: 获取信用卡数量及状态分布统计

**统计指标**:
- 总卡数
- 激活卡数
- 未激活卡数
- 冻结卡数
- 已注销卡数
- 过期卡数
- 即将过期卡数（未来3个月内）

### 3. 信用额度统计
```
GET /api/statistics/credit-limit
```
**功能**: 获取信用额度使用情况及利用率统计

**统计指标**:
- 总信用额度
- 已使用金额
- 可用金额
- 整体利用率
- 最高利用率
- 最低利用率
- 平均利用率

### 4. 交易统计
```
GET /api/statistics/transactions
```
**功能**: 获取交易笔数、金额及积分统计

**统计指标**:
- 总交易笔数
- 总消费金额
- 总还款金额
- 总积分收入
- 本月交易统计
- 平均交易金额

### 5. 年费统计
```
GET /api/statistics/annual-fee
```
**功能**: 获取年费缴费情况及减免统计

**统计指标**:
- 年费总额
- 减免次数
- 待缴费次数
- 已缴费次数
- 逾期次数
- 本年度应缴费用
- 减免节省金额

### 6. 消费分类统计
```
GET /api/statistics/categories
```
**功能**: 获取按消费类别统计的支出分布

**查询参数**:
- `limit` (可选): 返回前N个分类，默认10，最大20

**支持的消费分类**:
- 餐饮美食 (dining)
- 购物消费 (shopping)
- 交通出行 (transportation)
- 娱乐休闲 (entertainment)
- 医疗健康 (healthcare)
- 教育培训 (education)
- 旅游度假 (travel)
- 生活缴费 (utilities)
- 其他消费 (other)

### 7. 月度趋势
```
GET /api/statistics/monthly-trends
```
**功能**: 获取按月统计的交易趋势数据

**统计指标**:
- 年月(YYYY-MM格式)
- 交易笔数
- 消费金额
- 还款金额
- 积分收入

**默认**: 返回最近12个月的数据

### 8. 银行分布统计
```
GET /api/statistics/banks
```
**功能**: 获取按银行统计的信用卡分布和使用情况

**统计指标**:
- 银行名称
- 信用卡数量
- 总信用额度
- 已使用金额
- 利用率

## 技术实现

### 架构设计

```
routers/statistics.py     # 路由层 - HTTP请求处理
    ↓
services/statistics.py    # 服务层 - 业务逻辑处理
    ↓
db_models/               # 数据模型层 - 数据库操作
```

### 核心特性

1. **统一响应格式** - 所有接口使用标准的ApiResponse格式
2. **完整的认证** - 所有接口都需要JWT认证
3. **灵活的筛选** - 支持多维度的数据筛选
4. **高性能查询** - 使用SQLAlchemy优化的聚合查询
5. **详细的日志** - 完整的操作日志记录
6. **错误处理** - 完善的异常处理和错误返回

### 数据模型

**统计查询参数模型** (`DetailedStatisticsQuery`):
```python
class DetailedStatisticsQuery(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bank_name: Optional[str] = None
    card_id: Optional[str] = None
    include_cancelled: bool = False
```

**统计响应模型**:
- `OverallStatistics` - 总体统计
- `CardStatistics` - 信用卡统计
- `CreditLimitStatistics` - 信用额度统计
- `TransactionStatistics` - 交易统计
- `AnnualFeeStatistics` - 年费统计
- `CategoryStatistics` - 分类统计
- `MonthlyStatistics` - 月度统计
- `BankStatistics` - 银行统计

## 使用示例

### 获取统计概览
```bash
curl -X GET "http://localhost:8000/api/statistics/overview" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 获取特定银行的信用卡统计
```bash
curl -X GET "http://localhost:8000/api/statistics/cards?bank_name=招商银行" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 获取指定时间范围的交易统计
```bash
curl -X GET "http://localhost:8000/api/statistics/transactions?start_date=2024-01-01&end_date=2024-06-30" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### 获取消费分类TOP5
```bash
curl -X GET "http://localhost:8000/api/statistics/categories?limit=5" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 测试

### 自动化测试
```bash
# 运行统计接口测试套件
python -m pytest tests/test_statistics.py -v
```

### 手动测试
```bash
# 运行手动测试脚本
python test_statistics_manual.py
```

**测试覆盖**:
- ✅ 17个自动化测试用例
- ✅ 8个手动测试场景
- ✅ 完整的功能覆盖
- ✅ 错误场景测试
- ✅ 数据一致性验证

## 性能优化

1. **数据库查询优化** - 使用聚合查询减少数据传输
2. **索引优化** - 在关键字段上建立索引
3. **缓存策略** - 可考虑对统计数据进行缓存
4. **分页支持** - 大数据量时支持分页查询

## 扩展功能

### 未来可扩展的功能

1. **实时统计** - WebSocket推送实时统计更新
2. **导出功能** - 支持Excel/PDF格式导出
3. **图表数据** - 提供图表渲染所需的数据格式
4. **对比分析** - 同期对比、环比分析
5. **预测分析** - 基于历史数据的趋势预测
6. **自定义报表** - 用户自定义统计维度和指标

## 注意事项

1. **数据权限** - 所有统计数据都基于当前用户的数据
2. **时区处理** - 统一使用东八区时间
3. **数据精度** - 金额使用Decimal类型保证精度
4. **性能考虑** - 大数据量时建议使用时间范围筛选
5. **缓存策略** - 统计数据可考虑适当缓存以提高性能

---

**版本**: v1.0.0  
**更新时间**: 2024-06-09  
**维护者**: LEO (leoyfm@gmail.com) 