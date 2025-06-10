"""
智能测试运行器

支持自动测试发现、智能执行策略、丰富的报告生成等功能。

Usage:
    runner = SmartTestRunner()
    runner.discover_tests("tests/suites/")
    results = runner.run_all()
"""

import os
import sys
import re
import time
import importlib
import inspect
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass
from datetime import datetime
import json
import asyncio
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import threading

from .suite import TestSuite, TestCase, TestResult, TestStatus, TestPriority
from ..clients.api import FluentAPIClient


class TestDiscovery:
    """测试发现器"""
    
    def __init__(self, base_path: str = "tests/suites/"):
        self.base_path = Path(base_path)
        self.discovered_suites: List[TestSuite] = []
        self.discovered_tests: List[TestCase] = []
    
    def discover_suites(self, pattern: str = "*.py") -> List[TestSuite]:
        """发现测试套件"""
        print(f"🔍 在 {self.base_path} 中发现测试套件...")
        
        suites = []
        test_files = list(self.base_path.rglob(pattern))
        
        for file_path in test_files:
            if file_path.name.startswith('__'):
                continue
                
            try:
                suite = self._load_suite_from_file(file_path)
                if suite:
                    suites.append(suite)
                    print(f"📁 发现套件: {suite.name} ({len(suite.tests)} 个测试)")
            except Exception as e:
                print(f"⚠️ 加载 {file_path} 失败: {e}")
        
        self.discovered_suites = suites
        return suites
    
    def _load_suite_from_file(self, file_path: Path) -> Optional[TestSuite]:
        """从文件加载测试套件"""
        try:
            # 修复Windows路径问题 - 使用绝对路径计算相对模块路径
            file_abs_path = file_path.resolve()
            cwd_abs_path = Path.cwd().resolve()
            
            # 确保文件在当前工作目录下
            try:
                relative_path = file_abs_path.relative_to(cwd_abs_path)
            except ValueError:
                print(f"文件 {file_path} 不在当前工作目录下")
                return None
            
            # 转换为模块路径，统一使用点分隔符
            module_path = str(relative_path).replace('\\', '.').replace('/', '.').replace('.py', '')
            
            # 动态导入模块
            import importlib
            import sys
            
            # 确保当前目录在Python路径中
            if str(cwd_abs_path) not in sys.path:
                sys.path.insert(0, str(cwd_abs_path))
            
            module = importlib.import_module(module_path)
            
            # 查找测试套件类
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    hasattr(obj, '_test_suite_name') and 
                    hasattr(obj, '_suite')):
                    return obj._suite
                    
        except Exception as e:
            print(f"导入模块失败: {e}")
            return None
        
        return None
    
    def discover_tests_by_tags(self, tags: List[str]) -> List[TestCase]:
        """根据标签发现测试"""
        if not self.discovered_suites:
            self.discover_suites()
        
        tests = []
        for suite in self.discovered_suites:
            tests.extend(suite.get_tests_by_tags(tags))
        
        return tests
    
    def discover_tests_by_pattern(self, pattern: str) -> List[TestCase]:
        """根据名称模式发现测试"""
        if not self.discovered_suites:
            self.discover_suites()
        
        tests = []
        for suite in self.discovered_suites:
            for test in suite.tests:
                if re.search(pattern, test.name, re.IGNORECASE):
                    tests.append(test)
        
        return tests


@dataclass
class TestRunConfig:
    """测试运行配置"""
    # 过滤条件
    filter_tags: Optional[List[str]] = None
    filter_pattern: Optional[str] = None
    filter_suites: Optional[List[str]] = None
    min_priority: Optional[TestPriority] = None
    
    # 执行配置
    parallel: bool = False
    max_workers: int = 4
    timeout: Optional[int] = None
    fail_fast: bool = False
    
    # 报告配置
    output_format: str = "console"  # console, json, html
    output_file: Optional[str] = None
    verbose: bool = True
    
    # 环境配置
    base_url: str = "http://127.0.0.1:8000"
    environment: str = "test"


class TestReporter:
    """测试报告生成器"""
    
    def __init__(self, config: TestRunConfig):
        self.config = config
        self.start_time = datetime.now()
        self.end_time = None
        self.total_duration = 0.0
    
    def report_test_start(self, test: TestCase):
        """报告测试开始"""
        if self.config.verbose:
            print(f"▶️ 开始执行: {test.name}")
    
    def report_test_result(self, result: TestResult):
        """报告单个测试结果"""
        if self.config.verbose:
            status_icon = {
                TestStatus.PASSED: "✅",
                TestStatus.FAILED: "❌", 
                TestStatus.ERROR: "💥",
                TestStatus.SKIPPED: "⏭️"
            }.get(result.status, "❓")
            
            print(f"{status_icon} {result.test_name} ({result.duration:.3f}s)")
            
            if result.error_message and self.config.verbose:
                print(f"   💬 {result.error_message}")
    
    def generate_final_report(self, results: List[TestResult]) -> Dict[str, Any]:
        """生成最终报告"""
        self.end_time = datetime.now()
        self.total_duration = (self.end_time - self.start_time).total_seconds()
        
        # 统计数据
        total = len(results)
        passed = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in results if r.status == TestStatus.FAILED)
        errors = sum(1 for r in results if r.status == TestStatus.ERROR)
        skipped = sum(1 for r in results if r.status == TestStatus.SKIPPED)
        
        success_rate = (passed / total * 100) if total > 0 else 0
        avg_duration = sum(r.duration for r in results) / total if total > 0 else 0
        
        report = {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "skipped": skipped,
                "success_rate": round(success_rate, 2),
                "avg_duration": round(avg_duration, 3),
                "total_duration": round(self.total_duration, 3)
            },
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "results": [self._serialize_result(r) for r in results]
        }
        
        # 生成报告
        if self.config.output_format == "console":
            self._print_console_report(report)
        elif self.config.output_format == "json":
            self._generate_json_report(report)
        elif self.config.output_format == "html":
            self._generate_html_report(report)
        
        return report
    
    def _serialize_result(self, result: TestResult) -> Dict[str, Any]:
        """序列化测试结果"""
        return {
            "test_id": result.test_id,
            "test_name": result.test_name,
            "status": result.status.value,
            "duration": result.duration,
            "error_message": result.error_message,
            "start_time": result.start_time.isoformat() if result.start_time else None,
            "end_time": result.end_time.isoformat() if result.end_time else None,
            "assertions": result.assertions,
            "performance_metrics": result.performance_metrics
        }
    
    def _print_console_report(self, report: Dict[str, Any]):
        """打印控制台报告"""
        summary = report["summary"]
        
        print("\n" + "="*60)
        print("🎯 测试执行总结")
        print("="*60)
        
        print(f"📊 总计: {summary['total']} 个测试")
        print(f"✅ 通过: {summary['passed']} 个")
        print(f"❌ 失败: {summary['failed']} 个")
        print(f"💥 错误: {summary['errors']} 个")
        print(f"⏭️ 跳过: {summary['skipped']} 个")
        print(f"📈 成功率: {summary['success_rate']}%")
        print(f"⏱️ 平均耗时: {summary['avg_duration']}s")
        print(f"🕐 总耗时: {summary['total_duration']}s")
        
        # 失败测试详情
        failed_results = [r for r in report["results"] if r["status"] in ["failed", "error"]]
        if failed_results:
            print("\n❌ 失败测试详情:")
            for result in failed_results:
                print(f"  • {result['test_name']}: {result['error_message']}")
        
        print("="*60)
    
    def _generate_json_report(self, report: Dict[str, Any]):
        """生成JSON报告"""
        output_file = self.config.output_file or f"test_report_{int(time.time())}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 JSON报告已生成: {output_file}")
    
    def _generate_html_report(self, report: Dict[str, Any]):
        """生成HTML报告"""
        # TODO: 实现HTML报告生成
        print("HTML报告生成功能待实现")


class SmartTestRunner:
    """智能测试运行器"""
    
    def __init__(self, config: TestRunConfig = None):
        self.config = config or TestRunConfig()
        self.discovery = TestDiscovery()
        self.reporter = TestReporter(self.config)
        self.api_client = FluentAPIClient(self.config.base_url)
        self.results: List[TestResult] = []
    
    def run_all(self) -> List[TestResult]:
        """运行所有发现的测试"""
        print("🚀 启动智能测试运行器")
        
        # 发现测试套件
        suites = self.discovery.discover_suites()
        if not suites:
            print("❌ 未发现任何测试套件")
            return []
        
        # 应用过滤条件
        filtered_suites = self._filter_suites(suites)
        
        print(f"📋 将运行 {len(filtered_suites)} 个测试套件")
        
        # 执行测试
        all_results = []
        for suite in filtered_suites:
            print(f"\n🏃 运行套件: {suite.name}")
            
            if self.config.parallel and len(suite.tests) > 1:
                results = self._run_suite_parallel(suite)
            else:
                results = suite.run_suite(
                    filter_tags=self.config.filter_tags,
                    min_priority=self.config.min_priority
                )
            
            all_results.extend(results)
            
            # 快速失败检查
            if self.config.fail_fast and any(r.status in [TestStatus.FAILED, TestStatus.ERROR] for r in results):
                print("💥 检测到失败，启用快速失败模式")
                break
        
        self.results = all_results
        
        # 生成最终报告
        self.reporter.generate_final_report(all_results)
        
        return all_results
    
    def run_suites(self, suite_names: List[str]) -> List[TestResult]:
        """运行指定的测试套件"""
        suites = self.discovery.discover_suites()
        target_suites = [s for s in suites if s.name in suite_names]
        
        if not target_suites:
            print(f"❌ 未找到指定的测试套件: {suite_names}")
            return []
        
        all_results = []
        for suite in target_suites:
            results = suite.run_suite(
                filter_tags=self.config.filter_tags,
                min_priority=self.config.min_priority
            )
            all_results.extend(results)
        
        self.reporter.generate_final_report(all_results)
        return all_results
    
    def run_tests_by_tags(self, tags: List[str]) -> List[TestResult]:
        """根据标签运行测试"""
        tests = self.discovery.discover_tests_by_tags(tags)
        
        if not tests:
            print(f"❌ 未找到标签为 {tags} 的测试")
            return []
        
        print(f"🏷️ 根据标签 {tags} 找到 {len(tests)} 个测试")
        
        # 按套件分组执行
        suite_tests = {}
        for test in tests:
            suite_name = test.suite.name
            if suite_name not in suite_tests:
                suite_tests[suite_name] = []
            suite_tests[suite_name].append(test)
        
        all_results = []
        for suite_name, suite_test_list in suite_tests.items():
            print(f"\n🏃 运行套件 {suite_name} 中的 {len(suite_test_list)} 个测试")
            
            # 临时修改suite的tests列表
            original_tests = suite_test_list[0].suite.tests
            suite_test_list[0].suite.tests = suite_test_list
            
            results = suite_test_list[0].suite.run_suite()
            all_results.extend(results)
            
            # 恢复原始tests列表
            suite_test_list[0].suite.tests = original_tests
        
        self.reporter.generate_final_report(all_results)
        return all_results
    
    def run_smoke_tests(self) -> List[TestResult]:
        """运行冒烟测试"""
        return self.run_tests_by_tags(["smoke", "critical"])
    
    def run_performance_tests(self) -> List[TestResult]:
        """运行性能测试"""
        return self.run_tests_by_tags(["performance", "benchmark"])
    
    def run_integration_tests(self) -> List[TestResult]:
        """运行集成测试"""
        return self.run_tests_by_tags(["integration", "e2e"])
    
    def check_server_status(self) -> bool:
        """检查服务器状态"""
        try:
            response = self.api_client.get("/api/v1/public/system/health")
            return response.response.status_code == 200
        except Exception as e:
            print(f"❌ 服务器连接失败: {e}")
            return False
    
    def _filter_suites(self, suites: List[TestSuite]) -> List[TestSuite]:
        """过滤测试套件"""
        filtered = suites
        
        # 按套件名过滤
        if self.config.filter_suites:
            filtered = [s for s in filtered if s.name in self.config.filter_suites]
        
        # 按模式过滤（套件名）
        if self.config.filter_pattern:
            pattern = re.compile(self.config.filter_pattern, re.IGNORECASE)
            filtered = [s for s in filtered if pattern.search(s.name)]
        
        return filtered
    
    def _run_suite_parallel(self, suite: TestSuite) -> List[TestResult]:
        """并行运行测试套件"""
        print(f"🔄 并行执行 {len(suite.tests)} 个测试 (最大worker数: {self.config.max_workers})")
        
        results = []
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # 提交所有测试任务
            future_to_test = {}
            for test in suite.tests:
                future = executor.submit(self._run_single_test_safely, test)
                future_to_test[future] = test
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_test):
                test = future_to_test[future]
                try:
                    result = future.result(timeout=self.config.timeout)
                    results.append(result)
                    self.reporter.report_test_result(result)
                except Exception as e:
                    print(f"💥 测试 {test.name} 执行异常: {e}")
        
        return results
    
    def _run_single_test_safely(self, test: TestCase) -> TestResult:
        """安全执行单个测试"""
        try:
            # 准备测试环境
            context = test.suite._prepare_test_context(test)
            # 注入API客户端
            context['api'] = FluentAPIClient(self.config.base_url)
            
            return test.execute(context)
        except Exception as e:
            return TestResult(
                test_id=test.test_id,
                test_name=test.name,
                status=TestStatus.ERROR,
                error_message=f"测试执行异常: {str(e)}",
                start_time=datetime.now(),
                end_time=datetime.now()
            )


# 便捷函数
def create_runner(config: TestRunConfig = None) -> SmartTestRunner:
    """创建测试运行器"""
    return SmartTestRunner(config)


def run_all_tests(**kwargs) -> List[TestResult]:
    """运行所有测试的便捷函数"""
    config = TestRunConfig(**kwargs)
    runner = create_runner(config)
    return runner.run_all()


def run_smoke_tests(**kwargs) -> List[TestResult]:
    """运行冒烟测试的便捷函数"""
    config = TestRunConfig(**kwargs)
    runner = create_runner(config)
    return runner.run_smoke_tests()


def run_performance_tests(**kwargs) -> List[TestResult]:
    """运行性能测试的便捷函数"""
    config = TestRunConfig(**kwargs)
    runner = create_runner(config)
    return runner.run_performance_tests()


if __name__ == "__main__":
    # 简单的命令行接口
    import argparse
    
    parser = argparse.ArgumentParser(description="智能测试运行器")
    parser.add_argument("--tags", nargs="+", help="按标签过滤测试")
    parser.add_argument("--suites", nargs="+", help="指定测试套件")
    parser.add_argument("--pattern", help="测试名称模式")
    parser.add_argument("--parallel", action="store_true", help="并行执行")
    parser.add_argument("--workers", type=int, default=4, help="并行worker数")
    parser.add_argument("--smoke", action="store_true", help="运行冒烟测试")
    parser.add_argument("--performance", action="store_true", help="运行性能测试")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="API基础URL")
    parser.add_argument("--output", choices=["console", "json", "html"], default="console", help="输出格式")
    parser.add_argument("--output-file", help="输出文件")
    
    args = parser.parse_args()
    
    config = TestRunConfig(
        filter_tags=args.tags,
        filter_suites=args.suites,
        filter_pattern=args.pattern,
        parallel=args.parallel,
        max_workers=args.workers,
        base_url=args.base_url,
        output_format=args.output,
        output_file=args.output_file
    )
    
    runner = create_runner(config)
    
    if args.smoke:
        runner.run_smoke_tests()
    elif args.performance:
        runner.run_performance_tests()
    elif args.suites:
        runner.run_suites(args.suites)
    elif args.tags:
        runner.run_tests_by_tags(args.tags)
    else:
        runner.run_all() 