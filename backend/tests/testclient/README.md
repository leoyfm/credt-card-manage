# TestClient 测试模块

## 概述

`tests/testclient/` 目录包含使用测试数据库进行的完整API测试。这些测试使用真实的HTTP请求和数据库操作，提供端到端的功能验证。

## 特点

- **真实环境测试**: 使用测试数据库，模拟真实的数据库操作
- **完整HTTP测试**: 通过HTTP请求测试API接口
- **业务流程验证**: 测试完整的业务流程和用户场景
- **数据持久化**: 验证数据在数据库中的正确存储和检索

## 测试结构

```
tests/testclient/
├── __init__.py          # 模块初始化
├── conftest.py          # pytest配置和fixture
├── test_auth.py         # 用户认证功能测试
├── test_reminders.py    # 用户提醒功能测试
├── run_tests.py         # 测试运行器
└── README.md           # 本说明文档
```

## 核心Fixture

### api_client
创建基础的API客户端，用于发送HTTP请求。

```python
def test_example(api_client):
    response = api_client.get("/api/v1/some-endpoint")
    assert response.status_code == 200
```

### test_user
生成测试用户数据。

```python
def test_example(test_user):
    assert "username" in test_user
    assert "password" in test_user
    assert "email" in test_user
```

### authenticated_client
创建已认证的API客户端，自动完成用户注册和登录流程。

```python
def test_example(authenticated_client):
    api_client, user_data = authenticated_client
    response = api_client.get("/api/v1/user/profile")
    assert response.status_code == 200
```

## 运行测试

### 启动服务器
在运行测试前，需要启动开发服务器：

```bash
# 终端1: 启动服务器
python main.py --reload
```

### 运行测试

#### 方式一：使用测试运行器（推荐）
```bash
# 使用专用的测试运行器
python tests/testclient/run_tests.py
```

#### 方式二：直接使用pytest
```bash
# 运行所有testclient测试
pytest tests/testclient/ -v

# 运行特定测试文件
pytest tests/testclient/test_auth.py -v

# 运行特定测试方法
pytest tests/testclient/test_auth.py::TestUserAuth::test_user_register_success -v
```

## 测试用例

### 用户认证测试 (test_auth.py)

- **test_user_register_success**: 测试用户注册成功
- **test_user_register_duplicate_username**: 测试重复用户名注册失败
- **test_user_login_username_success**: 测试用户名登录成功
- **test_get_user_profile_success**: 测试获取用户资料成功
- **test_complete_auth_flow**: 测试完整的认证流程

### 用户提醒测试 (test_reminders.py)

- **test_create_reminder_setting_success**: 测试创建提醒设置成功
- **test_get_reminder_settings_list**: 测试获取提醒设置列表（支持分页）
- **test_update_reminder_setting**: 测试更新提醒设置
- **test_delete_reminder_setting**: 测试删除提醒设置
- **test_get_reminder_statistics**: 测试获取提醒统计数据
- **test_get_upcoming_reminders**: 测试获取即将到来的提醒
- **test_get_unread_reminders_count**: 测试获取未读提醒个数
- **test_mark_all_reminders_as_read**: 测试标记所有提醒为已读
- **test_get_recent_reminders**: 测试获取最近提醒记录
- **test_generate_automatic_reminders**: 测试生成自动提醒
- **test_reminder_permission_control**: 测试提醒功能权限控制
- **test_reminder_setting_not_found**: 测试访问不存在提醒设置的错误处理

## 最佳实践

1. **数据隔离**: 每个测试使用独立的测试数据
2. **清理资源**: 测试完成后自动清理创建的数据
3. **错误处理**: 验证各种错误情况和边界条件
4. **完整流程**: 测试端到端的业务流程
5. **断言详细**: 提供详细的断言信息，便于调试

## 注意事项

- 这些测试需要运行的服务器实例
- 使用测试数据库，不会影响开发数据库
- 测试可能会创建和删除数据库记录
- 建议在CI/CD环境中使用独立的测试数据库

## 扩展测试

要添加新的测试模块：

1. 在 `tests/testclient/` 目录下创建新的测试文件
2. 使用现有的fixture进行测试
3. 遵循现有的测试命名和结构规范
4. 更新本README文档 