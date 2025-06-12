#!/usr/bin/env python3
"""
调试测试脚本 - 查看API响应详细信息
"""
import requests
import json

def test_api_response():
    """测试API响应并打印详细信息"""
    base_url = "http://127.0.0.1:8000"
    endpoint = "/api/v1/user/profile/info"
    
    print(f"测试未认证访问: {base_url}{endpoint}")
    
    try:
        response = requests.get(f"{base_url}{endpoint}")
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应体: {response.text}")
        
        try:
            json_data = response.json()
            print(f"JSON数据: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
        except Exception as e:
            print(f"JSON解析失败: {e}")
            
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_api_response() 