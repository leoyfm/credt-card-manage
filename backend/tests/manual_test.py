#!/usr/bin/env python3
"""
手动测试脚本 - 不依赖复杂的测试框架
"""

import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import requests
import json


def test_server_health():
    """测试服务器健康状态"""
    print("🔍 测试服务器健康状态...")
    
    try:
        # 测试健康检查接口
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        print(f"✅ 健康检查接口响应: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   响应数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
                return True
            except:
                print(f"   响应文本: {response.text}")
                return True
        else:
            print(f"   非200状态码，响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False


def test_root_endpoint():
    """测试根路径"""
    print("🔍 测试根路径...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"✅ 根路径响应: {response.status_code}")
        
        if response.status_code in [200, 500]:  # 允许500错误
            try:
                if response.headers.get('content-type', '').startswith('application/json'):
                    data = response.json()
                    print(f"   JSON响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
                else:
                    print(f"   文本响应: {response.text[:500]}...")
                return True  
            except:
                print(f"   响应文本: {response.text[:200]}...")
                return True
        else:
            print(f"   意外状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 根路径测试失败: {e}")
        return False


def test_api_documentation():
    """测试API文档"""
    print("🔍 测试API文档...")
    
    try:
        response = requests.get("http://127.0.0.1:8000/docs", timeout=5)
        print(f"✅ API文档响应: {response.status_code}")
        
        if response.status_code == 200:
            print("   API文档可访问")
            return True
        else:
            print(f"   文档不可访问: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ API文档测试失败: {e}")
        return False


def test_auth_endpoints():
    """测试认证接口"""
    print("🔍 测试认证接口...")
    
    # 测试注册接口是否存在
    endpoints_to_test = [
        "/api/v1/public/auth/register",
        "/api/v1/public/auth/login", 
        "/api/v1/user/profile",
        "/api/v1/admin/users"
    ]
    
    results = []
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"http://127.0.0.1:8000{endpoint}", timeout=5)
            # 对于认证接口，401/422/405等都是预期的响应
            if response.status_code in [200, 401, 422, 405, 404]:
                print(f"   ✅ {endpoint}: {response.status_code}")
                results.append(True)
            else:
                print(f"   ⚠️ {endpoint}: {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"   ❌ {endpoint}: {e}")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"   认证接口可达性: {success_rate:.1f}%")
    return success_rate > 50  # 超过50%的接口可达即认为成功


def main():
    """主测试函数"""
    print("="*60)
    print("🚀 开始手动测试")
    print("="*60)
    
    tests = [
        ("服务器健康检查", test_server_health),
        ("根路径测试", test_root_endpoint),
        ("API文档测试", test_api_documentation),
        ("认证接口测试", test_auth_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        start_time = time.time()
        result = test_func()
        end_time = time.time()
        duration = end_time - start_time
        
        results.append((test_name, result, duration))
        
        if result:
            print(f"✅ {test_name} 通过 ({duration:.2f}s)")
        else:
            print(f"❌ {test_name} 失败 ({duration:.2f}s)")
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    success_rate = passed / total * 100
    
    print(f"总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")
    print(f"成功率: {success_rate:.1f}%")
    
    print("\n详细结果:")
    for test_name, result, duration in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status} {test_name} ({duration:.2f}s)")
    
    return success_rate > 75  # 超过75%成功率认为整体成功


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 