#!/usr/bin/env python3
"""
快速测试脚本

只运行核心功能测试，跳过性能测试，适合开发时快速验证。
"""

import os
import subprocess
import sys

def main():
    """运行快速测试"""
    # 设置测试环境
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["DEBUG"] = "true"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"
    
    print("🚀 运行快速测试...")
    print("✅ 测试环境设置完成")
    
    # 只运行非性能测试
    cmd = [
        "python", "-m", "pytest", 
        "tests/test_transactions.py",
        "-v",
        "-m", "not slow",
        "--tb=short"
    ]
    
    print(f"🔍 运行命令: {' '.join(cmd)}")
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ 快速测试通过!")
        print("💡 运行完整测试: python run_tests.py")
        print("💡 运行性能测试: python run_tests.py -m slow")
    else:
        print(f"\n❌ 测试失败，退出码: {result.returncode}")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main()) 