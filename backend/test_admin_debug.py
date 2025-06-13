#!/usr/bin/env python3
"""
调试管理员API
"""
import requests
import json
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_admin_api():
    # 登录管理员
    login_resp = requests.post('http://localhost:8000/api/v1/public/auth/login/username', json={
        'username': 'admin',
        'password': 'Admin123456'
    })
    
    print(f"登录状态: {login_resp.status_code}")
    if login_resp.status_code != 200:
        print(f"登录失败: {login_resp.text}")
        return
    
    token = login_resp.json()['data']['access_token']
    print(f"Token获取成功: {token[:50]}...")
    
    # 测试用户列表API
    headers = {'Authorization': f'Bearer {token}'}
    list_resp = requests.get('http://localhost:8000/api/v1/admin/users/list', headers=headers)
    
    print(f"用户列表状态: {list_resp.status_code}")
    print(f"用户列表响应: {list_resp.text}")

def test_service_directly():
    """直接测试服务层"""
    print("\n=== 测试服务层 ===")
    try:
        print("开始测试服务层...")
        from app.db.database import SessionLocal
        from app.services.admin_service import AdminUserService
        from app.utils.response import ResponseUtil
        
        db = SessionLocal()
        admin_service = AdminUserService(db)
        
        users, pagination_info = admin_service.get_users_list(
            page=1,
            page_size=20,
            search=None,
            is_active=None,
            is_admin=None,
            is_verified=None
        )
        
        print(f"服务层测试成功: 找到 {len(users)} 个用户")
        print(f"分页信息: {pagination_info}")
        
        # 测试ResponseUtil.paginated
        response = ResponseUtil.paginated(
            items=users,
            total=pagination_info['total'],
            page=pagination_info['page'],
            page_size=pagination_info['page_size'],
            message="测试成功"
        )
        print("服务层测试成功: ResponseUtil.paginated 调用正常")
        print(f"响应状态: {response.status_code}")
        
        db.close()
        
    except Exception as e:
        print(f"服务层测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_route_directly():
    """直接测试路由层"""
    print("\n=== 测试路由层 ===")
    try:
        from app.db.database import SessionLocal
        from app.models.database.user import User
        from app.services.admin_service import AdminUserService
        from app.utils.response import ResponseUtil
        
        db = SessionLocal()
        
        # 查找管理员用户
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            print("未找到管理员用户")
            return
        
        print(f"找到管理员用户: {admin_user.username}")
        
        # 测试服务层
        admin_service = AdminUserService(db)
        users, pagination_info = admin_service.get_users_list(
            page=1,
            page_size=20,
            search=None,
            is_active=None,
            is_admin=None,
            is_verified=None
        )
        
        # 测试ResponseUtil.paginated
        response = ResponseUtil.paginated(
            items=users,
            total=pagination_info['total'],
            page=pagination_info['page'],
            page_size=pagination_info['page_size'],
            message="测试成功"
        )
        
        print(f"路由层测试成功: {type(response)}")
        print(f"响应数据: {response}")
        
        db.close()
        
    except Exception as e:
        print(f"路由层测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== 测试API ===")
    test_admin_api()
    
    print("\n=== 测试服务层 ===")
    test_service_directly()
    
    print("\n=== 测试路由层 ===")
    test_route_directly() 