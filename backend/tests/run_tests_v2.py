#!/usr/bin/env python3
"""
测试框架 v2.0 主运行器

支持交互模式和命令行模式，提供智能的测试发现、执行和报告功能
"""

import sys
import argparse
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.framework.core.runner import SmartTestRunner
from tests.framework.clients.api import FluentAPIClient


class TestsV2Runner:
    """测试框架v2.0主运行器"""
    
    def __init__(self):
        self.runner = SmartTestRunner()
        self.api_client = FluentAPIClient()
    
    def interactive_mode(self):
        """交互模式"""
        print("🧪 信用卡管理系统测试框架 v2.0")
        print("=" * 50)
        
        while True:
            print("\n📋 测试选项:")
            print("1. 🔍 发现所有测试")
            print("2. 🚀 运行全部测试")
            print("3. 🏷️  按标签运行测试")
            print("4. 📦 按套件运行测试")
            print("5. ⚡ 运行烟雾测试")
            print("6. 🏃 运行性能测试")
            print("7. 💪 运行压力测试")
            print("8. 🔧 检查服务器状态")
            print("9. 📊 查看测试统计")
            print("0. 退出")
            
            choice = input("\n请选择操作 (0-9): ").strip()
            
            if choice == "0":
                print("👋 再见!")
                break
            elif choice == "1":
                self.discover_tests()
            elif choice == "2":
                self.run_all_tests()
            elif choice == "3":
                self.run_tests_by_tags()
            elif choice == "4":
                self.run_tests_by_suite()
            elif choice == "5":
                self.run_smoke_tests()
            elif choice == "6":
                self.run_performance_tests()
            elif choice == "7":
                self.run_stress_tests()
            elif choice == "8":
                self.check_server_status()
            elif choice == "9":
                self.show_test_statistics()
            else:
                print("❌ 无效选择，请重试")
    
    def discover_tests(self):
        """发现所有测试"""
        print("\n🔍 正在发现测试...")
        
        tests = self.runner.discover_tests()
        
        print(f"📋 发现 {len(tests)} 个测试:")
        
        # 按套件分组显示
        suites = {}
        for test in tests:
            suite_name = test.get('suite', 'Unknown')
            if suite_name not in suites:
                suites[suite_name] = []
            suites[suite_name].append(test)
        
        for suite_name, suite_tests in suites.items():
            print(f"\n📦 {suite_name} ({len(suite_tests)} 个测试)")
            for test in suite_tests[:5]:  # 只显示前5个
                print(f"   • {test.get('name', 'Unknown')}")
            if len(suite_tests) > 5:
                print(f"   ... 还有 {len(suite_tests) - 5} 个测试")
    
    def run_all_tests(self):
        """运行全部测试"""
        print("\n🚀 运行全部测试...")
        
        confirm = input("⚠️  这可能需要较长时间，确定继续? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 已取消")
            return
        
        results = self.runner.run_all_tests()
        self.display_results(results)
    
    def run_tests_by_tags(self):
        """按标签运行测试"""
        print("\n🏷️  可用标签:")
        tags = ["smoke", "api", "performance", "stress", "unit", "integration"]
        for i, tag in enumerate(tags, 1):
            print(f"{i}. {tag}")
        
        choice = input("\n请输入标签名称或编号: ").strip()
        
        # 处理编号输入
        if choice.isdigit():
            tag_index = int(choice) - 1
            if 0 <= tag_index < len(tags):
                tag = tags[tag_index]
            else:
                print("❌ 无效编号")
                return
        else:
            tag = choice
        
        print(f"\n🚀 运行标签 '{tag}' 的测试...")
        results = self.runner.run_tests_by_tags([tag])
        self.display_results(results)
    
    def run_tests_by_suite(self):
        """按套件运行测试"""
        print("\n📦 可用测试套件:")
        suites = [
            "信用卡管理API",
            "交易管理API", 
            "年费规则管理",
            "智能推荐API",
            "还款提醒API",
            "仪表板统计API",
            "用户管理API"
        ]
        
        for i, suite in enumerate(suites, 1):
            print(f"{i}. {suite}")
        
        choice = input("\n请输入套件名称或编号: ").strip()
        
        # 处理编号输入
        if choice.isdigit():
            suite_index = int(choice) - 1
            if 0 <= suite_index < len(suites):
                suite = suites[suite_index]
            else:
                print("❌ 无效编号")
                return
        else:
            suite = choice
        
        print(f"\n🚀 运行套件 '{suite}' 的测试...")
        results = self.runner.run_tests_by_suite(suite)
        self.display_results(results)
    
    def run_smoke_tests(self):
        """运行烟雾测试"""
        print("\n⚡ 运行烟雾测试 (快速验证核心功能)...")
        results = self.runner.run_smoke_tests()
        self.display_results(results)
    
    def run_performance_tests(self):
        """运行性能测试"""
        print("\n🏃 运行性能测试...")
        confirm = input("⚠️  性能测试可能影响系统性能，确定继续? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 已取消")
            return
        
        results = self.runner.run_performance_tests()
        self.display_results(results)
    
    def run_stress_tests(self):
        """运行压力测试"""
        print("\n💪 运行压力测试...")
        confirm = input("⚠️  压力测试会产生高负载，确定继续? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ 已取消")
            return
        
        results = self.runner.run_stress_tests()
        self.display_results(results)
    
    def check_server_status(self):
        """检查服务器状态"""
        print("\n🔧 检查服务器状态...")
        
        try:
            # 检查基本连接
            response = self.api_client.get("/health")
            if response.status_code == 200:
                print("✅ 服务器运行正常")
                
                # 检查具体服务状态
                print("\n📊 服务状态详情:")
                
                # 检查数据库连接
                try:
                    db_response = self.api_client.get("/health/db")
                    if db_response.status_code == 200:
                        print("✅ 数据库连接正常")
                    else:
                        print("❌ 数据库连接异常")
                except:
                    print("❌ 无法检查数据库状态")
                
                # 检查认证服务
                try:
                    auth_response = self.api_client.get("/api/v1/public/health")
                    if auth_response.status_code == 200:
                        print("✅ 认证服务正常")
                    else:
                        print("❌ 认证服务异常")
                except:
                    print("❌ 无法检查认证服务")
                
            else:
                print(f"❌ 服务器响应异常: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 无法连接到服务器: {e}")
            print("\n💡 请确保:")
            print("1. 服务器正在运行 (python start.py dev)")
            print("2. 服务器地址正确 (默认: http://localhost:8000)")
            print("3. 网络连接正常")
    
    def show_test_statistics(self):
        """显示测试统计"""
        print("\n📊 测试统计信息...")
        
        stats = self.runner.get_test_statistics()
        
        print(f"📋 总测试数: {stats.get('total_tests', 0)}")
        print(f"📦 测试套件数: {stats.get('total_suites', 0)}")
        print(f"🏷️  标签数: {stats.get('total_tags', 0)}")
        
        # 按类型统计
        by_type = stats.get('by_type', {})
        print(f"\n📊 按类型分布:")
        for test_type, count in by_type.items():
            print(f"   {test_type}: {count}")
        
        # 按套件统计
        by_suite = stats.get('by_suite', {})
        print(f"\n📦 按套件分布:")
        for suite, count in by_suite.items():
            print(f"   {suite}: {count}")
    
    def display_results(self, results: Dict[str, Any]):
        """显示测试结果"""
        print("\n" + "=" * 50)
        print("📊 测试结果")
        print("=" * 50)
        
        total = results.get('total', 0)
        passed = results.get('passed', 0)
        failed = results.get('failed', 0)
        skipped = results.get('skipped', 0)
        
        print(f"总计: {total}")
        print(f"✅ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        print(f"⏭️  跳过: {skipped}")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"📈 成功率: {success_rate:.1f}%")
        
        # 显示失败的测试
        failures = results.get('failures', [])
        if failures:
            print(f"\n❌ 失败的测试 ({len(failures)}):")
            for failure in failures[:10]:  # 只显示前10个
                print(f"   • {failure.get('name', 'Unknown')}: {failure.get('error', 'Unknown error')}")
            if len(failures) > 10:
                print(f"   ... 还有 {len(failures) - 10} 个失败")
        
        # 显示性能数据
        performance = results.get('performance', {})
        if performance:
            print(f"\n⚡ 性能数据:")
            print(f"   执行时间: {performance.get('total_time', 0):.2f}s")
            print(f"   平均响应时间: {performance.get('avg_response_time', 0):.2f}s")
    
    def command_line_mode(self, args):
        """命令行模式"""
        if args.discover:
            self.discover_tests()
        elif args.all:
            self.run_all_tests()
        elif args.tags:
            results = self.runner.run_tests_by_tags(args.tags)
            self.display_results(results)
        elif args.suite:
            results = self.runner.run_tests_by_suite(args.suite)
            self.display_results(results)
        elif args.smoke:
            self.run_smoke_tests()
        elif args.performance:
            self.run_performance_tests()
        elif args.stress:
            self.run_stress_tests()
        elif args.check:
            self.check_server_status()
        elif args.stats:
            self.show_test_statistics()
        else:
            print("❌ 请指定要执行的操作，使用 -h 查看帮助")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="信用卡管理系统测试框架 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s                          # 交互模式
  %(prog)s --all                    # 运行所有测试
  %(prog)s --tags smoke api         # 运行特定标签的测试
  %(prog)s --suite "信用卡管理API"   # 运行特定套件的测试
  %(prog)s --smoke                  # 运行烟雾测试
  %(prog)s --performance            # 运行性能测试
  %(prog)s --stress                 # 运行压力测试
  %(prog)s --check                  # 检查服务器状态
  %(prog)s --stats                  # 显示测试统计
        """
    )
    
    # 测试执行选项
    execution_group = parser.add_argument_group('测试执行')
    execution_group.add_argument('--all', action='store_true', help='运行所有测试')
    execution_group.add_argument('--tags', nargs='+', help='按标签运行测试')
    execution_group.add_argument('--suite', help='按套件运行测试')
    execution_group.add_argument('--smoke', action='store_true', help='运行烟雾测试')
    execution_group.add_argument('--performance', action='store_true', help='运行性能测试')
    execution_group.add_argument('--stress', action='store_true', help='运行压力测试')
    
    # 信息查看选项
    info_group = parser.add_argument_group('信息查看')
    info_group.add_argument('--discover', action='store_true', help='发现所有测试')
    info_group.add_argument('--check', action='store_true', help='检查服务器状态')
    info_group.add_argument('--stats', action='store_true', help='显示测试统计')
    
    # 运行配置选项
    config_group = parser.add_argument_group('运行配置')
    config_group.add_argument('--parallel', type=int, help='并行执行的进程数')
    config_group.add_argument('--timeout', type=int, help='测试超时时间(秒)')
    config_group.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    config_group.add_argument('--report', help='生成报告文件路径')
    
    args = parser.parse_args()
    
    runner = TestsV2Runner()
    
    # 如果没有任何参数，启动交互模式
    if len(sys.argv) == 1:
        runner.interactive_mode()
    else:
        runner.command_line_mode(args)


if __name__ == "__main__":
    main()