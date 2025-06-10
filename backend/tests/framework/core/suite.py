"""
测试套件核心组件

提供测试套件的基础功能，包括测试管理、数据工厂管理、钩子函数等。
"""

from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
import traceback
from datetime import datetime


class TestStatus(Enum):
    """测试状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestPriority(Enum):
    """测试优先级枚举"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TestResult:
    """测试结果"""
    test_id: str
    test_name: str
    status: TestStatus
    duration: float = 0.0
    error_message: Optional[str] = None
    error_trace: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    context: Optional[Dict[str, Any]] = None
    assertions: List[Dict[str, Any]] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestCase:
    """测试用例"""
    test_id: str
    name: str
    func: Callable
    suite: 'TestSuite'
    tags: List[str] = field(default_factory=list)
    priority: TestPriority = TestPriority.MEDIUM
    timeout: Optional[int] = None
    setup_hooks: List[Callable] = field(default_factory=list)
    teardown_hooks: List[Callable] = field(default_factory=list)
    data_requirements: Dict[str, Any] = field(default_factory=dict)
    
    def execute(self, context: Dict[str, Any] = None) -> TestResult:
        """执行测试用例"""
        if context is None:
            context = {}
            
        result = TestResult(
            test_id=self.test_id,
            test_name=self.name,
            status=TestStatus.RUNNING,
            start_time=datetime.now(),
            context=context
        )
        
        try:
            # 执行前置钩子
            for hook in self.setup_hooks:
                hook(context)
            
            # 执行测试
            start_time = time.time()
            self.func(**context)
            end_time = time.time()
            
            result.duration = end_time - start_time
            result.status = TestStatus.PASSED
            result.end_time = datetime.now()
            
        except AssertionError as e:
            result.status = TestStatus.FAILED
            result.error_message = str(e)
            result.error_trace = traceback.format_exc()
            result.end_time = datetime.now()
            
        except Exception as e:
            result.status = TestStatus.ERROR
            result.error_message = str(e)
            result.error_trace = traceback.format_exc()
            result.end_time = datetime.now()
            
        finally:
            # 执行后置钩子
            try:
                for hook in self.teardown_hooks:
                    hook(context)
            except Exception as cleanup_error:
                print(f"清理错误: {cleanup_error}")
        
        return result


class TestSuite:
    """测试套件基类"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.tests: List[TestCase] = []
        self.setup_hooks: List[Callable] = []
        self.teardown_hooks: List[Callable] = []
        self.suite_setup_hooks: List[Callable] = []
        self.suite_teardown_hooks: List[Callable] = []
        self.data_factories: Dict[str, Any] = {}
        self.tags: List[str] = []
        self.environment: Dict[str, Any] = {}
        self.config: Dict[str, Any] = {}
        
    def add_test(self, func: Callable, name: str = None, **kwargs) -> TestCase:
        """添加测试方法"""
        test_id = str(uuid.uuid4())
        test_name = name or func.__name__
        
        test_case = TestCase(
            test_id=test_id,
            name=test_name,
            func=func,
            suite=self,
            **kwargs
        )
        
        self.tests.append(test_case)
        return test_case
    
    def before_each(self, hook_func: Callable):
        """添加每个测试前的钩子"""
        self.setup_hooks.append(hook_func)
        return hook_func
    
    def after_each(self, hook_func: Callable):
        """添加每个测试后的钩子"""
        self.teardown_hooks.append(hook_func)
        return hook_func
    
    def before_suite(self, hook_func: Callable):
        """添加套件启动前的钩子"""
        self.suite_setup_hooks.append(hook_func)
        return hook_func
    
    def after_suite(self, hook_func: Callable):
        """添加套件结束后的钩子"""
        self.suite_teardown_hooks.append(hook_func)
        return hook_func
    
    def with_data(self, **factories):
        """配置数据工厂"""
        self.data_factories.update(factories)
        return self
    
    def with_tags(self, *tags: str):
        """设置标签"""
        self.tags.extend(tags)
        return self
    
    def with_config(self, **config):
        """设置配置"""
        self.config.update(config)
        return self
    
    def get_tests_by_tags(self, tags: List[str]) -> List[TestCase]:
        """根据标签筛选测试"""
        if not tags:
            return self.tests
        
        filtered_tests = []
        for test in self.tests:
            if any(tag in test.tags for tag in tags):
                filtered_tests.append(test)
        
        return filtered_tests
    
    def get_tests_by_priority(self, min_priority: TestPriority) -> List[TestCase]:
        """根据优先级筛选测试"""
        priority_order = [TestPriority.CRITICAL, TestPriority.HIGH, TestPriority.MEDIUM, TestPriority.LOW]
        min_index = priority_order.index(min_priority)
        
        return [test for test in self.tests if priority_order.index(test.priority) <= min_index]
    
    def run_suite(self, filter_tags: List[str] = None, min_priority: TestPriority = None) -> List[TestResult]:
        """运行整个测试套件"""
        print(f"\n开始运行测试套件: {self.name}")
        if self.description:
            print(f"描述: {self.description}")
        
        # 执行套件前置钩子
        for hook in self.suite_setup_hooks:
            try:
                hook()
            except Exception as e:
                print(f"套件前置钩子执行失败: {e}")
        
        # 筛选测试
        tests_to_run = self.tests
        if filter_tags:
            tests_to_run = self.get_tests_by_tags(filter_tags)
        if min_priority:
            tests_to_run = [t for t in tests_to_run if t.priority in [TestPriority.CRITICAL, TestPriority.HIGH, TestPriority.MEDIUM, TestPriority.LOW][:list(TestPriority).index(min_priority) + 1]]
        
        results = []
        passed = 0
        failed = 0
        errors = 0
        
        print(f"共找到 {len(tests_to_run)} 个测试用例")
        
        # 执行测试
        for i, test in enumerate(tests_to_run, 1):
            print(f"\n[{i}/{len(tests_to_run)}] 运行测试: {test.name}")
            
            # 准备测试环境
            test_context = self._prepare_test_context(test)
            
            # 执行测试
            result = test.execute(test_context)
            results.append(result)
            
            # 统计结果
            if result.status == TestStatus.PASSED:
                passed += 1
                print(f"✅ 通过 ({result.duration:.3f}s)")
            elif result.status == TestStatus.FAILED:
                failed += 1
                print(f"❌ 失败: {result.error_message}")
            elif result.status == TestStatus.ERROR:
                errors += 1
                print(f"💥 错误: {result.error_message}")
        
        # 执行套件后置钩子
        for hook in self.suite_teardown_hooks:
            try:
                hook()
            except Exception as e:
                print(f"套件后置钩子执行失败: {e}")
        
        # 输出总结
        total = len(tests_to_run)
        print(f"\n🎯 测试套件完成: {self.name}")
        print(f"总计: {total}, 通过: {passed}, 失败: {failed}, 错误: {errors}")
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"成功率: {success_rate:.1f}%")
        
        return results
    
    def _prepare_test_context(self, test: TestCase) -> Dict[str, Any]:
        """准备测试上下文环境"""
        context = {}
        
        # 添加环境变量
        context.update(self.environment)
        
        # 添加配置
        context.update(self.config)
        
        # TODO: 这里应该根据test.data_requirements创建测试数据
        # 暂时返回基础上下文
        
        return context


class TestSuiteBuilder:
    """测试套件构建器"""
    
    def __init__(self, name: str):
        self.suite = TestSuite(name)
    
    def description(self, desc: str):
        """设置描述"""
        self.suite.description = desc
        return self
    
    def tags(self, *tags: str):
        """设置标签"""
        self.suite.with_tags(*tags)
        return self
    
    def config(self, **config):
        """设置配置"""
        self.suite.with_config(**config)
        return self
    
    def data_factories(self, **factories):
        """设置数据工厂"""
        self.suite.with_data(**factories)
        return self
    
    def build(self) -> TestSuite:
        """构建测试套件"""
        return self.suite


# 全局测试套件注册表
_test_suites: Dict[str, TestSuite] = {}


def register_suite(suite: TestSuite):
    """注册测试套件"""
    _test_suites[suite.name] = suite


def get_suite(name: str) -> Optional[TestSuite]:
    """获取测试套件"""
    return _test_suites.get(name)


def get_all_suites() -> Dict[str, TestSuite]:
    """获取所有测试套件"""
    return _test_suites.copy()


def create_suite(name: str) -> TestSuiteBuilder:
    """创建测试套件构建器"""
    return TestSuiteBuilder(name) 