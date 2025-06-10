"""
智能测试运行器

支持自动发现测试、智能执行策略、丰富的报告生成。

Usage:
    runner = SmartTestRunner()
    runner.discover_tests("tests/suites/")
    results = runner.run_all()
"""

import os
import sys
import time
import importlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import traceback

logger = logging.getLogger(__name__)


class TestResult:
    """测试结果"""
    
    def __init__(self, test_name: str, test_func: Callable):
        self.test_name = test_name
        self.test_func = test_func
        self.status = "PENDING"
        self.start_time = None
        self.end_time = None
        self.duration = 0
        self.error = None
        self.traceback = None
        self.performance_metrics = {}
        self.context = {}
    
    def mark_started(self):
        """标记测试开始"""
        self.start_time = time.time()
        self.status = "RUNNING"
    
    def mark_passed(self):
        """标记测试通过"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = "PASSED"
    
    def mark_failed(self, error: Exception):
        """标记测试失败"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = "FAILED"
        self.error = str(error)
        self.traceback = traceback.format_exc()
    
    def mark_skipped(self, reason: str = ""):
        """标记测试跳过"""
        self.status = "SKIPPED"
        self.error = reason
    
    def to_dict(self):
        """转换为字典"""
        return {
            "test_name": self.test_name,
            "status": self.status,
            "duration": self.duration,
            "error": self.error,
            "performance_metrics": self.performance_metrics,
            "context": self.context
        }


class TestSuiteResult:
    """测试套件结果"""
    
    def __init__(self, suite_name: str):
        self.suite_name = suite_name
        self.test_results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
        self.duration = 0
    
    def add_test_result(self, result: TestResult):
        """添加测试结果"""
        self.test_results.append(result)
    
    @property
    def total_tests(self) -> int:
        """总测试数"""
        return len(self.test_results)
    
    @property
    def passed_tests(self) -> int:
        """通过测试数"""
        return len([r for r in self.test_results if r.status == "PASSED"])
    
    @property
    def failed_tests(self) -> int:
        """失败测试数"""
        return len([r for r in self.test_results if r.status == "FAILED"])
    
    @property
    def skipped_tests(self) -> int:
        """跳过测试数"""
        return len([r for r in self.test_results if r.status == "SKIPPED"])
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_tests == 0:
            return 0.0
        return (self.passed_tests / self.total_tests) * 100
    
    def to_dict(self):
        """转换为字典"""
        return {
            "suite_name": self.suite_name,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests,
            "skipped_tests": self.skipped_tests,
            "success_rate": self.success_rate,
            "duration": self.duration,
            "test_results": [r.to_dict() for r in self.test_results]
        }


class SmartTestRunner:
    """智能测试运行器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.discovered_suites = {}
        self.execution_results = []
        self.total_start_time = None
        self.total_end_time = None
        
        # 配置默认值
        self.max_workers = self.config.get("max_workers", 4)
        self.parallel_execution = self.config.get("parallel_execution", False)
        self.fail_fast = self.config.get("fail_fast", False)
        self.verbose = self.config.get("verbose", True)
        
        # 设置日志
        self._setup_logging()
    
    def _setup_logging(self):
        """设置日志"""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def discover_tests(self, test_path: str = "tests/suites/"):
        """自动发现测试"""
        logger.info(f"🔍 在 {test_path} 中发现测试...")
        
        test_dir = Path(test_path)
        if not test_dir.exists():
            logger.error(f"测试目录不存在: {test_path}")
            return
        
        # 添加到Python路径
        if str(test_dir.parent) not in sys.path:
            sys.path.insert(0, str(test_dir.parent))
        
        # 递归发现测试文件
        test_files = list(test_dir.rglob("*.py"))
        
        for test_file in test_files:
            if test_file.name.startswith("__"):
                continue
            
            try:
                self._load_test_file(test_file)
            except Exception as e:
                logger.warning(f"加载测试文件失败 {test_file}: {e}")
        
        logger.info(f"✅ 发现 {len(self.discovered_suites)} 个测试套件")
        
        # 打印发现的测试套件
        for suite_name, suite_info in self.discovered_suites.items():
            test_count = len(suite_info['tests'])
            logger.info(f"  📦 {suite_name}: {test_count} 个测试")
    
    def _load_test_file(self, test_file: Path):
        """加载测试文件"""
        # 构建模块名
        relative_path = test_file.relative_to(Path.cwd())
        module_name = str(relative_path).replace(os.path.sep, ".").replace(".py", "")
        
        try:
            # 导入模块
            module = importlib.import_module(module_name)
            
            # 查找测试套件类
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    hasattr(attr, '_test_suite_name')):
                    
                    suite_name = attr._test_suite_name
                    suite_description = getattr(attr, '_test_suite_description', "")
                    
                    # 提取测试方法
                    tests = self._extract_tests_from_class(attr)
                    
                    if tests:
                        self.discovered_suites[suite_name] = {
                            'class': attr,
                            'description': suite_description,
                            'tests': tests,
                            'file': str(test_file)
                        }
                        
                        logger.debug(f"  发现测试套件: {suite_name} ({len(tests)} 个测试)")
        
        except Exception as e:
            logger.warning(f"导入模块失败 {module_name}: {e}")
    
    def _extract_tests_from_class(self, test_class) -> List[Dict[str, Any]]:
        """从测试类中提取测试方法"""
        tests = []
        
        for attr_name in dir(test_class):
            if not attr_name.startswith("test_"):
                continue
            
            attr = getattr(test_class, attr_name)
            if callable(attr) and hasattr(attr, '_is_test_method'):
                test_info = {
                    'name': attr_name,
                    'function': attr,
                    'tags': getattr(attr, '_test_tags', []),
                    'priority': getattr(attr, '_priority', 999),
                    'description': getattr(attr, '_test_description', ""),
                    'is_performance': hasattr(attr, '_is_performance_test'),
                    'timeout': getattr(attr, '_timeout', None),
                    'retry_times': getattr(attr, '_retry_times', 0)
                }
                tests.append(test_info)
        
        # 按优先级排序
        tests.sort(key=lambda x: x['priority'])
        return tests
    
    def run_all(self, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """运行所有测试"""
        logger.info("🚀 开始执行测试...")
        
        self.total_start_time = time.time()
        
        # 应用过滤器
        suites_to_run = self._apply_filters(filters or {})
        
        if not suites_to_run:
            logger.warning("没有找到符合条件的测试")
            return self._generate_final_report([])
        
        # 执行测试套件
        if self.parallel_execution:
            suite_results = self._run_suites_parallel(suites_to_run)
        else:
            suite_results = self._run_suites_sequential(suites_to_run)
        
        self.total_end_time = time.time()
        
        # 生成最终报告
        return self._generate_final_report(suite_results)
    
    def _apply_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """应用过滤器"""
        suites_to_run = {}
        
        suite_filter = filters.get('suites', [])
        tag_filter = filters.get('tags', [])
        priority_filter = filters.get('max_priority', 999)
        
        for suite_name, suite_info in self.discovered_suites.items():
            # 套件过滤
            if suite_filter and suite_name not in suite_filter:
                continue
            
            # 过滤测试
            filtered_tests = []
            for test in suite_info['tests']:
                # 标签过滤
                if tag_filter:
                    test_tags = test.get('tags', [])
                    if not any(tag in test_tags for tag in tag_filter):
                        continue
                
                # 优先级过滤
                if test.get('priority', 999) > priority_filter:
                    continue
                
                filtered_tests.append(test)
            
            if filtered_tests:
                suite_info_copy = suite_info.copy()
                suite_info_copy['tests'] = filtered_tests
                suites_to_run[suite_name] = suite_info_copy
        
        return suites_to_run
    
    def _run_suites_sequential(self, suites: Dict[str, Any]) -> List[TestSuiteResult]:
        """顺序执行测试套件"""
        results = []
        
        for suite_name, suite_info in suites.items():
            logger.info(f"📦 执行测试套件: {suite_name}")
            
            suite_result = self._run_single_suite(suite_name, suite_info)
            results.append(suite_result)
            
            # 快速失败检查
            if self.fail_fast and suite_result.failed_tests > 0:
                logger.warning("启用快速失败，停止执行")
                break
        
        return results
    
    def _run_suites_parallel(self, suites: Dict[str, Any]) -> List[TestSuiteResult]:
        """并行执行测试套件"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有套件任务
            future_to_suite = {
                executor.submit(self._run_single_suite, suite_name, suite_info): suite_name
                for suite_name, suite_info in suites.items()
            }
            
            # 收集结果
            for future in as_completed(future_to_suite):
                suite_name = future_to_suite[future]
                try:
                    suite_result = future.result()
                    results.append(suite_result)
                    
                    # 快速失败检查
                    if self.fail_fast and suite_result.failed_tests > 0:
                        logger.warning("启用快速失败，取消其他任务")
                        for f in future_to_suite:
                            f.cancel()
                        break
                        
                except Exception as e:
                    logger.error(f"套件 {suite_name} 执行异常: {e}")
        
        return results
    
    def _run_single_suite(self, suite_name: str, suite_info: Dict[str, Any]) -> TestSuiteResult:
        """执行单个测试套件"""
        suite_result = TestSuiteResult(suite_name)
        suite_result.start_time = time.time()
        
        # 创建套件实例
        suite_class = suite_info['class']
        suite_instance = suite_class()
        
        # 执行测试
        for test_info in suite_info['tests']:
            test_result = self._run_single_test(
                suite_instance, 
                test_info,
                f"{suite_name}::{test_info['name']}"
            )
            suite_result.add_test_result(test_result)
            
            # 打印测试结果
            self._print_test_result(test_result)
        
        suite_result.end_time = time.time()
        suite_result.duration = suite_result.end_time - suite_result.start_time
        
        # 打印套件总结
        self._print_suite_summary(suite_result)
        
        return suite_result
    
    def _run_single_test(self, suite_instance: Any, test_info: Dict[str, Any], full_name: str) -> TestResult:
        """执行单个测试"""
        test_result = TestResult(full_name, test_info['function'])
        test_result.mark_started()
        
        try:
            # 执行测试方法
            test_method = getattr(suite_instance, test_info['name'])
            test_method()
            
            test_result.mark_passed()
            
        except Exception as e:
            test_result.mark_failed(e)
            logger.error(f"测试失败 {full_name}: {e}")
        
        return test_result
    
    def _print_test_result(self, result: TestResult):
        """打印测试结果"""
        if result.status == "PASSED":
            icon = "✅"
            color = ""
        elif result.status == "FAILED":
            icon = "❌"
            color = ""
        else:
            icon = "⏭️"
            color = ""
        
        duration_str = f"({result.duration:.3f}s)" if result.duration > 0 else ""
        logger.info(f"  {icon} {result.test_name} {duration_str}")
        
        if result.status == "FAILED" and self.verbose:
            logger.error(f"    错误: {result.error}")
    
    def _print_suite_summary(self, suite_result: TestSuiteResult):
        """打印套件总结"""
        logger.info(f"📋 套件 {suite_result.suite_name} 总结:")
        logger.info(f"  总测试数: {suite_result.total_tests}")
        logger.info(f"  通过: {suite_result.passed_tests}")
        logger.info(f"  失败: {suite_result.failed_tests}")
        logger.info(f"  跳过: {suite_result.skipped_tests}")
        logger.info(f"  成功率: {suite_result.success_rate:.1f}%")
        logger.info(f"  耗时: {suite_result.duration:.3f}s")
        logger.info("")
    
    def _generate_final_report(self, suite_results: List[TestSuiteResult]) -> Dict[str, Any]:
        """生成最终报告"""
        total_duration = (self.total_end_time - self.total_start_time) if self.total_end_time else 0
        
        # 汇总统计
        total_tests = sum(s.total_tests for s in suite_results)
        total_passed = sum(s.passed_tests for s in suite_results)
        total_failed = sum(s.failed_tests for s in suite_results)
        total_skipped = sum(s.skipped_tests for s in suite_results)
        
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "summary": {
                "total_suites": len(suite_results),
                "total_tests": total_tests,
                "passed_tests": total_passed,
                "failed_tests": total_failed,
                "skipped_tests": total_skipped,
                "success_rate": overall_success_rate,
                "total_duration": total_duration
            },
            "suite_results": [s.to_dict() for s in suite_results],
            "timestamp": time.time()
        }
        
        # 打印最终总结
        self._print_final_summary(report)
        
        # 保存报告
        self._save_report(report)
        
        return report
    
    def _print_final_summary(self, report: Dict[str, Any]):
        """打印最终总结"""
        summary = report["summary"]
        
        logger.info("=" * 60)
        logger.info("🎯 测试执行总结")
        logger.info("=" * 60)
        logger.info(f"📦 测试套件: {summary['total_suites']}")
        logger.info(f"🧪 总测试数: {summary['total_tests']}")
        logger.info(f"✅ 通过: {summary['passed_tests']}")
        logger.info(f"❌ 失败: {summary['failed_tests']}")
        logger.info(f"⏭️ 跳过: {summary['skipped_tests']}")
        logger.info(f"📊 成功率: {summary['success_rate']:.1f}%")
        logger.info(f"⏱️ 总耗时: {summary['total_duration']:.3f}s")
        
        if summary['failed_tests'] > 0:
            logger.info("")
            logger.info("❌ 失败测试:")
            for suite_result in report["suite_results"]:
                for test_result in suite_result["test_results"]:
                    if test_result["status"] == "FAILED":
                        logger.info(f"  - {test_result['test_name']}: {test_result['error']}")
        
        logger.info("=" * 60)
    
    def _save_report(self, report: Dict[str, Any]):
        """保存测试报告"""
        # 保存JSON报告
        reports_dir = Path("tests/reports")
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = int(time.time())
        json_file = reports_dir / f"test_report_{timestamp}.json"
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 测试报告已保存: {json_file}")
    
    def run_with_filters(self, **filters) -> Dict[str, Any]:
        """使用过滤器运行测试"""
        return self.run_all(filters)
    
    def run_by_tags(self, tags: List[str]) -> Dict[str, Any]:
        """按标签运行测试"""
        return self.run_all({"tags": tags})
    
    def run_suite(self, suite_name: str) -> Dict[str, Any]:
        """运行指定套件"""
        return self.run_all({"suites": [suite_name]})
    
    def list_discovered_tests(self):
        """列出发现的测试"""
        logger.info("📋 发现的测试套件:")
        
        for suite_name, suite_info in self.discovered_suites.items():
            logger.info(f"\n📦 {suite_name}")
            logger.info(f"   描述: {suite_info.get('description', '无描述')}")
            logger.info(f"   文件: {suite_info['file']}")
            logger.info(f"   测试数: {len(suite_info['tests'])}")
            
            for test in suite_info['tests']:
                tags_str = f"[{', '.join(test['tags'])}]" if test['tags'] else ""
                logger.info(f"     🧪 {test['name']} {tags_str}")
                if test['description']:
                    logger.info(f"        {test['description']}")


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="智能测试运行器")
    parser.add_argument("--path", default="tests/suites/", help="测试路径")
    parser.add_argument("--suite", help="指定运行的套件")
    parser.add_argument("--tags", nargs="+", help="按标签过滤")
    parser.add_argument("--parallel", action="store_true", help="并行执行")
    parser.add_argument("--fail-fast", action="store_true", help="快速失败")
    parser.add_argument("--list", action="store_true", help="列出所有测试")
    parser.add_argument("--verbose", action="store_true", default=True, help="详细输出")
    
    args = parser.parse_args()
    
    # 创建运行器
    config = {
        "parallel_execution": args.parallel,
        "fail_fast": args.fail_fast,
        "verbose": args.verbose
    }
    
    runner = SmartTestRunner(config)
    
    # 发现测试
    runner.discover_tests(args.path)
    
    if args.list:
        runner.list_discovered_tests()
        return
    
    # 构建过滤器
    filters = {}
    if args.suite:
        filters["suites"] = [args.suite]
    if args.tags:
        filters["tags"] = args.tags
    
    # 运行测试
    results = runner.run_all(filters)
    
    # 退出码
    exit_code = 0 if results["summary"]["failed_tests"] == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 