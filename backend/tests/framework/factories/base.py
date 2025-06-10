"""数据工厂基类

提供通用的测试数据生成功能
"""

import uuid
import random
import string
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, TypeVar, Generic
from abc import ABC, abstractmethod

T = TypeVar('T')


class DataFactory(ABC, Generic[T]):
    """数据工厂基类"""
    
    def __init__(self):
        self.defaults = {}
        self.traits = {}
        self.sequences = {}
        self._generated_objects = []
    
    @property
    def model_class(self):
        """需要子类实现，返回模型类"""
        return dict
    
    def create(self, **kwargs) -> T:
        """创建单个对象"""
        data = self._build_data(**kwargs)
        obj = self._create_instance(data)
        self._generated_objects.append(obj)
        return obj
    
    def create_batch(self, count: int, **kwargs) -> List[T]:
        """批量创建对象"""
        return [self.create(**kwargs) for _ in range(count)]
    
    def build(self, **kwargs) -> Dict[str, Any]:
        """构建数据但不创建实例"""
        return self._build_data(**kwargs)
    
    def build_batch(self, count: int, **kwargs) -> List[Dict[str, Any]]:
        """批量构建数据"""
        return [self.build(**kwargs) for _ in range(count)]
    
    def with_trait(self, trait_name: str):
        """应用特征数据"""
        if trait_name in self.traits:
            factory = self.__class__()
            factory.defaults = {**self.defaults, **self.traits[trait_name]}
            factory.traits = self.traits
            factory.sequences = self.sequences
            return factory
        return self
    
    def sequence(self, field: str, func: Callable[[int], Any]):
        """定义序列字段"""
        self.sequences[field] = func
        return self
    
    def _build_data(self, **kwargs) -> Dict[str, Any]:
        """构建数据字典"""
        data = {}
        
        # 1. 应用默认值
        for key, value in self.defaults.items():
            data[key] = self._resolve_value(value)
        
        # 2. 应用序列值
        for key, func in self.sequences.items():
            if key not in kwargs:
                seq_num = len([obj for obj in self._generated_objects])
                data[key] = func(seq_num)
        
        # 3. 应用用户提供的值
        data.update(kwargs)
        
        return data
    
    def _resolve_value(self, value: Any) -> Any:
        """解析值（处理函数调用）"""
        if callable(value):
            return value()
        return value
    
    def _create_instance(self, data: Dict[str, Any]) -> T:
        """创建实例（子类可重写）"""
        if self.model_class == dict:
            return data
        return self.model_class(**data)
    
    def cleanup(self):
        """清理生成的对象"""
        self._generated_objects.clear()


class FactoryRegistry:
    """工厂注册表"""
    
    _factories = {}
    
    @classmethod
    def register(cls, name: str, factory_class):
        """注册工厂"""
        cls._factories[name] = factory_class
    
    @classmethod
    def get(cls, name: str) -> DataFactory:
        """获取工厂实例"""
        if name not in cls._factories:
            raise ValueError(f"Factory '{name}' not registered")
        return cls._factories[name]()
    
    @classmethod
    def create(cls, name: str, **kwargs):
        """使用工厂创建对象"""
        factory = cls.get(name)
        return factory.create(**kwargs)


def random_string(length: int = 8) -> str:
    """生成随机字符串"""
    return ''.join(random.choices(string.ascii_lowercase, k=length))


def random_email() -> str:
    """生成随机邮箱"""
    return f"test_{random_string()}@example.com"


def random_phone() -> str:
    """生成随机手机号"""
    return f"138{random.randint(10000000, 99999999)}"


def random_card_number() -> str:
    """生成随机卡号"""
    return f"6225{random.randint(100000000000, 999999999999)}"


def random_future_date(days: int = 365) -> datetime:
    """生成未来日期"""
    return datetime.now() + timedelta(days=random.randint(30, days))


def random_amount(min_val: float = 1.0, max_val: float = 10000.0) -> float:
    """生成随机金额"""
    return round(random.uniform(min_val, max_val), 2) 