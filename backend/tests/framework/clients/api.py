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

logger = logging.getLogger(__name__)


class FluentAPIClient:
    """流畅的API客户端"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or "http://127.0.0.1:8000"
        self.session = requests.Session()
        self.auth_token = None
        self.last_response = None
        self.request_start_time = None
        
        # 配置重试策略
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # 设置默认超时
        self.session.timeout = 30
        
        # 设置默认头部
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "TestFramework/2.0"
        })
    
    def get(self, path: str, params: Optional[Dict] = None, **kwargs):
        """GET请求"""
        return self._make_request("GET", path, params=params, **kwargs)
    
    def post(self, path: str, data: Optional[Dict] = None, **kwargs):
        """POST请求"""
        return self._make_request("POST", path, json=data, **kwargs)
    
    def put(self, path: str, data: Optional[Dict] = None, **kwargs):
        """PUT请求"""
        return self._make_request("PUT", path, json=data, **kwargs)
    
    def delete(self, path: str, **kwargs):
        """DELETE请求"""
        return self._make_request("DELETE", path, **kwargs)
    
    def patch(self, path: str, data: Optional[Dict] = None, **kwargs):
        """PATCH请求"""
        return self._make_request("PATCH", path, json=data, **kwargs)
    
    def _make_request(self, method: str, path: str, **kwargs):
        """执行HTTP请求"""
        url = f"{self.base_url}{path}"
        
        # 记录请求开始时间
        self.request_start_time = time.time()
        
        # 合并headers
        headers = kwargs.pop('headers', {})
        if self.auth_token:
            headers['Authorization'] = f"Bearer {self.auth_token}"
        kwargs['headers'] = headers
        
        try:
            logger.debug(f"{method} {url}")
            if 'json' in kwargs and kwargs['json']:
                logger.debug(f"Request data: {json.dumps(kwargs['json'], indent=2, ensure_ascii=False)}")
            
            self.last_response = self.session.request(method, url, **kwargs)
            
            # 记录响应时间
            response_time = time.time() - self.request_start_time
            logger.debug(f"Response time: {response_time:.3f}s")
            logger.debug(f"Response status: {self.last_response.status_code}")
            
            if self.last_response.content:
                try:
                    response_data = self.last_response.json()
                    logger.debug(f"Response data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                except:
                    logger.debug(f"Response text: {self.last_response.text}")
            
            return ResponseAssertion(self.last_response, self.request_start_time)
            
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def set_auth(self, token: str):
        """设置认证令牌"""
        self.auth_token = token
        logger.info(f"已设置认证令牌: {token[:20]}...")
        return self
    
    def clear_auth(self):
        """清除认证令牌"""
        self.auth_token = None
        logger.info("已清除认证令牌")
        return self
    
    def set_header(self, key: str, value: str):
        """设置请求头"""
        self.session.headers[key] = value
        return self
    
    def get_last_response(self):
        """获取最后一次响应"""
        return self.last_response


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