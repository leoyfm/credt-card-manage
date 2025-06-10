"""
新一代测试框架 v2.0

一个更易用、更全面的测试框架，提供：
- 极简API设计
- 自动数据管理  
- 流畅断言接口
- 智能运行器
- 丰富报告

Usage:
    from tests.framework import test_suite, api_test, with_user, with_cards
    
    @test_suite("用户管理")
    class UserTests:
        
        @api_test
        @with_user
        def test_get_profile(self, api, user):
            api.get("/api/v1/user/profile").should.succeed()
"""

__version__ = "2.0.0"
__author__ = "LEO"
__email__ = "leoyfm@gmail.com"

# 核心装饰器
from .decorators.test import test_suite, api_test, test_scenario
from .decorators.data import with_user, with_cards, with_transactions, with_data
from .decorators.performance import performance_test, benchmark, stress_test, load_test

# 核心组件
from .core.suite import TestSuite
from .core.runner import SmartTestRunner
from .clients.api import FluentAPIClient, ResponseAssertion
from .data.factory import DataFactory, UserFactory, CardFactory, TransactionFactory

# 工具类
from .utils.env import TestEnvironment
from .utils.timing import Timer, Benchmark

__all__ = [
    # 装饰器
    "test_suite", "api_test", "test_scenario",
    "with_user", "with_cards", "with_transactions", "with_data", 
    "performance_test", "benchmark", "stress_test", "load_test",
    
    # 核心组件
    "TestSuite", "SmartTestRunner", "FluentAPIClient", "ResponseAssertion",
    "DataFactory", "UserFactory", "CardFactory", "TransactionFactory",
    
    # 工具类
    "TestEnvironment", "Timer", "Benchmark"
] 