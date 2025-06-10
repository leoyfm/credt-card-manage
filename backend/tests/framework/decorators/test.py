"""
测试装饰器系统

提供声明式的测试定义、标记、参数化等功能。
"""

import time
import asyncio
import inspect
from functools import wraps
from typing import Any, Dict, List, Optional, Callable, Union
from dataclasses import dataclass
import uuid
from datetime import datetime

from ..core.suite import TestSuite, TestCase, TestPriority, register_suite
from ..clients.api import FluentAPIClient


@dataclass
class TestMetadata:
    """测试元数据"""
    name: str
    description: str = ""
    tags: List[str] = None
    priority: TestPriority = TestPriority.MEDIUM
    timeout: Optional[int] = None
    retry_count: int = 0
    skip_condition: Optional[Callable] = None
    expected_to_fail: bool = False
    depends_on: List[str] = None
    parameters: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.depends_on is None:
            self.depends_on = []
        if self.parameters is None:
            self.parameters = {}


class TestRegistry:
    """测试注册表"""
    
    _suites: Dict[str, TestSuite] = {}
    _current_suite: Optional[TestSuite] = None
    
    @classmethod
    def get_or_create_suite(cls, name: str, description: str = "") -> TestSuite:
        """获取或创建测试套件"""
        if name not in cls._suites:
            cls._suites[name] = TestSuite(name, description)
            register_suite(cls._suites[name])
        return cls._suites[name]
    
    @classmethod
    def set_current_suite(cls, suite: TestSuite):
        """设置当前套件"""
        cls._current_suite = suite
    
    @classmethod
    def get_current_suite(cls) -> Optional[TestSuite]:
        """获取当前套件"""
        return cls._current_suite
    
    @classmethod
    def add_test_to_current_suite(cls, test_case: TestCase):
        """添加测试到当前套件"""
        if cls._current_suite:
            cls._current_suite.tests.append(test_case)
        else:
            # 如果没有当前套件，创建默认套件
            default_suite = cls.get_or_create_suite("default", "默认测试套件")
            default_suite.tests.append(test_case)


def test_suite(name: str, description: str = "", **kwargs):
    """
    测试套件装饰器
    
    用于标记类为测试套件，自动创建TestSuite对象。
    
    Args:
        name: 套件名称
        description: 套件描述
        **kwargs: 其他套件配置
    """
    def decorator(cls):
        # 创建测试套件
        suite = TestRegistry.get_or_create_suite(name, description)
        suite.with_config(**kwargs)
        
        # 设置为当前套件
        TestRegistry.set_current_suite(suite)
        
        # 在类上添加套件信息
        cls._test_suite_name = name
        cls._suite = suite
        
        # 处理类中的测试方法
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if hasattr(attr, '_test_metadata'):
                # 这是一个测试方法，添加到套件中
                metadata = attr._test_metadata
                
                # 创建测试用例
                test_case = TestCase(
                    test_id=str(uuid.uuid4()),
                    name=metadata.name,
                    func=attr,
                    suite=suite,
                    tags=metadata.tags,
                    priority=metadata.priority,
                    timeout=metadata.timeout
                )
                
                suite.tests.append(test_case)
        
        return cls
    
    return decorator


def api_test(name: str = None, **test_kwargs):
    """
    API测试装饰器
    
    标记方法为API测试，自动注入API客户端和相关功能。
    
    Args:
        name: 测试名称
        **test_kwargs: 测试配置
    """
    def decorator(func):
        test_name = name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 注入API客户端
            if 'api' not in kwargs:
                kwargs['api'] = FluentAPIClient()
            
            # 执行测试
            return func(*args, **kwargs)
        
        # 添加测试元数据
        wrapper._test_metadata = TestMetadata(
            name=test_name,
            **test_kwargs
        )
        
        return wrapper
    
    return decorator


def unit_test(name: str = None, **test_kwargs):
    """
    单元测试装饰器
    
    标记方法为单元测试。
    """
    def decorator(func):
        test_name = name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # 添加测试元数据
        wrapper._test_metadata = TestMetadata(
            name=test_name,
            tags=["unit"],
            **test_kwargs
        )
        
        return wrapper
    
    return decorator


def integration_test(name: str = None, **test_kwargs):
    """
    集成测试装饰器
    
    标记方法为集成测试。
    """
    def decorator(func):
        test_name = name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # 添加测试元数据
        wrapper._test_metadata = TestMetadata(
            name=test_name,
            tags=["integration"],
            **test_kwargs
        )
        
        return wrapper
    
    return decorator


def performance_test(name: str = None, max_duration: float = None, **test_kwargs):
    """
    性能测试装饰器
    
    标记方法为性能测试，自动测量执行时间。
    """
    def decorator(func):
        test_name = name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                duration = time.time() - start_time
                
                # 检查性能约束
                if max_duration and duration > max_duration:
                    raise AssertionError(f"性能测试失败: 执行时间 {duration:.3f}s 超过限制 {max_duration}s")
                
                print(f"⏱️ 性能测试 {test_name}: {duration:.3f}s")
                
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                print(f"💥 性能测试 {test_name} 失败 ({duration:.3f}s): {e}")
                raise
        
        # 添加测试元数据
        wrapper._test_metadata = TestMetadata(
            name=test_name,
            tags=["performance"],
            **test_kwargs
        )
        
        return wrapper
    
    return decorator


def stress_test(name: str = None, iterations: int = 100, **test_kwargs):
    """
    压力测试装饰器
    
    多次执行测试函数，验证系统稳定性。
    """
    def decorator(func):
        test_name = name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            failed_count = 0
            durations = []
            
            print(f"🔥 开始压力测试 {test_name} ({iterations} 次迭代)")
            
            for i in range(iterations):
                start_time = time.time()
                
                try:
                    func(*args, **kwargs)
                    duration = time.time() - start_time
                    durations.append(duration)
                    
                    if (i + 1) % 10 == 0:
                        avg_duration = sum(durations) / len(durations)
                        print(f"  进度: {i+1}/{iterations}, 平均耗时: {avg_duration:.3f}s")
                        
                except Exception as e:
                    failed_count += 1
                    print(f"  第{i+1}次迭代失败: {e}")
            
            # 统计结果
            success_rate = ((iterations - failed_count) / iterations) * 100
            avg_duration = sum(durations) / len(durations) if durations else 0
            
            print(f"🎯 压力测试完成: 成功率 {success_rate:.1f}%, 平均耗时 {avg_duration:.3f}s")
            
            if failed_count > 0:
                raise AssertionError(f"压力测试失败: {failed_count}/{iterations} 次失败")
        
        # 添加测试元数据
        wrapper._test_metadata = TestMetadata(
            name=test_name,
            tags=["stress"],
            **test_kwargs
        )
        
        return wrapper
    
    return decorator


def smoke_test(name: str = None, **test_kwargs):
    """
    冒烟测试装饰器
    
    标记为关键的冒烟测试。
    """
    def decorator(func):
        test_name = name or func.__name__
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # 添加测试元数据
        wrapper._test_metadata = TestMetadata(
            name=test_name,
            tags=["smoke", "critical"],
            priority=TestPriority.CRITICAL,
            **test_kwargs
        )
        
        return wrapper
    
    return decorator


def tag(*tags: str):
    """
    标签装饰器
    
    为测试添加标签。
    """
    def decorator(func):
        if hasattr(func, '_test_metadata'):
            func._test_metadata.tags.extend(tags)
        else:
            func._test_metadata = TestMetadata(
                name=func.__name__,
                tags=list(tags)
            )
        
        return func
    
    return decorator


def priority(level: TestPriority):
    """
    优先级装饰器
    
    设置测试优先级。
    """
    def decorator(func):
        if hasattr(func, '_test_metadata'):
            func._test_metadata.priority = level
        else:
            func._test_metadata = TestMetadata(
                name=func.__name__,
                priority=level
            )
        
        return func
    
    return decorator


def timeout(seconds: int):
    """
    超时装饰器
    
    设置测试超时时间。
    """
    def decorator(func):
        if hasattr(func, '_test_metadata'):
            func._test_metadata.timeout = seconds
        else:
            func._test_metadata = TestMetadata(
                name=func.__name__,
                timeout=seconds
            )
        
        return func
    
    return decorator


def retry(count: int = 3, delay: float = 1.0):
    """
    重试装饰器
    
    测试失败时自动重试。
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(count + 1):
                try:
                    if attempt > 0:
                        print(f"🔄 重试测试 {func.__name__} (第{attempt}次)")
                        time.sleep(delay)
                    
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    if attempt == count:
                        print(f"💥 测试 {func.__name__} 重试{count}次后仍然失败")
                        raise
                    else:
                        print(f"⚠️ 测试 {func.__name__} 第{attempt+1}次尝试失败: {e}")
            
            # 这行代码理论上不会执行到
            raise last_exception
        
        # 保持原有元数据
        if hasattr(func, '_test_metadata'):
            wrapper._test_metadata = func._test_metadata
            wrapper._test_metadata.retry_count = count
        
        return wrapper
    
    return decorator


def skip_if(condition: Union[bool, Callable], reason: str = ""):
    """
    条件跳过装饰器
    
    根据条件跳过测试。
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 评估跳过条件
            should_skip = condition() if callable(condition) else condition
            
            if should_skip:
                print(f"⏭️ 跳过测试 {func.__name__}: {reason}")
                return  # 跳过测试
            
            return func(*args, **kwargs)
        
        # 保持原有元数据
        if hasattr(func, '_test_metadata'):
            wrapper._test_metadata = func._test_metadata
            wrapper._test_metadata.skip_condition = condition
        
        return wrapper
    
    return decorator


def expect_failure(reason: str = ""):
    """
    预期失败装饰器
    
    标记测试预期会失败。
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                print(f"⚠️ 预期失败的测试 {func.__name__} 意外成功: {reason}")
                raise AssertionError(f"预期失败的测试成功了: {reason}")
            except AssertionError as e:
                if "预期失败的测试成功了" in str(e):
                    raise
                print(f"✅ 测试 {func.__name__} 按预期失败: {e}")
                return  # 预期的失败
            except Exception as e:
                print(f"✅ 测试 {func.__name__} 按预期失败: {e}")
                return  # 预期的失败
        
        # 保持原有元数据
        if hasattr(func, '_test_metadata'):
            wrapper._test_metadata = func._test_metadata
            wrapper._test_metadata.expected_to_fail = True
        
        return wrapper
    
    return decorator


def depends_on(*test_names: str):
    """
    依赖装饰器
    
    指定测试依赖关系。
    """
    def decorator(func):
        if hasattr(func, '_test_metadata'):
            func._test_metadata.depends_on.extend(test_names)
        else:
            func._test_metadata = TestMetadata(
                name=func.__name__,
                depends_on=list(test_names)
            )
        
        return func
    
    return decorator


def parametrize(param_name: str, param_values: List[Any]):
    """
    参数化装饰器
    
    为测试提供多组参数。
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            
            for i, value in enumerate(param_values):
                print(f"📋 参数化测试 {func.__name__} - 参数组 {i+1}/{len(param_values)}: {param_name}={value}")
                
                # 设置参数
                kwargs[param_name] = value
                
                try:
                    result = func(*args, **kwargs)
                    results.append(result)
                    print(f"✅ 参数组 {i+1} 通过")
                except Exception as e:
                    print(f"❌ 参数组 {i+1} 失败: {e}")
                    raise
            
            return results
        
        # 保持原有元数据
        if hasattr(func, '_test_metadata'):
            wrapper._test_metadata = func._test_metadata
            wrapper._test_metadata.parameters[param_name] = param_values
        
        return wrapper
    
    return decorator


def setup_method(func: Callable):
    """
    前置方法装饰器
    
    标记方法为测试前置操作。
    """
    func._is_setup_method = True
    return func


def teardown_method(func: Callable):
    """
    后置方法装饰器
    
    标记方法为测试后置操作。
    """
    func._is_teardown_method = True
    return func


def before_suite(func: Callable):
    """
    套件前置装饰器
    
    标记方法为套件启动前操作。
    """
    func._is_before_suite = True
    return func


def after_suite(func: Callable):
    """
    套件后置装饰器
    
    标记方法为套件结束后操作。
    """
    func._is_after_suite = True
    return func


# 便捷组合装饰器
def api_smoke_test(name: str = None, **kwargs):
    """API冒烟测试组合装饰器"""
    def decorator(func):
        decorated = smoke_test(name, **kwargs)(func)
        decorated = api_test()(decorated)
        return decorated
    return decorator


def api_performance_test(name: str = None, max_duration: float = None, **kwargs):
    """API性能测试组合装饰器"""
    def decorator(func):
        decorated = performance_test(name, max_duration, **kwargs)(func)
        decorated = api_test()(decorated)
        return decorated
    return decorator


def api_stress_test(name: str = None, iterations: int = 100, **kwargs):
    """API压力测试组合装饰器"""
    def decorator(func):
        decorated = stress_test(name, iterations, **kwargs)(func)
        decorated = api_test()(decorated)
        return decorated
    return decorator


# 测试发现辅助函数
def is_test_method(obj) -> bool:
    """检查对象是否为测试方法"""
    return (
        callable(obj) and 
        hasattr(obj, '_test_metadata') and
        not obj.__name__.startswith('_')
    )


def get_test_metadata(test_func) -> Optional[TestMetadata]:
    """获取测试方法的元数据"""
    return getattr(test_func, '_test_metadata', None)


def collect_test_methods(test_class) -> List[Callable]:
    """收集类中的所有测试方法"""
    test_methods = []
    
    for attr_name in dir(test_class):
        if attr_name.startswith('_'):
            continue
            
        attr = getattr(test_class, attr_name)
        if is_test_method(attr):
            test_methods.append(attr)
    
    return test_methods 