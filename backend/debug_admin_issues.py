#!/usr/bin/env python3
"""
调试管理员API问题
"""
import requests
import json

def test_admin_issues():
    # 登录管理员
    login_resp = requests.post('http://localhost:8000/api/v1/public/auth/login/username', json={
        'username': 'admin',
        'password': 'Admin123456'
    })
    
    if login_resp.status_code != 200:
        print(f"登录失败: {login_resp.text}")
        return
    
    token = login_resp.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # 获取用户列表
    users_resp = requests.get('http://localhost:8000/api/v1/admin/users/list', headers=headers)
    if users_resp.status_code != 200:
        print(f"获取用户列表失败: {users_resp.text}")
        return
    
    users = users_resp.json()['data']
    if not users:
        print("没有找到用户")
        return
    
    user_id = users[0]['id']
    print(f"测试用户ID: {user_id}")
    
    # 测试1: 权限更新
    print("\\n=== 测试权限更新 ===")
    perm_resp = requests.put(
        f'http://localhost:8000/api/v1/admin/users/{user_id}/permissions',
        json={'is_verified': True},
        headers=headers
    )
    print(f"权限更新响应: {perm_resp.status_code}")
    print(f"权限更新内容: {perm_resp.text}")
    
    # 测试2: 登录日志
    print("\\n=== 测试登录日志 ===")
    logs_resp = requests.get(
        f'http://localhost:8000/api/v1/admin/users/{user_id}/login-logs',
        headers=headers
    )
    print(f"登录日志响应: {logs_resp.status_code}")
    print(f"登录日志内容: {logs_resp.text[:300]}")
    
    # 测试3: 删除用户
    print("\\n=== 测试删除用户 ===")
    delete_resp = requests.delete(
        f'http://localhost:8000/api/v1/admin/users/{user_id}/delete',
        json={'confirm_deletion': True},
        headers=headers
    )
    print(f"删除用户响应: {delete_resp.status_code}")
    print(f"删除用户内容: {delete_resp.text}")

if __name__ == "__main__":
    test_admin_issues() 