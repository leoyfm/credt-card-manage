#!/usr/bin/env python3
"""
测试运行脚本

提供便捷的测试运行命令。
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def setup_test_environment():
    """设置测试环境"""
    # 设置测试环境变量
    os.environ["TESTING"] = "true"
    os.environ["DATABASE_URL"] = "postgresql://credit_user:credit_password@localhost:5432/credit_card_db"
    os.environ["DEBUG"] = "true"
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"
    
    print("✅ 测试环境设置完成")

def run_pytest(args=None):
    """运行pytest"""
    cmd = ["python", "-m", "pytest"]
    
    if args:
        cmd.extend(args)
    
    print(f"🚀 运行命令: {' '.join(cmd)}")
    return subprocess.run(cmd)

def main():
    parser = argparse.ArgumentParser(description="运行测试")
    parser.add_argument(
        "test_path", 
        nargs="?", 
        default="tests/",
        help="测试文件或目录路径 (默认: tests/)"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="详细输出"
    )
    parser.add_argument(
        "-s", "--capture", 
        action="store_true",
        help="禁用输出捕获"
    )
    parser.add_argument(
        "-k", "--keyword",
        help="按关键词筛选测试"
    )
    parser.add_argument(
        "-m", "--marker",
        help="按标记筛选测试"
    )
    parser.add_argument(
        "--cov", 
        action="store_true",
        help="生成覆盖率报告"
    )
    parser.add_argument(
        "--html",
        action="store_true", 
        help="生成HTML报告"
    )
    
    args = parser.parse_args()
    
    # 设置测试环境
    setup_test_environment()
    
    # 构建pytest参数
    pytest_args = [args.test_path]
    
    if args.verbose:
        pytest_args.append("-v")
    
    if args.capture:
        pytest_args.append("-s")
        
    if args.keyword:
        pytest_args.extend(["-k", args.keyword])
        
    if args.marker:
        pytest_args.extend(["-m", args.marker])
        
    if args.cov:
        pytest_args.extend([
            "--cov=.",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
        
    if args.html:
        pytest_args.extend([
            "--html=reports/report.html",
            "--self-contained-html"
        ])
    
    # 运行测试
    result = run_pytest(pytest_args)
    
    # 输出结果
    if result.returncode == 0:
        print("\n✅ 所有测试通过!")
    else:
        print(f"\n❌ 测试失败，退出码: {result.returncode}")
        
    return result.returncode

if __name__ == "__main__":
    sys.exit(main()) 