"""
测试装饰器

提供极简的测试声明方式，自动处理测试套件管理和API客户端注入。

Usage:
    @test_suite("用户管理")
    class UserTests:
        
        @api_test
        @with_user
        def test_get_profile(self, api, user):
            api.get("/api/v1/user/profile").should.succeed()
"""

import functools
import logging
from typing import Dict, Any, Callable, Optional, List
from ..clients.api import FluentAPIClient
from ..core.suite import TestSuite
from ..core.scenario import TestScenario

logger = logging.getLogger(__name__)


def test_suite(name: str, description: str = None):
    """
    测试套件装饰器
    
    Args:
        name: 测试套件名称
        description: 测试套件描述
    """
    def decorator(cls):
        cls._test_suite_name = name
        cls._test_suite_description = description
        cls._suite = TestSuite(name, description)
        
        # 收集测试方法
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and hasattr(attr, '_is_test_method'):
                cls._suite.add_test(attr)
        
        logger.info(f"注册测试套件: {name}")
        return cls
    
    return decorator


def api_test(func: Callable = None, **options):
    """
    API测试装饰器
    
    自动注入FluentAPIClient实例到测试方法中。
    
    Args:
        func: 测试函数
        **options: 测试选项（超时、重试等）
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # 创建API客户端
            api = FluentAPIClient()
            
            # 设置测试选项
            if 'timeout' in options:
                api.session.timeout = options['timeout']
            
            # 注入API客户端
            if 'api' not in kwargs:
                kwargs['api'] = api
            
            try:
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"API测试失败 {f.__name__}: {e}")
                raise
            finally:
                # 清理工作
                if hasattr(api, 'cleanup'):
                    api.cleanup()
        
        wrapper._is_test_method = True
        wrapper._is_api_test = True
        wrapper._test_options = options
        return wrapper
    
    if func is None:
        # 带参数的装饰器
        return decorator
    else:
        # 不带参数的装饰器
        return decorator(func)


def test_scenario(name: str, description: str = None):
    """
    测试场景装饰器
    
    用于标记场景化测试类，支持多步骤测试流程。
    
    Args:
        name: 场景名称
        description: 场景描述
    """
    def decorator(cls):
        cls._scenario_name = name
        cls._scenario_description = description
        cls._scenario = TestScenario(name, description)
        
        # 收集场景步骤
        for attr_name in dir(cls):
            if attr_name.startswith('step_'):
                step_func = getattr(cls, attr_name)
                if callable(step_func):
                    cls._scenario.add_step(step_func)
        
        logger.info(f"注册测试场景: {name}")
        return cls
    
    return decorator


def test_step(order: int = None, description: str = None):
    """
    测试步骤装饰器
    
    用于标记场景中的测试步骤。
    
    Args:
        order: 步骤顺序
        description: 步骤描述
    """
    def decorator(func):
        func._is_test_step = True
        func._step_order = order
        func._step_description = description
        return func
    
    return decorator


def require_auth(func):
    """
    要求认证装饰器
    
    确保测试执行前已设置认证信息。
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        api = kwargs.get('api')
        if api and not api.auth_token:
            raise ValueError(f"测试 {func.__name__} 需要认证，但未设置auth_token")
        return func(*args, **kwargs)
    
    wrapper._requires_auth = True
    return wrapper


def skip_if(condition: bool, reason: str = "跳过测试"):
    """
    条件跳过装饰器
    
    Args:
        condition: 跳过条件
        reason: 跳过原因
    """
    def decorator(func):
        if condition:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                logger.info(f"跳过测试 {func.__name__}: {reason}")
                return
            return wrapper
        return func
    
    return decorator


def timeout(seconds: int):
    """
    超时装饰器
    
    Args:
        seconds: 超时时间（秒）
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"测试 {func.__name__} 超时({seconds}秒)")
            
            # 设置超时信号
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(seconds)
            
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)
        
        wrapper._timeout = seconds
        return wrapper
    
    return decorator


def retry(times: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """
    重试装饰器
    
    Args:
        times: 重试次数
        delay: 重试间隔（秒）
        exceptions: 需要重试的异常类型
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times - 1:
                        # 最后一次重试失败，抛出异常
                        logger.error(f"测试 {func.__name__} 重试{times}次后仍然失败: {e}")
                        raise
                    else:
                        logger.warning(f"测试 {func.__name__} 第{attempt+1}次尝试失败，{delay}秒后重试: {e}")
                        time.sleep(delay)
        
        wrapper._retry_times = times
        wrapper._retry_delay = delay
        return wrapper
    
    return decorator


def tags(*tag_list):
    """
    标签装饰器
    
    为测试添加标签，用于筛选和分组。
    
    Args:
        *tag_list: 标签列表
    """
    def decorator(func):
        func._test_tags = list(tag_list)
        return func
    
    return decorator


def priority(level: int):
    """
    优先级装饰器
    
    设置测试优先级，数字越小优先级越高。
    
    Args:
        level: 优先级等级
    """
    def decorator(func):
        func._priority = level
        return func
    
    return decorator


def description(text: str):
    """
    描述装饰器
    
    为测试添加详细描述。
    
    Args:
        text: 测试描述
    """
    def decorator(func):
        func._test_description = text
        return func
    
    return decorator


class TestContext:
    """测试上下文"""
    
    def __init__(self):
        self.data = {}
        self.api = None
        self.user = None
        self.cleanup_funcs = []
    
    def add_cleanup(self, func: Callable):
        """添加清理函数"""
        self.cleanup_funcs.append(func)
    
    def cleanup(self):
        """执行清理"""
        for func in reversed(self.cleanup_funcs):
            try:
                func()
            except Exception as e:
                logger.warning(f"清理函数执行失败: {e}")


def with_context(func):
    """
    上下文装饰器
    
    为测试方法提供测试上下文。
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        context = TestContext()
        kwargs['context'] = context
        
        try:
            return func(*args, **kwargs)
        finally:
            context.cleanup()
    
    return wrapper 