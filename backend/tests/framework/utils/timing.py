"""时间测量工具

用于性能测试和响应时间监控
"""

import time
import logging
from typing import Dict, List, Optional, Any
from contextlib import contextmanager
from statistics import mean, median


logger = logging.getLogger(__name__)


class TimingHelper:
    """时间测量助手"""
    
    def __init__(self):
        self.measurements: Dict[str, List[float]] = {}
        self.current_timers: Dict[str, float] = {}
    
    def start_timer(self, name: str):
        """开始计时"""
        self.current_timers[name] = time.perf_counter()
        logger.debug(f"开始计时: {name}")
    
    def stop_timer(self, name: str) -> float:
        """停止计时并返回耗时"""
        if name not in self.current_timers:
            raise ValueError(f"计时器 '{name}' 未启动")
        
        start_time = self.current_timers[name]
        elapsed = time.perf_counter() - start_time
        
        # 记录测量结果
        if name not in self.measurements:
            self.measurements[name] = []
        self.measurements[name].append(elapsed)
        
        del self.current_timers[name]
        logger.debug(f"停止计时: {name}, 耗时: {elapsed:.3f}s")
        
        return elapsed
    
    @contextmanager
    def measure(self, name: str):
        """计时上下文管理器"""
        self.start_timer(name)
        try:
            yield
        finally:
            self.stop_timer(name)
    
    def get_stats(self, name: str) -> Dict[str, float]:
        """获取统计信息"""
        if name not in self.measurements:
            return {}
        
        times = self.measurements[name]
        return {
            "count": len(times),
            "total": sum(times),
            "mean": mean(times),
            "median": median(times),
            "min": min(times),
            "max": max(times)
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """获取所有统计信息"""
        return {name: self.get_stats(name) for name in self.measurements.keys()}
    
    def clear_measurements(self, name: Optional[str] = None):
        """清除测量记录"""
        if name:
            self.measurements.pop(name, None)
        else:
            self.measurements.clear()
    
    def assert_response_time(self, name: str, max_time: float):
        """断言响应时间"""
        stats = self.get_stats(name)
        if not stats:
            raise AssertionError(f"没有找到计时器 '{name}' 的测量数据")
        
        if stats["mean"] > max_time:
            raise AssertionError(
                f"平均响应时间 {stats['mean']:.3f}s 超过了限制 {max_time:.3f}s"
            )
        
        logger.info(f"✅ 响应时间检查通过: {name} (平均 {stats['mean']:.3f}s)")
    
    def print_stats(self, name: Optional[str] = None):
        """打印统计信息"""
        if name:
            stats = self.get_stats(name)
            if stats:
                print(f"\n⏱️  {name} 性能统计:")
                print(f"  执行次数: {stats['count']}")
                print(f"  总耗时: {stats['total']:.3f}s")
                print(f"  平均耗时: {stats['mean']:.3f}s")
                print(f"  中位数: {stats['median']:.3f}s")
                print(f"  最小值: {stats['min']:.3f}s")
                print(f"  最大值: {stats['max']:.3f}s")
        else:
            all_stats = self.get_all_stats()
            if all_stats:
                print("\n⏱️  性能统计汇总:")
                print("=" * 60)
                for timer_name, stats in all_stats.items():
                    print(f"{timer_name}:")
                    print(f"  执行 {stats['count']} 次，平均 {stats['mean']:.3f}s")
                print("=" * 60)


class PerformanceBenchmark:
    """性能基准测试"""
    
    def __init__(self, name: str):
        self.name = name
        self.timer = TimingHelper()
        self.benchmarks: Dict[str, float] = {}
    
    def set_benchmark(self, operation: str, max_time: float):
        """设置性能基准"""
        self.benchmarks[operation] = max_time
        logger.info(f"设置性能基准: {operation} <= {max_time:.3f}s")
    
    def measure_operation(self, operation: str, func, *args, **kwargs):
        """测量操作性能"""
        with self.timer.measure(operation):
            result = func(*args, **kwargs)
        
        # 检查是否超过基准
        if operation in self.benchmarks:
            self.timer.assert_response_time(operation, self.benchmarks[operation])
        
        return result
    
    def run_stress_test(self, operation: str, func, iterations: int = 100):
        """运行压力测试"""
        logger.info(f"开始压力测试: {operation} ({iterations} 次)")
        
        failures = 0
        for i in range(iterations):
            try:
                with self.timer.measure(f"{operation}_stress"):
                    func()
            except Exception as e:
                failures += 1
                logger.warning(f"第 {i+1} 次执行失败: {e}")
        
        success_rate = ((iterations - failures) / iterations) * 100
        stats = self.timer.get_stats(f"{operation}_stress")
        
        print(f"\n🔥 压力测试结果: {operation}")
        print(f"  执行次数: {iterations}")
        print(f"  成功次数: {iterations - failures}")
        print(f"  失败次数: {failures}")
        print(f"  成功率: {success_rate:.1f}%")
        if stats:
            print(f"  平均响应时间: {stats['mean']:.3f}s")
            print(f"  最慢响应时间: {stats['max']:.3f}s")
        
        return {
            "iterations": iterations,
            "failures": failures,
            "success_rate": success_rate,
            "stats": stats
        }


# 全局计时器实例
global_timer = TimingHelper()


@contextmanager
def time_operation(name: str):
    """操作计时上下文管理器"""
    with global_timer.measure(name):
        yield


def timed_test(max_time: float = None):
    """计时测试装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            operation_name = func.__name__
            
            with global_timer.measure(operation_name):
                result = func(*args, **kwargs)
            
            if max_time:
                global_timer.assert_response_time(operation_name, max_time)
            
            return result
        return wrapper
    return decorator 