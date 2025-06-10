#!/usr/bin/env python3
"""新测试框架v2.0 - 集成测试运行器

使用新测试框架运行集成测试，需要实际的HTTP服务器
"""

import sys
import os
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.framework import SmartTestRunner
from tests.framework.utils import TestEnvironment


def check_server_status():
    """检查服务器状态"""
    env = TestEnvironment()
    print("🔍 检查服务器状态...")
    
    if env.check_server_running():
        print("✅ 服务器运行正常，可以开始集成测试")
        return True
    else:
        print("❌ 服务器未运行或无法访问")
        print("\n🚀 启动服务器指南:")
        print("1. 打开新的终端窗口")
        print("2. 进入后端目录: cd backend")
        print("3. 启动开发服务器: python start.py dev")
        print("4. 等待服务器启动完成")
        print("5. 重新运行此集成测试")
        
        # 询问是否等待服务器启动
        try:
            choice = input("\n是否等待服务器启动? (y/n): ").lower().strip()
            if choice == 'y':
                print("⏳ 等待服务器启动...")
                if env.wait_for_server(max_attempts=30, interval=2):
                    print("✅ 服务器已启动，开始测试")
                    return True
                else:
                    print("❌ 等待超时，服务器仍未启动")
                    return False
        except KeyboardInterrupt:
            print("\n❌ 用户取消等待")
        
        return False


def run_integration_tests():
    """运行集成测试"""
    print("🧪 信用卡管理系统 - 新框架v2.0集成测试")
    print("=" * 60)
    
    # 检查服务器状态
    if not check_server_status():
        print("❌ 无法连接到服务器，集成测试停止")
        return False
    
    # 打印环境信息
    env = TestEnvironment()
    env.print_env_info()
    
    # 创建测试运行器
    runner = SmartTestRunner()
    
    # 设置集成测试配置
    runner.config.update({
        "test_type": "integration",
        "use_real_server": True,
        "cleanup_data": True,
        "parallel_tests": False,  # 集成测试通常不并行运行
        "timeout": 30
    })
    
    print("\n🔍 发现集成测试...")
    
    # 发现集成测试套件
    test_suites = [
        "tests/suites/api/user_management_v2.py",
        "tests/suites/api/card_management_v2.py"
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    # 运行每个测试套件
    for suite_path in test_suites:
        if not Path(suite_path).exists():
            print(f"⚠️  测试套件不存在: {suite_path}")
            continue
        
        print(f"\n🧪 运行测试套件: {suite_path}")
        print("-" * 50)
        
        try:
            # 发现并运行测试
            runner.discover_tests(suite_path)
            results = runner.run_all()
            
            # 统计结果
            suite_passed = len([r for r in results if r.status == "PASSED"])
            suite_failed = len([r for r in results if r.status == "FAILED"])
            
            total_tests += len(results)
            passed_tests += suite_passed
            failed_tests += suite_failed
            
            print(f"✅ 套件完成: {suite_passed} 通过, {suite_failed} 失败")
            
        except Exception as e:
            print(f"❌ 套件运行失败: {e}")
            failed_tests += 1
    
    # 打印总结
    print("\n" + "=" * 60)
    print("📊 集成测试总结")
    print("=" * 60)
    print(f"总测试数: {total_tests}")
    print(f"通过: {passed_tests}")
    print(f"失败: {failed_tests}")
    
    if failed_tests == 0:
        print("🎉 所有集成测试通过!")
        return True
    else:
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"⚠️  成功率: {success_rate:.1f}%")
        return False


def main():
    """主函数"""
    start_time = time.time()
    
    try:
        success = run_integration_tests()
        
        elapsed_time = time.time() - start_time
        print(f"\n⏱️  总耗时: {elapsed_time:.2f} 秒")
        
        if success:
            print("✅ 集成测试完成")
            sys.exit(0)
        else:
            print("❌ 集成测试失败")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n❌ 用户中断测试")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 集成测试运行错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 