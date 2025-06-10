"""
流畅的API客户端

提供链式调用和优雅的断言接口，让测试代码更加清晰易读。

Usage:
    api = FluentAPIClient()
    api.get("/api/v1/user/profile").should.succeed().with_data(
        username="testuser",
        email__contains="@example.com"
    )
"""

import time
import json
import logging
from typing import Dict, Any, Optional, Union, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib.parse import urljoin
import uuid
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """请求指标"""
    start_time: float
    end_time: float
    duration: float
    status_code: int
    response_size: int


class FluentAPIClient:
    """流畅的API客户端"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.auth_token: Optional[str] = None
        self.default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "CreditCard-TestFramework/2.0"
        }
        self.session.headers.update(self.default_headers)
        
        # 请求历史和指标
        self.request_history: list = []
        self.last_response: Optional[requests.Response] = None
        self.last_metrics: Optional[RequestMetrics] = None
    
    def set_auth(self, token: str) -> 'FluentAPIClient':
        """设置认证令牌"""
        self.auth_token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        return self
    
    def clear_auth(self) -> 'FluentAPIClient':
        """清除认证"""
        self.auth_token = None
        self.session.headers.pop("Authorization", None)
        return self
    
    def set_header(self, key: str, value: str) -> 'FluentAPIClient':
        """设置请求头"""
        self.session.headers[key] = value
        return self
    
    def set_headers(self, headers: Dict[str, str]) -> 'FluentAPIClient':
        """设置多个请求头"""
        self.session.headers.update(headers)
        return self
    
    def get(self, path: str, params: Dict[str, Any] = None, **kwargs) -> ResponseAssertion:
        """GET请求"""
        return self._request("GET", path, params=params, **kwargs)
    
    def post(self, path: str, data: Any = None, **kwargs) -> ResponseAssertion:
        """POST请求"""
        return self._request("POST", path, json=data, **kwargs)
    
    def put(self, path: str, data: Any = None, **kwargs) -> ResponseAssertion:
        """PUT请求"""
        return self._request("PUT", path, json=data, **kwargs)
    
    def patch(self, path: str, data: Any = None, **kwargs) -> ResponseAssertion:
        """PATCH请求"""
        return self._request("PATCH", path, json=data, **kwargs)
    
    def delete(self, path: str, **kwargs) -> ResponseAssertion:
        """DELETE请求"""
        return self._request("DELETE", path, **kwargs)
    
    def _request(self, method: str, path: str, **kwargs) -> ResponseAssertion:
        """执行HTTP请求"""
        url = urljoin(self.base_url + "/", path.lstrip('/'))
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 生成请求ID用于追踪
        request_id = str(uuid.uuid4())[:8]
        
        try:
            # 执行请求
            response = self.session.request(method, url, **kwargs)
            
            # 记录请求结束时间
            end_time = time.time()
            duration = end_time - start_time
            
            # 创建请求指标
            self.last_metrics = RequestMetrics(
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                status_code=response.status_code,
                response_size=len(response.content) if response.content else 0
            )
            
            # 记录请求历史
            self.request_history.append({
                "id": request_id,
                "method": method,
                "url": url,
                "status_code": response.status_code,
                "duration": duration,
                "timestamp": start_time
            })
            
            # 保存最后的响应
            self.last_response = response
            
            # 如果响应很慢，打印警告
            if duration > 1.0:
                print(f"⚠️ 慢响应: {method} {path} ({duration:.3f}s)")
            
            # 返回流畅断言对象
            return ResponseAssertion(response, f"{method} {path}")
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 请求失败: {method} {path} - {e}")
            raise
    
    def login_user(self, username: str, password: str) -> ResponseAssertion:
        """用户登录便捷方法"""
        response = self.post("/api/v1/public/auth/login/username", {
            "username": username,
            "password": password
        })
        
        # 如果登录成功，自动设置认证令牌
        if response.response.status_code == 200:
            try:
                data = response.response.json()
                if data.get("success") and "data" in data:
                    access_token = data["data"].get("access_token")
                    if access_token:
                        self.set_auth(access_token)
                        print(f"✅ 用户 {username} 登录成功，已设置认证令牌")
            except:
                pass
        
        return response
    
    def register_user(self, user_data: Dict[str, Any]) -> ResponseAssertion:
        """用户注册便捷方法"""
        return self.post("/api/v1/public/auth/register", user_data)
    
    def logout(self) -> ResponseAssertion:
        """退出登录便捷方法"""
        response = self.post("/api/v1/user/profile/logout")
        
        # 清除本地认证信息
        self.clear_auth()
        print("✅ 已退出登录，清除认证令牌")
        
        return response
    
    def health_check(self) -> ResponseAssertion:
        """健康检查便捷方法"""
        return self.get("/api/v1/public/system/health")
    
    def get_user_profile(self) -> ResponseAssertion:
        """获取用户资料便捷方法"""
        return self.get("/api/v1/user/profile/info")
    
    def create_card(self, card_data: Dict[str, Any]) -> ResponseAssertion:
        """创建信用卡便捷方法"""
        return self.post("/api/v1/user/cards/create", card_data)
    
    def get_cards_list(self, page: int = 1, page_size: int = 20) -> ResponseAssertion:
        """获取信用卡列表便捷方法"""
        return self.get("/api/v1/user/cards/list", {
            "page": page,
            "page_size": page_size
        })
    
    def create_transaction(self, transaction_data: Dict[str, Any]) -> ResponseAssertion:
        """创建交易记录便捷方法"""
        return self.post("/api/v1/user/transactions/create", transaction_data)
    
    def get_transactions_list(self, page: int = 1, page_size: int = 20) -> ResponseAssertion:
        """获取交易列表便捷方法"""
        return self.get("/api/v1/user/transactions/list", {
            "page": page,
            "page_size": page_size
        })
    
    def get_statistics_overview(self) -> ResponseAssertion:
        """获取统计总览便捷方法"""
        return self.get("/api/v1/user/statistics/overview")
    
    def is_server_available(self) -> bool:
        """检查服务器是否可用"""
        try:
            response = self.health_check()
            return response.response.status_code == 200
        except:
            return False
    
    def wait_for_server(self, timeout: int = 30, interval: float = 1.0) -> bool:
        """等待服务器可用"""
        print(f"⏳ 等待服务器启动 (超时: {timeout}s)...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_server_available():
                print("✅ 服务器已准备就绪")
                return True
            
            time.sleep(interval)
            print(".", end="", flush=True)
        
        print(f"\n❌ 服务器在 {timeout}s 内未响应")
        return False
    
    def print_request_history(self, limit: int = 10):
        """打印请求历史"""
        print(f"\n📊 最近 {min(limit, len(self.request_history))} 个请求:")
        print("-" * 80)
        print(f"{'方法':<8} {'状态码':<8} {'耗时(s)':<10} {'URL':<50}")
        print("-" * 80)
        
        for request in self.request_history[-limit:]:
            print(f"{request['method']:<8} {request['status_code']:<8} {request['duration']:<10.3f} {request['url']:<50}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.request_history:
            return {}
        
        durations = [req["duration"] for req in self.request_history]
        status_codes = [req["status_code"] for req in self.request_history]
        
        return {
            "total_requests": len(self.request_history),
            "avg_duration": sum(durations) / len(durations),
            "min_duration": min(durations),
            "max_duration": max(durations),
            "success_rate": sum(1 for code in status_codes if 200 <= code < 300) / len(status_codes) * 100,
            "status_code_distribution": {
                str(code): status_codes.count(code) for code in set(status_codes)
            }
        }


class APIClientBuilder:
    """API客户端构建器"""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.headers = {}
        self.auth_token = None
    
    def with_base_url(self, url: str) -> 'APIClientBuilder':
        """设置基础URL"""
        self.base_url = url
        return self
    
    def with_auth(self, token: str) -> 'APIClientBuilder':
        """设置认证令牌"""
        self.auth_token = token
        return self
    
    def with_header(self, key: str, value: str) -> 'APIClientBuilder':
        """设置请求头"""
        self.headers[key] = value
        return self
    
    def with_headers(self, headers: Dict[str, str]) -> 'APIClientBuilder':
        """设置多个请求头"""
        self.headers.update(headers)
        return self
    
    def build(self) -> FluentAPIClient:
        """构建API客户端"""
        client = FluentAPIClient(self.base_url)
        
        if self.headers:
            client.set_headers(self.headers)
        
        if self.auth_token:
            client.set_auth(self.auth_token)
        
        return client


# 便捷函数
def create_api_client(base_url: str = "http://127.0.0.1:8000") -> FluentAPIClient:
    """创建API客户端"""
    return FluentAPIClient(base_url)


def api_client_builder() -> APIClientBuilder:
    """创建API客户端构建器"""
    return APIClientBuilder()


# 全局默认客户端
_default_client: Optional[FluentAPIClient] = None


def get_default_client() -> FluentAPIClient:
    """获取默认API客户端"""
    global _default_client
    if _default_client is None:
        _default_client = FluentAPIClient()
    return _default_client


def set_default_client(client: FluentAPIClient):
    """设置默认API客户端"""
    global _default_client
    _default_client = client


# 便捷API方法（使用默认客户端）
def get(path: str, **kwargs) -> ResponseAssertion:
    """GET请求便捷函数"""
    return get_default_client().get(path, **kwargs)


def post(path: str, data: Any = None, **kwargs) -> ResponseAssertion:
    """POST请求便捷函数"""
    return get_default_client().post(path, data, **kwargs)


def put(path: str, data: Any = None, **kwargs) -> ResponseAssertion:
    """PUT请求便捷函数"""
    return get_default_client().put(path, data, **kwargs)


def delete(path: str, **kwargs) -> ResponseAssertion:
    """DELETE请求便捷函数"""
    return get_default_client().delete(path, **kwargs)


def login(username: str, password: str) -> ResponseAssertion:
    """登录便捷函数"""
    return get_default_client().login_user(username, password)


def logout() -> ResponseAssertion:
    """退出登录便捷函数"""
    return get_default_client().logout()


def health_check() -> ResponseAssertion:
    """健康检查便捷函数"""
    return get_default_client().health_check()


class ResponseAssertion:
    """响应断言类"""
    
    def __init__(self, response: requests.Response, request_start_time: float = None):
        self.response = response
        self.request_start_time = request_start_time
        self.response_time = time.time() - request_start_time if request_start_time else None
        
        # 解析响应数据
        self.raw_data = None
        self.data = None
        
        if response.content:
            try:
                self.raw_data = response.json()
                # 处理统一响应格式
                if isinstance(self.raw_data, dict) and "data" in self.raw_data:
                    self.data = self.raw_data["data"]
                else:
                    self.data = self.raw_data
            except json.JSONDecodeError:
                self.raw_data = response.text
                self.data = response.text
    
    @property
    def should(self):
        """流畅断言接口入口"""
        return self
    
    def succeed(self, status_code: int = 200):
        """断言请求成功"""
        assert self.response.status_code == status_code, \
            f"期望状态码 {status_code}，实际 {self.response.status_code}\n" \
            f"响应内容: {self.response.text}"
        
        # 检查统一响应格式中的success字段
        if isinstance(self.raw_data, dict) and "success" in self.raw_data:
            assert self.raw_data.get("success", True), \
                f"响应失败: {self.raw_data.get('message', '未知错误')}"
        
        return self
    
    def fail(self, status_code: int = None, error_code: str = None):
        """断言请求失败"""
        if status_code:
            assert self.response.status_code == status_code, \
                f"期望失败状态码 {status_code}，实际 {self.response.status_code}"
        else:
            assert self.response.status_code >= 400, \
                f"期望失败状态码(>=400)，实际 {self.response.status_code}"
        
        if error_code and isinstance(self.raw_data, dict):
            actual_code = self.raw_data.get("code") or self.raw_data.get("error_code")
            assert actual_code == error_code, \
                f"期望错误代码 {error_code}，实际 {actual_code}"
        
        return self
    
    def with_data(self, **expected):
        """断言响应数据"""
        assert self.data is not None, "响应中没有数据"
        
        if not isinstance(self.data, dict):
            raise AssertionError(f"响应数据不是字典格式: {type(self.data)}")
        
        for key, expected_value in expected.items():
            if "__" in key:
                # 支持复杂断言
                field, operator = key.split("__", 1)
                actual_value = self._get_nested_value(self.data, field)
                self._assert_with_operator(actual_value, operator, expected_value, field)
            else:
                actual_value = self._get_nested_value(self.data, key)
                assert actual_value == expected_value, \
                    f"字段 {key} 期望值 {expected_value}，实际值 {actual_value}"
        
        return self
    
    def with_pagination(self, total_items: int = None, items_type: str = None, **kwargs):
        """断言分页响应"""
        # 检查是否有分页信息
        pagination = None
        if isinstance(self.raw_data, dict):
            pagination = self.raw_data.get("pagination")
        
        assert pagination is not None, "响应中缺少分页信息"
        
        # 验证总数
        if total_items is not None:
            actual_total = pagination.get("total", 0)
            assert actual_total == total_items, \
                f"期望总数 {total_items}，实际 {actual_total}"
        
        # 验证数据类型
        if items_type:
            items = self.data if isinstance(self.data, list) else []
            assert len(items) > 0, f"没有找到 {items_type} 数据"
        
        # 验证其他分页参数
        for key, value in kwargs.items():
            assert key in pagination, f"分页信息中缺少字段 {key}"
            assert pagination[key] == value, \
                f"分页字段 {key} 期望值 {value}，实际值 {pagination[key]}"
        
        return self
    
    def with_error(self, error_code: str = None, message_contains: str = None):
        """断言错误响应"""
        if isinstance(self.raw_data, dict):
            if error_code:
                actual_code = self.raw_data.get("code") or self.raw_data.get("error_code")
                assert actual_code == error_code, \
                    f"期望错误代码 {error_code}，实际 {actual_code}"
            
            if message_contains:
                message = self.raw_data.get("message", "")
                assert message_contains in message, \
                    f"错误消息中不包含 '{message_contains}': {message}"
        
        return self
    
    def complete_within(self, seconds: float):
        """断言响应时间"""
        if self.response_time is None:
            logger.warning("无法检查响应时间，请求时间未记录")
            return self
        
        assert self.response_time <= seconds, \
            f"响应时间超出预期: {self.response_time:.3f}s > {seconds}s"
        
        return self
    
    def have_header(self, header_name: str, expected_value: str = None):
        """断言响应头"""
        assert header_name in self.response.headers, \
            f"响应头中缺少 {header_name}"
        
        if expected_value:
            actual_value = self.response.headers[header_name]
            assert actual_value == expected_value, \
                f"响应头 {header_name} 期望值 {expected_value}，实际值 {actual_value}"
        
        return self
    
    def _get_nested_value(self, data: dict, key: str):
        """获取嵌套字段值"""
        if "." in key:
            # 支持嵌套字段如 user.profile.name
            keys = key.split(".")
            current = data
            for k in keys:
                if isinstance(current, dict) and k in current:
                    current = current[k]
                else:
                    return None
            return current
        else:
            return data.get(key)
    
    def _assert_with_operator(self, actual, operator: str, expected, field: str):
        """使用操作符进行断言"""
        if operator == "exists":
            assert actual is not None, f"字段 {field} 不存在"
        elif operator == "not_exists":
            assert actual is None, f"字段 {field} 不应该存在"
        elif operator == "contains":
            assert expected in str(actual), \
                f"字段 {field} 值 '{actual}' 不包含 '{expected}'"
        elif operator == "not_contains":
            assert expected not in str(actual), \
                f"字段 {field} 值 '{actual}' 包含了不期望的 '{expected}'"
        elif operator == "startswith":
            assert str(actual).startswith(str(expected)), \
                f"字段 {field} 值 '{actual}' 不以 '{expected}' 开头"
        elif operator == "endswith":
            assert str(actual).endswith(str(expected)), \
                f"字段 {field} 值 '{actual}' 不以 '{expected}' 结尾"
        elif operator == "gt":
            assert actual > expected, \
                f"字段 {field} 值 {actual} 不大于 {expected}"
        elif operator == "gte":
            assert actual >= expected, \
                f"字段 {field} 值 {actual} 不大于等于 {expected}"
        elif operator == "lt":
            assert actual < expected, \
                f"字段 {field} 值 {actual} 不小于 {expected}"
        elif operator == "lte":
            assert actual <= expected, \
                f"字段 {field} 值 {actual} 不小于等于 {expected}"
        elif operator == "in":
            assert actual in expected, \
                f"字段 {field} 值 {actual} 不在 {expected} 中"
        elif operator == "not_in":
            assert actual not in expected, \
                f"字段 {field} 值 {actual} 在不期望的列表 {expected} 中"
        elif operator == "length":
            actual_length = len(actual) if actual else 0
            assert actual_length == expected, \
                f"字段 {field} 长度 {actual_length} 不等于 {expected}"
        else:
            raise ValueError(f"不支持的操作符: {operator}")
    
    def debug(self):
        """调试输出响应信息"""
        print(f"\n=== 响应调试信息 ===")
        print(f"状态码: {self.response.status_code}")
        print(f"响应时间: {self.response_time:.3f}s" if self.response_time else "响应时间: 未知")
        print(f"响应头: {dict(self.response.headers)}")
        print(f"原始数据: {json.dumps(self.raw_data, indent=2, ensure_ascii=False)}")
        print(f"解析数据: {json.dumps(self.data, indent=2, ensure_ascii=False)}")
        print(f"==================\n")
        return self 