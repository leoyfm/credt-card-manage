#!/usr/bin/env python3
"""
TestClient 测试运行器

使用测试数据库运行用户认证功能的完整测试
"""
import subprocess
import sys
import os

def main():
    """运行testclient测试"""
    print("🚀 开始运行 TestClient 认证测试...")
    print("=" * 50)
    
    # 确保在正确的目录
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(backend_dir)
    
    # 运行测试
    cmd = ["pytest", "tests/testclient/", "-v", "--tb=short"]
    
    try:
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print("\n✅ 所有测试通过！")
            print("📊 测试覆盖：")
            print("  🔐 认证功能：")
            print("    - 用户注册成功")
            print("    - 重复用户名注册失败")
            print("    - 用户名登录成功")
            print("    - 获取用户资料成功")
            print("    - 完整认证流程")
            print("  ⏰ 提醒功能：")
            print("    - 提醒设置CRUD操作")
            print("    - 提醒记录管理")
            print("    - 提醒统计查询")
            print("    - 权限验证")
            print("    - 完整工作流程")
        else:
            print(f"\n❌ 测试失败，退出码: {result.returncode}")
            
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n💥 运行测试时出错: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 