"""
信用卡管理系统测试框架 v2.0

新一代智能测试框架，提供极简API、自动数据管理、流畅断言等功能。

特性:
- 🎯 极简API: 一行代码完成复杂测试
- 🤖 自动化: 自动数据准备、清理和依赖管理
- 📝 声明式: 通过装饰器和配置声明测试需求
- 🧠 智能感知: 自动检测测试环境和依赖
- 🔗 流畅接口: 链式调用，代码如文档般清晰

快速开始:
    from tests.framework import *
    
    @test_suite("我的测试套件")
    class MyTests:
        @with_user()
        @api_test("测试用户登录")
        def test_login(self, api, user):
            api.login(user.username, user.password).should.succeed()

使用示例:
    # 交互式运行
    python run_tests_v2.py
    
    # 命令行运行
    python run_tests_v2.py --all
    python run_tests_v2.py --smoke
    python run_tests_v2.py --tags api performance
"""

__version__ = "2.0.0"
__author__ = "Credit Card Management Team"
__description__ = "智能测试框架 v2.0"

# 核心组件导入
from .core.suite import (
    TestSuite, TestCase, TestResult, TestStatus, TestPriority,
    register_suite, get_suite, get_all_suites, create_suite
)

from .core.runner import (
    SmartTestRunner, TestRunConfig, TestDiscovery,
    create_runner, run_all_tests, run_smoke_tests, run_performance_tests
)

from .core.assertion import (
    expect, expect_response, expect_performance,
    assert_equal, assert_not_equal, assert_true, assert_false,
    assert_none, assert_not_none, assert_contains, assert_length,
    BaseAssertion, StringAssertion, NumberAssertion, 
    CollectionAssertion, DictionaryAssertion, ResponseAssertion
)

# 客户端组件导入
from .clients.api import (
    FluentAPIClient, APIClientBuilder,
    create_api_client, api_client_builder,
    get_default_client, set_default_client,
    get, post, put, delete, login, logout, health_check
)

# 装饰器组件导入
from .decorators.test import (
    test_suite, api_test, unit_test, integration_test,
    performance_test, stress_test, smoke_test,
    tag, priority, timeout, retry, parametrize,
    skip_if, expect_failure, depends_on,
    setup_method, teardown_method, before_suite, after_suite,
    api_smoke_test, api_performance_test, api_stress_test
)

from .decorators.data import (
    with_user, with_cards, with_transactions, with_user_and_cards, with_test_data,
    UserFactory, CardFactory, TransactionFactory, DataManager,
    UserData, CardData, TransactionData
)

# 便捷导入别名
TestFramework = SmartTestRunner
API = FluentAPIClient
Suite = TestSuite

# 全部导出
__all__ = [
    # 版本信息
    "__version__", "__author__", "__description__",
    
    # 核心组件
    "TestSuite", "TestCase", "TestResult", "TestStatus", "TestPriority",
    "register_suite", "get_suite", "get_all_suites", "create_suite",
    
    "SmartTestRunner", "TestRunConfig", "TestDiscovery",
    "create_runner", "run_all_tests", "run_smoke_tests", "run_performance_tests",
    
    "expect", "expect_response", "expect_performance",
    "assert_equal", "assert_not_equal", "assert_true", "assert_false",
    "assert_none", "assert_not_none", "assert_contains", "assert_length",
    "BaseAssertion", "StringAssertion", "NumberAssertion",
    "CollectionAssertion", "DictionaryAssertion", "ResponseAssertion",
    
    # 客户端组件
    "FluentAPIClient", "APIClientBuilder",
    "create_api_client", "api_client_builder",
    "get_default_client", "set_default_client",
    "get", "post", "put", "delete", "login", "logout", "health_check",
    
    # 装饰器组件
    "test_suite", "api_test", "unit_test", "integration_test",
    "performance_test", "stress_test", "smoke_test",
    "tag", "priority", "timeout", "retry", "parametrize",
    "skip_if", "expect_failure", "depends_on",
    "setup_method", "teardown_method", "before_suite", "after_suite",
    "api_smoke_test", "api_performance_test", "api_stress_test",
    
    "with_user", "with_cards", "with_transactions", "with_user_and_cards", "with_test_data",
    "UserFactory", "CardFactory", "TransactionFactory", "DataManager",
    "UserData", "CardData", "TransactionData",
    
    # 便捷别名
    "TestFramework", "API", "Suite"
]


def get_framework_info():
    """获取测试框架信息"""
    return {
        "name": "信用卡管理系统测试框架",
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "features": [
            "极简API设计",
            "自动化数据管理",
            "声明式测试配置",
            "智能环境感知",
            "流畅断言接口",
            "性能测试支持",
            "压力测试支持",
            "并行执行支持",
            "丰富的报告格式"
        ]
    }


def print_framework_info():
    """打印测试框架信息"""
    info = get_framework_info()
    
    print("=" * 60)
    print(f"🚀 {info['name']} v{info['version']}")
    print("=" * 60)
    print(f"📝 {info['description']}")
    print(f"👨‍💻 作者: {info['author']}")
    print("\n✨ 主要特性:")
    for feature in info['features']:
        print(f"  • {feature}")
    print("=" * 60)


def quick_start_guide():
    """显示快速开始指南"""
    print("""
🚀 快速开始指南

1️⃣ 创建测试套件:
    from tests.framework import *
    
    @test_suite("我的测试套件")
    class MyTests:
        @api_test("基础连通性测试")
        def test_connectivity(self, api):
            api.health_check().should.succeed()

2️⃣ 使用数据装饰器:
    @with_user()
    @with_cards(count=2)
    @api_test("信用卡测试")
    def test_cards(self, api, user, cards):
        response = api.get_cards_list()
        response.should.succeed().with_pagination(total_items=2)

3️⃣ 性能测试:
    @performance_test("API性能测试", max_duration=1.0)
    def test_performance(self, api):
        api.get("/api/v1/user/profile/info").should.succeed()

4️⃣ 运行测试:
    # 交互式模式
    python run_tests_v2.py
    
    # 命令行模式
    python run_tests_v2.py --all
    python run_tests_v2.py --smoke
    python run_tests_v2.py --tags api performance

📚 更多信息请查看: tests/framework/README.md
""")


if __name__ == "__main__":
    print_framework_info()
    quick_start_guide() 