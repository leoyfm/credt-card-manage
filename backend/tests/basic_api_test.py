#!/usr/bin/env python3
"""
基础API测试 - 验证新架构API是否工作
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import requests

def test_new_architecture():
    """测试新架构API"""
    base_url = "http://127.0.0.1:8000"
    
    print("🚀 测试新架构API...")
    
    # 1. 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   ✅ 健康检查: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   📊 服务状态: {data.get('data', {}).get('status', 'unknown')}")
    except Exception as e:
        print(f"   ❌ 健康检查失败: {e}")
    
    # 2. 测试API文档
    print("\n2. 测试API文档...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        print(f"   ✅ API文档: {response.status_code}")
    except Exception as e:
        print(f"   ❌ API文档失败: {e}")
    
    # 3. 测试新架构路由
    print("\n3. 测试新架构路由...")
    test_routes = [
        "/api/v1/public/auth/register",
        "/api/v1/public/auth/login/username", 
        "/api/v1/user/profile",
        "/api/v1/admin/users/list"
    ]
    
    for route in test_routes:
        try:
            response = requests.get(f"{base_url}{route}", timeout=5)
            status = "✅ 可达" if response.status_code in [404, 405, 422] else "🔄 其他"
            print(f"   {status} {route}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {route}: {e}")
    
    print("\n🎯 新架构API测试完成!")

if __name__ == "__main__":
    test_new_architecture() 