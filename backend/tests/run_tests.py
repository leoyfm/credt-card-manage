#!/usr/bin/env python3
"""
新测试框架快速启动脚本

简单易用的测试执行入口。

Usage:
    # 运行所有测试
    python tests/run_tests.py
    
    # 运行指定套件
    python tests/run_tests.py --suite "用户管理API"
    
    # 按标签运行
    python tests/run_tests.py --tags smoke auth
    
    # 并行执行
    python tests/run_tests.py --parallel
    
    # 性能测试
    python tests/run_tests.py --tags performance
"""

from framework.core.runner import SmartTestRunner


def main():
    """主函数"""
    print("🚀 信用卡管理系统 - 新一代测试框架 v2.0")
    print("=" * 60)
    
    # 创建智能测试运行器
    runner = SmartTestRunner({
        "verbose": True,
        "parallel_execution": False,
        "fail_fast": False
    })
    
    # 自动发现测试
    runner.discover_tests("tests/suites/")
    
    # 检查是否有测试
    if not runner.discovered_suites:
        print("❌ 没有发现任何测试套件")
        print("请确保测试文件位于 tests/suites/ 目录下")
        return
    
    # 显示菜单
    show_menu(runner)


def show_menu(runner: SmartTestRunner):
    """显示交互菜单"""
    while True:
        print("\n📋 请选择要执行的操作:")
        print("1. 运行所有测试")
        print("2. 运行烟雾测试 (smoke)")
        print("3. 运行认证测试 (auth)")
        print("4. 运行性能测试 (performance)")
        print("5. 运行指定套件")
        print("6. 列出所有测试")
        print("7. 自定义过滤运行")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-7): ").strip()
        
        if choice == "0":
            print("👋 再见!")
            break
        elif choice == "1":
            run_all_tests(runner)
        elif choice == "2":
            run_smoke_tests(runner)
        elif choice == "3":
            run_auth_tests(runner)
        elif choice == "4":
            run_performance_tests(runner)
        elif choice == "5":
            run_specific_suite(runner)
        elif choice == "6":
            runner.list_discovered_tests()
        elif choice == "7":
            run_custom_filter(runner)
        else:
            print("❌ 无效选择，请重新输入")


def run_all_tests(runner: SmartTestRunner):
    """运行所有测试"""
    print("\n🚀 运行所有测试...")
    results = runner.run_all()
    print_summary(results)


def run_smoke_tests(runner: SmartTestRunner):
    """运行烟雾测试"""
    print("\n💨 运行烟雾测试...")
    results = runner.run_by_tags(["smoke"])
    print_summary(results)


def run_auth_tests(runner: SmartTestRunner):
    """运行认证测试"""
    print("\n🔐 运行认证测试...")
    results = runner.run_by_tags(["auth"])
    print_summary(results)


def run_performance_tests(runner: SmartTestRunner):
    """运行性能测试"""
    print("\n⚡ 运行性能测试...")
    results = runner.run_by_tags(["performance"])
    print_summary(results)


def run_specific_suite(runner: SmartTestRunner):
    """运行指定套件"""
    print("\n📦 可用的测试套件:")
    suite_names = list(runner.discovered_suites.keys())
    
    for i, name in enumerate(suite_names, 1):
        print(f"{i}. {name}")
    
    try:
        choice = int(input("\n请选择套件编号: "))
        if 1 <= choice <= len(suite_names):
            suite_name = suite_names[choice - 1]
            print(f"\n🎯 运行套件: {suite_name}")
            results = runner.run_suite(suite_name)
            print_summary(results)
        else:
            print("❌ 无效选择")
    except ValueError:
        print("❌ 请输入有效数字")


def run_custom_filter(runner: SmartTestRunner):
    """自定义过滤运行"""
    print("\n🎛️ 自定义过滤配置:")
    
    # 标签过滤
    available_tags = set()
    for suite_info in runner.discovered_suites.values():
        for test in suite_info['tests']:
            available_tags.update(test.get('tags', []))
    
    if available_tags:
        print(f"可用标签: {', '.join(sorted(available_tags))}")
        tags_input = input("请输入标签 (用空格分隔, 回车跳过): ").strip()
        tags = tags_input.split() if tags_input else []
    else:
        tags = []
    
    # 优先级过滤
    max_priority = input("最大优先级 (数字越小优先级越高, 回车跳过): ").strip()
    try:
        max_priority = int(max_priority) if max_priority else 999
    except ValueError:
        max_priority = 999
    
    # 构建过滤器
    filters = {}
    if tags:
        filters["tags"] = tags
    if max_priority < 999:
        filters["max_priority"] = max_priority
    
    if filters:
        print(f"\n🎯 使用过滤器运行: {filters}")
        results = runner.run_all(filters)
        print_summary(results)
    else:
        print("❌ 没有设置过滤器，运行所有测试")
        run_all_tests(runner)


def print_summary(results: dict):
    """打印简要总结"""
    summary = results["summary"]
    
    print("\n" + "=" * 40)
    print("📊 测试执行总结")
    print("=" * 40)
    
    # 状态图标
    if summary["failed_tests"] == 0:
        status_icon = "✅"
        status_text = "全部通过"
    else:
        status_icon = "❌"
        status_text = "有失败测试"
    
    print(f"{status_icon} 状态: {status_text}")
    print(f"🧪 总测试: {summary['total_tests']}")
    print(f"✅ 通过: {summary['passed_tests']}")
    print(f"❌ 失败: {summary['failed_tests']}")
    print(f"⏭️ 跳过: {summary['skipped_tests']}")
    print(f"📈 成功率: {summary['success_rate']:.1f}%")
    print(f"⏱️ 耗时: {summary['total_duration']:.2f}s")
    
    # 推荐操作
    if summary["failed_tests"] > 0:
        print("\n💡 建议:")
        print("  - 检查失败测试的详细日志")
        print("  - 确认API服务器是否正常运行")
        print("  - 验证测试数据和环境配置")
    
    print("=" * 40)


def quick_demo():
    """快速演示"""
    print("🎬 新测试框架快速演示")
    print("\n以下是使用新框架编写测试的示例:")
    
    demo_code = '''
from tests.framework import test_suite, api_test, with_user, with_cards

@test_suite("信用卡管理")
class CardTests:
    
    @api_test
    @with_user
    @with_cards(count=3, bank="招商银行")
    def test_get_user_cards(self, api, user, cards):
        """一行装饰器自动创建用户和3张招商银行信用卡"""
        api.get("/api/v1/user/cards/list").should.succeed().with_pagination(
            total_items=3
        )
        
        # 验证所有卡片都是招商银行
        for card in cards:
            assert card.bank_name == "招商银行"
'''
    
    print(demo_code)
    print("\n✨ 特点:")
    print("  ✅ 极简API - 装饰器自动处理数据准备")
    print("  ✅ 流畅断言 - .should.succeed().with_data() 链式调用")
    print("  ✅ 自动清理 - 测试完成后自动清理数据")
    print("  ✅ 智能运行 - 支持标签、优先级、并行执行")
    print("  ✅ 丰富报告 - 详细的测试报告和统计")


if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="新测试框架启动器")
    parser.add_argument("--demo", action="store_true", help="显示框架演示")
    parser.add_argument("--suite", help="运行指定套件")
    parser.add_argument("--tags", nargs="+", help="按标签运行")
    parser.add_argument("--parallel", action="store_true", help="并行执行")
    
    args = parser.parse_args()
    
    if args.demo:
        quick_demo()
        sys.exit(0)
    
    if args.suite or args.tags or args.parallel:
        # 命令行模式
        config = {"parallel_execution": args.parallel}
        runner = SmartTestRunner(config)
        runner.discover_tests("tests/suites/")
        
        filters = {}
        if args.suite:
            filters["suites"] = [args.suite]
        if args.tags:
            filters["tags"] = args.tags
        
        results = runner.run_all(filters)
        exit_code = 0 if results["summary"]["failed_tests"] == 0 else 1
        sys.exit(exit_code)
    else:
        # 交互模式
        main() 