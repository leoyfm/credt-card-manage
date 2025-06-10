"""
流畅断言系统

提供链式调用的断言接口，让测试代码更加清晰和可读。
"""

import re
import time
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass
import json
import requests


class AssertionError(Exception):
    """断言失败异常"""
    pass


@dataclass
class AssertionResult:
    """断言结果"""
    passed: bool
    message: str
    expected: Any = None
    actual: Any = None
    operator: str = ""


class BaseAssertion:
    """基础断言类"""
    
    def __init__(self, value: Any, description: str = ""):
        self.value = value
        self.description = description
        self.negated = False
    
    @property
    def should(self):
        """流畅断言接口"""
        return self
    
    @property
    def should_not(self):
        """否定断言接口"""
        self.negated = True
        return self
    
    def _assert(self, condition: bool, message: str, expected: Any = None, actual: Any = None):
        """执行断言"""
        if self.negated:
            condition = not condition
            message = f"NOT ({message})"
        
        if not condition:
            full_message = f"{self.description}: {message}" if self.description else message
            if expected is not None and actual is not None:
                full_message += f"\n  期望: {expected}\n  实际: {actual}"
            raise AssertionError(full_message)
    
    def equal(self, expected: Any):
        """相等断言"""
        self._assert(
            self.value == expected,
            f"期望值相等",
            expected=expected,
            actual=self.value
        )
        return self
    
    def not_equal(self, expected: Any):
        """不相等断言"""
        self._assert(
            self.value != expected,
            f"期望值不相等",
            expected=f"不等于 {expected}",
            actual=self.value
        )
        return self
    
    def be_true(self):
        """真值断言"""
        self._assert(bool(self.value), "期望为True", expected=True, actual=self.value)
        return self
    
    def be_false(self):
        """假值断言"""
        self._assert(not bool(self.value), "期望为False", expected=False, actual=self.value)
        return self
    
    def be_none(self):
        """空值断言"""
        self._assert(self.value is None, "期望为None", expected=None, actual=self.value)
        return self
    
    def not_be_none(self):
        """非空值断言"""
        self._assert(self.value is not None, "期望非None", expected="非None", actual=self.value)
        return self
    
    def exist(self):
        """存在断言（非None且非空）"""
        self._assert(
            self.value is not None and self.value != "",
            "期望存在（非None且非空）",
            expected="存在",
            actual=self.value
        )
        return self


class StringAssertion(BaseAssertion):
    """字符串断言"""
    
    def contain(self, substring: str):
        """包含子字符串断言"""
        self._assert(
            substring in str(self.value),
            f"期望包含子字符串 '{substring}'",
            expected=f"包含 '{substring}'",
            actual=self.value
        )
        return self
    
    def start_with(self, prefix: str):
        """以指定字符串开头断言"""
        self._assert(
            str(self.value).startswith(prefix),
            f"期望以 '{prefix}' 开头",
            expected=f"以 '{prefix}' 开头",
            actual=self.value
        )
        return self
    
    def end_with(self, suffix: str):
        """以指定字符串结尾断言"""
        self._assert(
            str(self.value).endswith(suffix),
            f"期望以 '{suffix}' 结尾",
            expected=f"以 '{suffix}' 结尾",
            actual=self.value
        )
        return self
    
    def match_pattern(self, pattern: str):
        """正则匹配断言"""
        self._assert(
            re.search(pattern, str(self.value)) is not None,
            f"期望匹配正则 '{pattern}'",
            expected=f"匹配 '{pattern}'",
            actual=self.value
        )
        return self
    
    def be_empty(self):
        """空字符串断言"""
        self._assert(
            str(self.value) == "",
            "期望为空字符串",
            expected="",
            actual=self.value
        )
        return self
    
    def not_be_empty(self):
        """非空字符串断言"""
        self._assert(
            str(self.value) != "",
            "期望为非空字符串",
            expected="非空",
            actual=self.value
        )
        return self


class NumberAssertion(BaseAssertion):
    """数字断言"""
    
    def be_greater_than(self, value: Union[int, float]):
        """大于断言"""
        self._assert(
            float(self.value) > float(value),
            f"期望大于 {value}",
            expected=f"> {value}",
            actual=self.value
        )
        return self
    
    def be_greater_equal(self, value: Union[int, float]):
        """大于等于断言"""
        self._assert(
            float(self.value) >= float(value),
            f"期望大于等于 {value}",
            expected=f">= {value}",
            actual=self.value
        )
        return self
    
    def be_less_than(self, value: Union[int, float]):
        """小于断言"""
        self._assert(
            float(self.value) < float(value),
            f"期望小于 {value}",
            expected=f"< {value}",
            actual=self.value
        )
        return self
    
    def be_less_equal(self, value: Union[int, float]):
        """小于等于断言"""
        self._assert(
            float(self.value) <= float(value),
            f"期望小于等于 {value}",
            expected=f"<= {value}",
            actual=self.value
        )
        return self
    
    def be_between(self, min_val: Union[int, float], max_val: Union[int, float]):
        """区间断言"""
        val = float(self.value)
        self._assert(
            min_val <= val <= max_val,
            f"期望在 [{min_val}, {max_val}] 区间内",
            expected=f"[{min_val}, {max_val}]",
            actual=self.value
        )
        return self
    
    def be_positive(self):
        """正数断言"""
        self._assert(
            float(self.value) > 0,
            "期望为正数",
            expected="> 0",
            actual=self.value
        )
        return self
    
    def be_negative(self):
        """负数断言"""
        self._assert(
            float(self.value) < 0,
            "期望为负数",
            expected="< 0",
            actual=self.value
        )
        return self
    
    def be_zero(self):
        """零值断言"""
        self._assert(
            float(self.value) == 0,
            "期望为0",
            expected=0,
            actual=self.value
        )
        return self


class CollectionAssertion(BaseAssertion):
    """集合断言"""
    
    def have_length(self, expected_length: int):
        """长度断言"""
        actual_length = len(self.value)
        self._assert(
            actual_length == expected_length,
            f"期望长度为 {expected_length}",
            expected=expected_length,
            actual=actual_length
        )
        return self
    
    def be_empty(self):
        """空集合断言"""
        self._assert(
            len(self.value) == 0,
            "期望为空集合",
            expected="空集合",
            actual=f"长度为 {len(self.value)}"
        )
        return self
    
    def not_be_empty(self):
        """非空集合断言"""
        self._assert(
            len(self.value) > 0,
            "期望为非空集合",
            expected="非空集合",
            actual=f"长度为 {len(self.value)}"
        )
        return self
    
    def contain_item(self, item: Any):
        """包含元素断言"""
        self._assert(
            item in self.value,
            f"期望包含元素 {item}",
            expected=f"包含 {item}",
            actual=list(self.value) if hasattr(self.value, '__iter__') else self.value
        )
        return self
    
    def contain_all(self, *items):
        """包含所有元素断言"""
        missing_items = [item for item in items if item not in self.value]
        self._assert(
            len(missing_items) == 0,
            f"期望包含所有元素",
            expected=list(items),
            actual=f"缺少: {missing_items}" if missing_items else "包含所有"
        )
        return self
    
    def contain_any(self, *items):
        """包含任一元素断言"""
        found_items = [item for item in items if item in self.value]
        self._assert(
            len(found_items) > 0,
            f"期望包含任一元素",
            expected=f"任一: {list(items)}",
            actual=f"找到: {found_items}"
        )
        return self


class DictionaryAssertion(BaseAssertion):
    """字典断言"""
    
    def have_key(self, key: str):
        """包含键断言"""
        self._assert(
            key in self.value,
            f"期望包含键 '{key}'",
            expected=f"键 '{key}'",
            actual=list(self.value.keys()) if isinstance(self.value, dict) else self.value
        )
        return self
    
    def have_keys(self, *keys):
        """包含多个键断言"""
        missing_keys = [key for key in keys if key not in self.value]
        self._assert(
            len(missing_keys) == 0,
            f"期望包含所有键",
            expected=list(keys),
            actual=f"缺少键: {missing_keys}" if missing_keys else "包含所有键"
        )
        return self
    
    def have_value(self, value: Any):
        """包含值断言"""
        self._assert(
            value in self.value.values(),
            f"期望包含值 {value}",
            expected=value,
            actual=list(self.value.values()) if isinstance(self.value, dict) else self.value
        )
        return self
    
    def have_key_value(self, key: str, value: Any):
        """键值对断言"""
        self._assert(
            key in self.value and self.value[key] == value,
            f"期望键 '{key}' 的值为 {value}",
            expected={key: value},
            actual={key: self.value.get(key)} if isinstance(self.value, dict) else self.value
        )
        return self


class ResponseAssertion(BaseAssertion):
    """HTTP响应断言"""
    
    def __init__(self, response: requests.Response, description: str = ""):
        super().__init__(response, description)
        self.response = response
        self._data = None
        
        # 尝试解析JSON
        try:
            if response.content:
                self._data = response.json()
        except:
            self._data = None
    
    @property
    def data(self):
        """响应数据"""
        return self._data
    
    def succeed(self, status_code: int = 200):
        """成功响应断言"""
        self._assert(
            self.response.status_code == status_code,
            f"期望状态码为 {status_code}",
            expected=status_code,
            actual=self.response.status_code
        )
        
        # 检查响应格式
        if self._data and isinstance(self._data, dict):
            success = self._data.get("success", True)
            self._assert(
                success,
                "期望响应成功",
                expected=True,
                actual=success
            )
        
        return self
    
    def fail(self, status_code: int = None):
        """失败响应断言"""
        if status_code:
            self._assert(
                self.response.status_code == status_code,
                f"期望状态码为 {status_code}",
                expected=status_code,
                actual=self.response.status_code
            )
        else:
            self._assert(
                self.response.status_code >= 400,
                "期望响应失败（状态码 >= 400）",
                expected=">= 400",
                actual=self.response.status_code
            )
        
        return self
    
    def with_data(self, **expected_fields):
        """响应数据断言"""
        if not self._data:
            self._assert(False, "响应不包含有效的JSON数据", expected="JSON数据", actual="无")
        
        response_data = self._data.get("data", {}) if isinstance(self._data, dict) else self._data
        
        for field_path, expected_value in expected_fields.items():
            actual_value = self._get_nested_value(response_data, field_path)
            
            if "__" in field_path:
                # 复杂断言，如 email__contains
                field, operator = field_path.split("__", 1)
                actual_value = self._get_nested_value(response_data, field)
                self._assert_with_operator(actual_value, operator, expected_value, field)
            else:
                self._assert(
                    actual_value == expected_value,
                    f"字段 '{field_path}' 值不匹配",
                    expected=expected_value,
                    actual=actual_value
                )
        
        return self
    
    def with_pagination(self, total_items: int = None, items_type: str = None, **pagination_fields):
        """分页响应断言"""
        if not self._data:
            self._assert(False, "响应不包含有效的JSON数据")
        
        pagination = self._data.get("pagination")
        self._assert(pagination is not None, "响应缺少分页信息", expected="分页信息", actual="无")
        
        if total_items is not None:
            actual_total = pagination.get("total")
            self._assert(
                actual_total == total_items,
                f"总条目数不匹配",
                expected=total_items,
                actual=actual_total
            )
        
        if items_type:
            items = self._data.get("data", [])
            self._assert(
                len(items) > 0,
                f"没有找到 {items_type} 数据",
                expected=f">0 个 {items_type}",
                actual=f"{len(items)} 个"
            )
        
        # 检查其他分页字段
        for field, expected_value in pagination_fields.items():
            actual_value = pagination.get(field)
            self._assert(
                actual_value == expected_value,
                f"分页字段 '{field}' 值不匹配",
                expected=expected_value,
                actual=actual_value
            )
        
        return self
    
    def with_error(self, error_code: str = None, error_message: str = None):
        """错误响应断言"""
        if not self._data:
            self._assert(False, "响应不包含有效的JSON数据")
        
        # 检查success字段
        success = self._data.get("success", True)
        self._assert(not success, "期望响应失败", expected=False, actual=success)
        
        if error_code:
            actual_error_code = self._data.get("error_code")
            self._assert(
                actual_error_code == error_code,
                f"错误码不匹配",
                expected=error_code,
                actual=actual_error_code
            )
        
        if error_message:
            actual_message = self._data.get("message", "")
            self._assert(
                error_message in actual_message,
                f"错误消息不匹配",
                expected=f"包含 '{error_message}'",
                actual=actual_message
            )
        
        return self
    
    def complete_within(self, seconds: float):
        """响应时间断言"""
        # 这里需要在调用时记录时间，暂时跳过实现
        # TODO: 在APIClient中实现响应时间记录
        return self
    
    def _get_nested_value(self, data: Dict, path: str):
        """获取嵌套字段值"""
        if not isinstance(data, dict):
            return None
        
        keys = path.split(".")
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        
        return current
    
    def _assert_with_operator(self, actual: Any, operator: str, expected: Any, field: str):
        """使用操作符进行断言"""
        if operator == "contains":
            self._assert(
                expected in str(actual),
                f"字段 '{field}' 不包含期望值",
                expected=f"包含 '{expected}'",
                actual=actual
            )
        elif operator == "exists":
            self._assert(
                actual is not None,
                f"字段 '{field}' 不存在",
                expected="存在",
                actual=actual
            )
        elif operator == "gt":
            self._assert(
                float(actual) > float(expected),
                f"字段 '{field}' 不大于期望值",
                expected=f"> {expected}",
                actual=actual
            )
        elif operator == "gte":
            self._assert(
                float(actual) >= float(expected),
                f"字段 '{field}' 不大于等于期望值",
                expected=f">= {expected}",
                actual=actual
            )
        elif operator == "lt":
            self._assert(
                float(actual) < float(expected),
                f"字段 '{field}' 不小于期望值",
                expected=f"< {expected}",
                actual=actual
            )
        elif operator == "lte":
            self._assert(
                float(actual) <= float(expected),
                f"字段 '{field}' 不小于等于期望值",
                expected=f"<= {expected}",
                actual=actual
            )
        else:
            raise ValueError(f"不支持的操作符: {operator}")


class PerformanceAssertion(BaseAssertion):
    """性能断言"""
    
    def complete_within(self, seconds: float):
        """完成时间断言"""
        if hasattr(self.value, 'elapsed'):
            actual_seconds = self.value.elapsed.total_seconds()
        elif isinstance(self.value, (int, float)):
            actual_seconds = float(self.value)
        else:
            self._assert(False, "无法获取执行时间", expected="时间值", actual=type(self.value))
            return self
        
        self._assert(
            actual_seconds <= seconds,
            f"执行时间超出限制",
            expected=f"<= {seconds}s",
            actual=f"{actual_seconds:.3f}s"
        )
        return self
    
    def have_throughput_at_least(self, requests_per_second: float):
        """吞吐量断言"""
        # TODO: 实现吞吐量断言
        return self


# 工厂函数
def expect(value: Any, description: str = "") -> BaseAssertion:
    """创建基础断言"""
    if isinstance(value, str):
        return StringAssertion(value, description)
    elif isinstance(value, (int, float)):
        return NumberAssertion(value, description)
    elif isinstance(value, (list, tuple, set)):
        return CollectionAssertion(value, description)
    elif isinstance(value, dict):
        return DictionaryAssertion(value, description)
    elif hasattr(value, 'status_code'):  # HTTP响应
        return ResponseAssertion(value, description)
    else:
        return BaseAssertion(value, description)


def expect_response(response: requests.Response, description: str = "") -> ResponseAssertion:
    """创建响应断言"""
    return ResponseAssertion(response, description)


def expect_performance(value: Any, description: str = "") -> PerformanceAssertion:
    """创建性能断言"""
    return PerformanceAssertion(value, description)


# 便捷断言函数
def assert_equal(actual: Any, expected: Any, message: str = ""):
    """相等断言便捷函数"""
    expect(actual, message).equal(expected)


def assert_not_equal(actual: Any, expected: Any, message: str = ""):
    """不相等断言便捷函数"""
    expect(actual, message).not_equal(expected)


def assert_true(value: Any, message: str = ""):
    """真值断言便捷函数"""
    expect(value, message).be_true()


def assert_false(value: Any, message: str = ""):
    """假值断言便捷函数"""
    expect(value, message).be_false()


def assert_none(value: Any, message: str = ""):
    """空值断言便捷函数"""
    expect(value, message).be_none()


def assert_not_none(value: Any, message: str = ""):
    """非空值断言便捷函数"""
    expect(value, message).not_be_none()


def assert_contains(container: Any, item: Any, message: str = ""):
    """包含断言便捷函数"""
    expect(container, message).contain_item(item)


def assert_length(collection: Any, expected_length: int, message: str = ""):
    """长度断言便捷函数"""
    expect(collection, message).have_length(expected_length) 