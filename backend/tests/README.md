# 交易接口测试说明

本目录包含了信用卡管理系统交易接口的完整测试套件。

## 测试结构

```
tests/
├── __init__.py           # 测试包初始化
├── conftest.py          # pytest配置和fixture
├── test_transactions.py # 交易接口测试
└── README.md           # 本说明文档
```

## 测试环境准备

### 1. 安装测试依赖

```bash
pip install pytest httpx pytest-asyncio pytest-cov pytest-html
```

### 2. 设置测试数据库

确保PostgreSQL已启动，并创建测试数据库：

```sql
CREATE DATABASE credit_card_manage_test;
```

### 3. 环境变量配置

测试会自动使用以下测试环境配置：
- 数据库: `postgresql://postgres:password@localhost:5432/credit_card_manage_test`
- DEBUG模式: `true`
- JWT密钥: `test-secret-key`

## 运行测试

### 基本运行

```bash
# 运行所有测试
python run_tests.py

# 或者直接使用pytest
python -m pytest tests/

# 运行特定测试文件
python run_tests.py tests/test_transactions.py
```

### 详细选项

```bash
# 详细输出
python run_tests.py -v

# 运行特定测试类
python run_tests.py -k "TestTransactionCRUD"

# 运行特定测试方法
python run_tests.py -k "test_create_transaction_success"

# 按标记筛选测试
python run_tests.py -m "crud"

# 生成覆盖率报告
python run_tests.py --cov

# 生成HTML报告
python run_tests.py --html
```

## 测试覆盖范围

### TestTransactionCRUD 类
- ✅ 创建交易记录成功
- ✅ 创建交易记录时信用卡ID无效
- ✅ 创建交易记录时缺少必填字段
- ✅ 创建交易记录时金额无效
- ✅ 获取交易记录列表
- ✅ 带筛选条件的交易记录列表
- ✅ 关键词搜索交易记录
- ✅ 获取交易记录详情
- ✅ 获取不存在的交易记录
- ✅ 更新交易记录
- ✅ 更新不存在的交易记录
- ✅ 删除交易记录
- ✅ 删除不存在的交易记录

### TestTransactionStatistics 类
- ✅ 获取交易统计概览
- ✅ 获取分类消费统计
- ✅ 获取月度交易趋势

### TestTransactionAuth 类
- ✅ 未认证时的各种操作权限测试
- ✅ 统计接口权限测试

### TestTransactionEdgeCases 类
- ✅ 分期交易记录测试
- ✅ 大金额交易记录测试
- ✅ 分页功能测试
- ✅ 带时间范围的统计测试

## 测试数据

测试使用以下fixture提供测试数据：

### test_user_data
随机生成的测试用户数据，包含用户名、邮箱、密码等。

### test_card_data
测试信用卡数据：
- 卡名: 测试信用卡
- 银行: 测试银行
- 额度: 50,000元
- 有效期: 2027年12月

### test_transaction_data
测试交易数据：
- 类型: 消费交易
- 金额: 199.50元
- 商户: 星巴克咖啡
- 分类: 餐饮美食

## 辅助函数

### create_test_transaction()
便捷创建测试交易记录的函数。

### assert_response_success()
断言API响应成功的函数。

### assert_response_error()
断言API响应错误的函数。

## 注意事项

1. **数据库隔离**: 每个测试都在独立的事务中运行，测试结束后自动回滚。

2. **认证处理**: `authenticated_user` fixture自动处理用户注册、登录和token获取。

3. **测试顺序**: 测试之间相互独立，可以任意顺序运行。

4. **环境配置**: 测试使用独立的测试数据库，不会影响开发环境数据。

## 扩展测试

要添加新的测试：

1. 在相应的测试类中添加新的测试方法
2. 使用描述性的方法名，以`test_`开头
3. 添加详细的docstring说明测试目的
4. 使用合适的断言验证结果

示例：

```python
def test_new_feature(self, client: TestClient, authenticated_user: Dict[str, Any]):
    """测试新功能"""
    response = client.get(
        "/api/new-endpoint/",
        headers=authenticated_user["headers"]
    )
    
    data = assert_response_success(response)
    assert "expected_field" in data
``` 