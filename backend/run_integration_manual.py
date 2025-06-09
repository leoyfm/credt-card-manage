#!/usr/bin/env python3
"""
手动集成测试运行器

使用方式:
1. 在一个终端中手动启动服务器: python start.py dev
2. 在另一个终端中运行此脚本: python run_integration_manual.py
"""

import subprocess
import requests
import time
import sys
from pathlib import Path

def check_server_running():
    """检查服务器是否运行"""
    urls_to_check = [
        "http://127.0.0.1:8000/",
        "http://127.0.0.1:8000/api/health", 
        "http://127.0.0.1:8000/docs",
        "http://127.0.0.1:8000/api/"
    ]
    
    for url in urls_to_check:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code in [200, 404]:
                print(f"✅ 服务器在运行: {url} -> {response.status_code}")
                return True
        except:
            continue
    
    return False

def run_integration_tests(verbose=True):
    """运行集成测试"""
    print("🌐 运行集成测试...")
    
    command = [
        "python", "-m", "pytest",
        "tests/integration/",
        "-m", "integration",
        "-x"  # 遇到失败就停止
    ]
    
    if verbose:
        command.append("-v")
    
    print(f"📝 执行命令: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行集成测试时出错: {e}")
        return False

def main():
    """主函数"""
    print("🔧 手动集成测试运行器")
    print("=" * 50)
    
    print("📋 使用步骤:")
    print("1. 在一个终端中启动服务器: python start.py dev")
    print("2. 等待服务器完全启动")
    print("3. 在当前终端运行集成测试")
    print()
    
    # 检查服务器是否运行
    print("🔍 检查服务器状态...")
    if not check_server_running():
        print("❌ 服务器未运行或无法访问")
        print()
        print("💡 请先在另一个终端中启动服务器:")
        print("   python start.py dev")
        print()
        print("然后等待服务器完全启动后，再运行此脚本")
        return
    
    print("✅ 服务器正在运行")
    print()
    
    # 询问是否继续
    try:
        response = input("🚀 是否现在运行集成测试? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("👋 已取消")
            return
    except KeyboardInterrupt:
        print("\n👋 已取消")
        return
    
    # 运行集成测试
    success = run_integration_tests()
    
    if success:
        print("\n🎉 集成测试完成!")
    else:
        print("\n❌ 集成测试失败")
        print("💡 请检查服务器日志和测试输出信息")

if __name__ == "__main__":
    main() 