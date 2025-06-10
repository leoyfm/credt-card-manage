#!/usr/bin/env python3
"""
新测试框架v2.0主运行器

提供智能测试发现、执行和报告功能。
支持交互式菜单和命令行界面。
"""

import os
import sys
import argparse
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入测试框架组件
from tests.framework.core.runner import SmartTestRunner, TestRunConfig, TestDiscovery
from tests.framework.clients.api import FluentAPIClient
from tests.framework.core.suite import TestPriority


class TestFrameworkCLI:
    """测试框架命令行界面"""
    
    def __init__(self):
        self.runner: Optional[SmartTestRunner] = None
        self.discovery = TestDiscovery()
        self.base_url = "http://127.0.0.1:8000"
    
    def create_runner(self, config: TestRunConfig = None) -> SmartTestRunner:
        """创建测试运行器"""
        if config is None:
            config = TestRunConfig(base_url=self.base_url)
        
        self.runner = SmartTestRunner(config)
        return self.runner
    
    def check_server_status(self) -> bool:
        """检查服务器状态"""
        try:
            client = FluentAPIClient(self.base_url)
            return client.is_server_available()
        except:
            return False
    
    def display_welcome(self):
        """显示欢迎信息"""
        print("\n" + "="*60)
        print("🚀 信用卡管理系统 - 新测试框架 v2.0")
        print("="*60)
        print("🎯 智能测试发现、执行和报告")
        print("🔥 支持API、集成、性能、压力测试")
        print("📊 详细的测试分析和性能指标")
        print("="*60)
    
    def display_main_menu(self):
        """显示主菜单"""
        print("\n📋 主菜单:")
        print("1. 🔍 发现并查看测试套件")
        print("2. 🏃 运行所有测试")
        print("3. 🔥 运行冒烟测试")
        print("4. ⚡ 运行性能测试")
        print("5. 💪 运行压力测试")
        print("6. 🔗 运行集成测试")
        print("7. 🏷️ 按标签运行测试")
        print("8. 📁 按套件运行测试")
        print("9. 🔧 服务器状态检查")
        print("10. ⚙️ 设置配置")
        print("0. 🚪 退出")
        print("-" * 40)
    
    def discover_and_display_suites(self):
        """发现并显示测试套件"""
        print("\n🔍 正在发现测试套件...")
        
        suites = self.discovery.discover_suites()
        
        if not suites:
            print("❌ 未发现任何测试套件")
            return
        
        print(f"\n📁 发现 {len(suites)} 个测试套件:")
        print("-" * 60)
        
        total_tests = 0
        for i, suite in enumerate(suites, 1):
            test_count = len(suite.tests)
            total_tests += test_count
            
            print(f"{i:2}. 📦 {suite.name}")
            print(f"     📝 {suite.description or '无描述'}")
            print(f"     🧪 {test_count} 个测试")
            
            if suite.tags:
                print(f"     🏷️ 标签: {', '.join(suite.tags)}")
            
            # 显示测试方法
            if test_count > 0:
                print("     🔸 测试用例:")
                for test in suite.tests[:5]:  # 只显示前5个
                    tags_str = f" [{', '.join(test.tags)}]" if test.tags else ""
                    print(f"       • {test.name}{tags_str}")
                
                if test_count > 5:
                    print(f"       • ... 还有 {test_count - 5} 个测试")
            
            print()
        
        print(f"📊 总计: {len(suites)} 个套件, {total_tests} 个测试")
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n🚀 开始运行所有测试...")
        
        config = TestRunConfig(
            base_url=self.base_url,
            verbose=True,
            output_format="console"
        )
        
        runner = self.create_runner(config)
        
        start_time = time.time()
        results = runner.run_all()
        duration = time.time() - start_time
        
        self.display_summary(results, duration)
    
    def run_smoke_tests(self):
        """运行冒烟测试"""
        print("\n🔥 开始运行冒烟测试...")
        
        config = TestRunConfig(
            base_url=self.base_url,
            filter_tags=["smoke", "critical"],
            verbose=True
        )
        
        runner = self.create_runner(config)
        
        start_time = time.time()
        results = runner.run_smoke_tests()
        duration = time.time() - start_time
        
        self.display_summary(results, duration)
    
    def run_performance_tests(self):
        """运行性能测试"""
        print("\n⚡ 开始运行性能测试...")
        
        config = TestRunConfig(
            base_url=self.base_url,
            filter_tags=["performance", "benchmark"],
            verbose=True
        )
        
        runner = self.create_runner(config)
        
        start_time = time.time()
        results = runner.run_performance_tests()
        duration = time.time() - start_time
        
        self.display_summary(results, duration)
        
        # 显示性能指标
        if runner:
            perf_summary = runner.api_client.get_performance_summary()
            if perf_summary:
                print("\n📊 性能指标:")
                print(f"  • 平均响应时间: {perf_summary.get('avg_duration', 0):.3f}s")
                print(f"  • 最快响应: {perf_summary.get('min_duration', 0):.3f}s")
                print(f"  • 最慢响应: {perf_summary.get('max_duration', 0):.3f}s")
                print(f"  • 成功率: {perf_summary.get('success_rate', 0):.1f}%")
    
    def run_stress_tests(self):
        """运行压力测试"""
        print("\n💪 开始运行压力测试...")
        print("⚠️ 压力测试可能需要较长时间，请耐心等待...")
        
        config = TestRunConfig(
            base_url=self.base_url,
            filter_tags=["stress"],
            verbose=True,
            timeout=300  # 5分钟超时
        )
        
        runner = self.create_runner(config)
        
        start_time = time.time()
        results = runner.run_tests_by_tags(["stress"])
        duration = time.time() - start_time
        
        self.display_summary(results, duration)
    
    def run_integration_tests(self):
        """运行集成测试"""
        print("\n🔗 开始运行集成测试...")
        
        # 检查服务器状态
        if not self.check_server_status():
            print("❌ 服务器未运行！集成测试需要服务器运行。")
            print("请在另一个终端中运行: python start.py dev")
            return
        
        config = TestRunConfig(
            base_url=self.base_url,
            filter_tags=["integration", "e2e"],
            verbose=True
        )
        
        runner = self.create_runner(config)
        
        start_time = time.time()
        results = runner.run_integration_tests()
        duration = time.time() - start_time
        
        self.display_summary(results, duration)
    
    def run_tests_by_tags(self):
        """按标签运行测试"""
        print("\n🏷️ 按标签运行测试")
        print("常用标签: smoke, performance, stress, integration, unit, api")
        
        tags_input = input("请输入标签 (多个标签用空格分隔): ").strip()
        if not tags_input:
            print("❌ 未输入标签")
            return
        
        tags = tags_input.split()
        print(f"\n🔍 搜索标签: {tags}")
        
        config = TestRunConfig(
            base_url=self.base_url,
            filter_tags=tags,
            verbose=True
        )
        
        runner = self.create_runner(config)
        
        start_time = time.time()
        results = runner.run_tests_by_tags(tags)
        duration = time.time() - start_time
        
        self.display_summary(results, duration)
    
    def run_tests_by_suites(self):
        """按套件运行测试"""
        print("\n📁 按测试套件运行")
        
        # 先发现套件
        suites = self.discovery.discover_suites()
        if not suites:
            print("❌ 未发现任何测试套件")
            return
        
        print("\n可用的测试套件:")
        for i, suite in enumerate(suites, 1):
            print(f"{i}. {suite.name} ({len(suite.tests)} 个测试)")
        
        try:
            choice = input("\n请选择套件编号 (多个用空格分隔): ").strip()
            if not choice:
                print("❌ 未选择套件")
                return
            
            selected_indices = [int(x) - 1 for x in choice.split()]
            selected_suites = [suites[i].name for i in selected_indices if 0 <= i < len(suites)]
            
            if not selected_suites:
                print("❌ 无效的套件选择")
                return
            
            print(f"\n🏃 运行套件: {', '.join(selected_suites)}")
            
            config = TestRunConfig(
                base_url=self.base_url,
                filter_suites=selected_suites,
                verbose=True
            )
            
            runner = self.create_runner(config)
            
            start_time = time.time()
            results = runner.run_suites(selected_suites)
            duration = time.time() - start_time
            
            self.display_summary(results, duration)
            
        except (ValueError, IndexError):
            print("❌ 无效的输入")
    
    def check_and_display_server_status(self):
        """检查并显示服务器状态"""
        print("\n🔧 检查服务器状态...")
        
        is_available = self.check_server_status()
        
        if is_available:
            print("✅ 服务器运行正常")
            
            # 获取服务器信息
            try:
                client = FluentAPIClient(self.base_url)
                health_response = client.health_check()
                
                if health_response.response.status_code == 200:
                    data = health_response.data
                    if data:
                        print(f"🌐 API版本: {data.get('version', 'unknown')}")
                        print(f"⏰ 服务器时间: {data.get('timestamp', 'unknown')}")
                        print(f"💽 数据库状态: {data.get('database', 'unknown')}")
                
            except Exception as e:
                print(f"⚠️ 获取服务器详细信息失败: {e}")
        else:
            print("❌ 服务器未运行或无法连接")
            print(f"🔗 检查地址: {self.base_url}")
            print("💡 启动命令: python start.py dev")
    
    def configure_settings(self):
        """配置设置"""
        print("\n⚙️ 配置设置")
        print(f"当前API地址: {self.base_url}")
        
        new_url = input(f"输入新的API地址 (回车保持当前): ").strip()
        if new_url:
            self.base_url = new_url
            print(f"✅ API地址已更新为: {self.base_url}")
    
    def display_summary(self, results: List, duration: float):
        """显示测试结果摘要"""
        if not results:
            print("\n❌ 没有测试结果")
            return
        
        from tests.framework.core.suite import TestStatus
        
        total = len(results)
        passed = sum(1 for r in results if r.status == TestStatus.PASSED)
        failed = sum(1 for r in results if r.status == TestStatus.FAILED)
        errors = sum(1 for r in results if r.status == TestStatus.ERROR)
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\n🎯 测试执行摘要 (耗时: {duration:.2f}s)")
        print("=" * 50)
        print(f"📊 总计: {total}")
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        print(f"💥 错误: {errors}")
        print(f"📈 成功率: {success_rate:.1f}%")
        
        if failed > 0 or errors > 0:
            print(f"\n❌ 失败的测试:")
            for result in results:
                if result.status in [TestStatus.FAILED, TestStatus.ERROR]:
                    print(f"  • {result.test_name}: {result.error_message}")
    
    def run_interactive(self):
        """运行交互式界面"""
        self.display_welcome()
        
        while True:
            try:
                self.display_main_menu()
                choice = input("请选择操作 (0-10): ").strip()
                
                if choice == "0":
                    print("\n👋 再见！")
                    break
                elif choice == "1":
                    self.discover_and_display_suites()
                elif choice == "2":
                    self.run_all_tests()
                elif choice == "3":
                    self.run_smoke_tests()
                elif choice == "4":
                    self.run_performance_tests()
                elif choice == "5":
                    self.run_stress_tests()
                elif choice == "6":
                    self.run_integration_tests()
                elif choice == "7":
                    self.run_tests_by_tags()
                elif choice == "8":
                    self.run_tests_by_suites()
                elif choice == "9":
                    self.check_and_display_server_status()
                elif choice == "10":
                    self.configure_settings()
                else:
                    print("❌ 无效选择，请重试")
                
                input("\n按回车键继续...")
                
            except KeyboardInterrupt:
                print("\n\n👋 用户中断，退出程序")
                break
            except Exception as e:
                print(f"\n💥 发生错误: {e}")
                input("按回车键继续...")


def create_argument_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="信用卡管理系统新测试框架v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python run_tests_v2.py                    # 交互式模式
  python run_tests_v2.py --all              # 运行所有测试
  python run_tests_v2.py --smoke            # 运行冒烟测试
  python run_tests_v2.py --performance      # 运行性能测试
  python run_tests_v2.py --tags smoke api   # 按标签运行
  python run_tests_v2.py --suites cards     # 按套件运行
  python run_tests_v2.py --parallel --workers 4  # 并行执行
        """
    )
    
    # 运行模式
    run_group = parser.add_mutually_exclusive_group()
    run_group.add_argument("--all", action="store_true", help="运行所有测试")
    run_group.add_argument("--smoke", action="store_true", help="运行冒烟测试")
    run_group.add_argument("--performance", action="store_true", help="运行性能测试")
    run_group.add_argument("--stress", action="store_true", help="运行压力测试")
    run_group.add_argument("--integration", action="store_true", help="运行集成测试")
    run_group.add_argument("--discover", action="store_true", help="发现并显示测试套件")
    
    # 过滤选项
    parser.add_argument("--tags", nargs="+", help="按标签过滤测试")
    parser.add_argument("--suites", nargs="+", help="按套件名称过滤测试")
    parser.add_argument("--pattern", help="按名称模式过滤测试")
    
    # 执行选项
    parser.add_argument("--parallel", action="store_true", help="并行执行测试")
    parser.add_argument("--workers", type=int, default=4, help="并行工作进程数")
    parser.add_argument("--timeout", type=int, help="测试超时时间(秒)")
    parser.add_argument("--fail-fast", action="store_true", help="遇到失败立即停止")
    
    # 输出选项
    parser.add_argument("--output", choices=["console", "json", "html"], 
                       default="console", help="输出格式")
    parser.add_argument("--output-file", help="输出文件路径")
    parser.add_argument("--verbose", action="store_true", help="详细输出")
    parser.add_argument("--quiet", action="store_true", help="静默模式")
    
    # 环境选项
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", 
                       help="API服务器地址")
    parser.add_argument("--check-server", action="store_true", help="检查服务器状态")
    
    return parser


def main():
    """主函数"""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # 创建CLI实例
    cli = TestFrameworkCLI()
    cli.base_url = args.base_url
    
    # 检查服务器状态
    if args.check_server:
        cli.check_and_display_server_status()
        return
    
    # 如果没有指定任何参数，运行交互式模式
    if len(sys.argv) == 1:
        cli.run_interactive()
        return
    
    # 命令行模式
    try:
        # 创建运行配置
        config = TestRunConfig(
            filter_tags=args.tags,
            filter_suites=args.suites,
            filter_pattern=args.pattern,
            parallel=args.parallel,
            max_workers=args.workers,
            timeout=args.timeout,
            fail_fast=args.fail_fast,
            output_format=args.output,
            output_file=args.output_file,
            verbose=args.verbose and not args.quiet,
            base_url=args.base_url
        )
        
        runner = cli.create_runner(config)
        
        # 执行相应的测试
        start_time = time.time()
        
        if args.discover:
            cli.discover_and_display_suites()
            return
        elif args.all:
            results = runner.run_all()
        elif args.smoke:
            results = runner.run_smoke_tests()
        elif args.performance:
            results = runner.run_performance_tests()
        elif args.stress:
            results = runner.run_tests_by_tags(["stress"])
        elif args.integration:
            results = runner.run_integration_tests()
        elif args.tags:
            results = runner.run_tests_by_tags(args.tags)
        elif args.suites:
            results = runner.run_suites(args.suites)
        else:
            # 默认运行所有测试
            results = runner.run_all()
        
        duration = time.time() - start_time
        
        # 显示结果摘要
        if not args.quiet:
            cli.display_summary(results, duration)
        
        # 根据测试结果设置退出代码
        from tests.framework.core.suite import TestStatus
        failed_count = sum(1 for r in results if r.status in [TestStatus.FAILED, TestStatus.ERROR])
        sys.exit(0 if failed_count == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"错误: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()