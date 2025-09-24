"""
时间统计工具类
用于API请求处理时间的统计和分析
"""
import time
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)


@dataclass
class TimingInfo:
    """时间统计信息数据类"""
    start_time: float
    end_time: float
    duration_seconds: float
    duration_ms: float
    start_datetime: datetime
    end_datetime: datetime
    is_slow_request: bool = False
    
    def __post_init__(self):
        """计算持续时间"""
        self.duration_seconds = self.end_time - self.start_time
        self.duration_ms = self.duration_seconds * 1000
        self.is_slow_request = self.duration_seconds > 5.0


class TimingContext:
    """时间统计上下文管理器"""
    
    def __init__(self, name: str = "operation"):
        self.name = name
        self.timing_info: Optional[TimingInfo] = None
        
    def __enter__(self):
        self.start_time = time.time()
        self.start_datetime = datetime.utcnow()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.end_datetime = datetime.utcnow()
        
        self.timing_info = TimingInfo(
            start_time=self.start_time,
            end_time=self.end_time,
            start_datetime=self.start_datetime,
            end_datetime=self.end_datetime
        )
        
        # 记录日志
        if self.timing_info.is_slow_request:
            logger.warning(f"SLOW {self.name}: {self.timing_info.duration_ms:.3f}ms")
        else:
            logger.info(f"{self.name}: {self.timing_info.duration_ms:.3f}ms")
    
    @property
    def duration_ms(self) -> float:
        """获取当前持续时间（毫秒）"""
        if hasattr(self, 'start_time'):
            return (time.time() - self.start_time) * 1000
        return 0.0
    
    @property
    def duration_seconds(self) -> float:
        """获取当前持续时间（秒）"""
        if hasattr(self, 'start_time'):
            return time.time() - self.start_time
        return 0.0


@asynccontextmanager
async def async_timing_context(name: str = "async_operation"):
    """异步时间统计上下文管理器"""
    start_time = time.time()
    start_datetime = datetime.utcnow()
    
    try:
        yield start_time
    finally:
        end_time = time.time()
        end_datetime = datetime.utcnow()
        
        timing_info = TimingInfo(
            start_time=start_time,
            end_time=end_time,
            start_datetime=start_datetime,
            end_datetime=end_datetime
        )
        
        # 记录日志
        if timing_info.is_slow_request:
            logger.warning(f"SLOW {name}: {timing_info.duration_ms:.3f}ms")
        else:
            logger.info(f"{name}: {timing_info.duration_ms:.3f}ms")


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.request_times: Dict[str, list] = {}
        self.slow_requests: list = []
        
    def record_request(self, path: str, method: str, duration_ms: float):
        """记录请求时间"""
        key = f"{method} {path}"
        if key not in self.request_times:
            self.request_times[key] = []
        
        self.request_times[key].append(duration_ms)
        
        # 记录慢请求
        if duration_ms > 5000:  # 5秒
            self.slow_requests.append({
                "path": path,
                "method": method,
                "duration_ms": duration_ms,
                "timestamp": datetime.utcnow().isoformat()
            })
    
    def get_average_time(self, path: str, method: str) -> float:
        """获取平均处理时间"""
        key = f"{method} {path}"
        if key not in self.request_times:
            return 0.0
        
        times = self.request_times[key]
        return sum(times) / len(times) if times else 0.0
    
    def get_slow_requests(self, limit: int = 10) -> list:
        """获取慢请求列表"""
        return sorted(self.slow_requests, key=lambda x: x['duration_ms'], reverse=True)[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {}
        for key, times in self.request_times.items():
            if times:
                stats[key] = {
                    "count": len(times),
                    "average_ms": sum(times) / len(times),
                    "min_ms": min(times),
                    "max_ms": max(times),
                    "total_ms": sum(times)
                }
        return stats


# 全局性能监控器实例
performance_monitor = PerformanceMonitor()


def format_duration(duration_seconds: float) -> str:
    """格式化持续时间显示"""
    if duration_seconds < 0.001:
        return f"{duration_seconds * 1000000:.1f}us"  # 使用us而不是μs
    elif duration_seconds < 1.0:
        return f"{duration_seconds * 1000:.3f}ms"
    elif duration_seconds < 60.0:
        return f"{duration_seconds:.3f}s"
    else:
        minutes = int(duration_seconds // 60)
        seconds = duration_seconds % 60
        return f"{minutes}m {seconds:.3f}s"


def get_performance_summary() -> Dict[str, Any]:
    """获取性能摘要"""
    stats = performance_monitor.get_statistics()
    slow_requests = performance_monitor.get_slow_requests()
    
    return {
        "total_endpoints": len(stats),
        "total_requests": sum(s['count'] for s in stats.values()),
        "average_response_time": sum(s['average_ms'] for s in stats.values()) / len(stats) if stats else 0,
        "slow_requests_count": len(slow_requests),
        "slowest_endpoints": sorted(stats.items(), key=lambda x: x[1]['average_ms'], reverse=True)[:5],
        "recent_slow_requests": slow_requests[:5]
    }
