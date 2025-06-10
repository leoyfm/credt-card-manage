#!/usr/bin/env python3
"""
简单测试运行脚本 - 直接运行测试套件而不依赖自动发现
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tests.framework.clients.api import FluentAPIClient


def check_server():
    """检查服务器是否运行"""
    print("🔧 检查服务器状态...")
    client = FluentAPIClient()
    
    # 尝试多个健康检查路径
    health_paths = [
        "/health",  # 主应用健康检查
        "/api/v1/public/system/health",  # 新架构路径
        "/",  # 根路径
    ]
    
    for path in health_paths:
        try:
            response = client.get(path)
            if response.response.status_code == 200:
                print(f"✅ 服务器运行正常 - 路径: {path}")
                if response.data:
                    message = response.data.get("message", "")
                    if message:
                        print(f"📋 服务信息: {message}")
                return True
            else:
                print(f"⚠️ 路径 {path} 响应异常: {response.response.status_code}")
        except Exception as e:
            print(f"❌ 路径 {path} 连接失败: {e}")
    
    print("❌ 服务器连接失败")
    print("💡 请先启动服务器: python start.py dev")
    return False


def run_basic_tests():
    """运行基础测试"""
    print("\n🧪 运行基础API测试...")
    client = FluentAPIClient()
    
    test_results = []
    
    # 测试1: 根路径
    try:
        print("测试1: 根路径访问")
        response = client.get("/")
        if response.response.status_code == 200:
            print("  ✅ 根路径测试通过")
            test_results.append(("根路径", True, "200 OK"))
        else:
            print(f"  ❌ 根路径测试失败: {response.response.status_code}")
            test_results.append(("根路径", False, f"{response.response.status_code}"))
    except Exception as e:
        print(f"  ❌ 根路径测试异常: {e}")
        test_results.append(("根路径", False, str(e)))
    
    # 测试2: 健康检查
    try:
        print("测试2: 健康检查接口")
        response = client.get("/health")
        if response.response.status_code == 200:
            print("  ✅ 健康检查测试通过")
            test_results.append(("健康检查", True, "200 OK"))
        else:
            print(f"  ❌ 健康检查测试失败: {response.response.status_code}")
            test_results.append(("健康检查", False, f"{response.response.status_code}"))
    except Exception as e:
        print(f"  ❌ 健康检查测试异常: {e}")
        test_results.append(("健康检查", False, str(e)))
    
    # 测试3: 新架构认证健康检查
    try:
        print("测试3: 新架构认证接口健康检查")
        response = client.get("/api/v1/public/auth/health")
        if response.response.status_code == 200:
            print("  ✅ 新架构认证接口测试通过")
            test_results.append(("新架构认证", True, "200 OK"))
        else:
            print(f"  ❌ 新架构认证接口测试失败: {response.response.status_code}")
            test_results.append(("新架构认证", False, f"{response.response.status_code}"))
    except Exception as e:
        print(f"  ❌ 新架构认证接口测试异常: {e}")
        test_results.append(("新架构认证", False, str(e)))
    
    return test_results


def print_test_summary(results):
    """打印测试结果摘要"""
    print("\n📊 测试结果摘要:")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for test_name, success, details in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status:10} {test_name:20} {details}")
        if success:
            passed += 1
        else:
            failed += 1
    
    print("=" * 50)
    print(f"总计: {len(results)} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {failed} 个")
    print(f"成功率: {(passed/len(results)*100):.1f}%" if results else "0%")


def main():
    """主函数"""
    print("🚀 信用卡管理系统简单测试")
    
    # 检查服务器
    if not check_server():
        return 1
    
    # 运行基础测试
    results = run_basic_tests()
    
    # 打印结果摘要
    print_test_summary(results)
    
    # 返回退出码
    failed_tests = sum(1 for _, success, _ in results if not success)
    return 0 if failed_tests == 0 else 1


if __name__ == "__main__":
    sys.exit(main()) 