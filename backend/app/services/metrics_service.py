"""
监控指标服务
提供 Prometheus 格式的监控指标
"""
import time
from typing import Dict, Any, List
from dataclasses import dataclass, field
from threading import Lock
from collections import defaultdict


@dataclass
class MetricValue:
    """指标值"""
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


class MetricsCollector:
    """
    指标收集器
    收集和暴露 Prometheus 格式的监控指标
    """

    def __init__(self):
        self._counters: Dict[str, List[MetricValue]] = defaultdict(list)
        self._gauges: Dict[str, List[MetricValue]] = defaultdict(list)
        self._histograms: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._lock = Lock()

    def counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """
        递增计数器

        Args:
            name: 指标名称
            value: 递增值
            labels: 标签
        """
        with self._lock:
            labels = labels or {}
            key = self._make_key(name, labels)

            # 查找现有计数器
            for metric in self._counters[name]:
                if metric.labels == labels:
                    metric.value += value
                    metric.timestamp = time.time()
                    return

            # 创建新计数器
            self._counters[name].append(MetricValue(
                value=value,
                labels=labels,
                timestamp=time.time()
            ))

    def gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """
        设置仪表盘值

        Args:
            name: 指标名称
            value: 当前值
            labels: 标签
        """
        with self._lock:
            labels = labels or {}

            # 查找现有仪表
            for metric in self._gauges[name]:
                if metric.labels == labels:
                    metric.value = value
                    metric.timestamp = time.time()
                    return

            # 创建新仪表
            self._gauges[name].append(MetricValue(
                value=value,
                labels=labels,
                timestamp=time.time()
            ))

    def histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """
        记录直方图值

        Args:
            name: 指标名称
            value: 观测值
            labels: 标签
        """
        with self._lock:
            labels = labels or {}
            key = self._make_key(name, labels)

            if key not in self._histograms[name]:
                self._histograms[name][key] = {
                    "labels": labels,
                    "count": 0,
                    "sum": 0.0,
                    "buckets": {
                        0.005: 0, 0.01: 0, 0.025: 0, 0.05: 0,
                        0.1: 0, 0.25: 0, 0.5: 0, 1.0: 0,
                        2.5: 0, 5.0: 0, 10.0: 0
                    }
                }

            hist = self._histograms[name][key]
            hist["count"] += 1
            hist["sum"] += value

            for bucket in hist["buckets"]:
                if value <= bucket:
                    hist["buckets"][bucket] += 1

    def _make_key(self, name: str, labels: Dict[str, str]) -> str:
        """生成唯一键"""
        if not labels:
            return name
        sorted_labels = sorted(labels.items())
        return f"{name}:{','.join(f'{k}={v}' for k, v in sorted_labels)}"

    def _format_labels(self, labels: Dict[str, str]) -> str:
        """格式化标签为 Prometheus 格式"""
        if not labels:
            return ""
        sorted_labels = sorted(labels.items())
        return "{" + ", ".join(f'{k}="{v}"' for k, v in sorted_labels) + "}"

    def _format_histogram(self, name: str, data: Dict[str, Any]) -> List[str]:
        """格式化直方图为 Prometheus 格式"""
        lines = []
        labels_str = self._format_labels(data["labels"])

        # 添加 bucket
        cumulative = 0
        for bucket, count in sorted(data["buckets"].items()):
            cumulative += count
            bucket_labels = data["labels"].copy()
            bucket_labels["le"] = str(bucket)
            bucket_labels_str = self._format_labels(bucket_labels)
            lines.append(f'{name}_bucket{bucket_labels_str} {cumulative}')

        # 添加 +Inf bucket
        bucket_labels = data["labels"].copy()
        bucket_labels["le"] = "+Inf"
        bucket_labels_str = self._format_labels(bucket_labels)
        lines.append(f'{name}_bucket{bucket_labels_str} {data["count"]}')

        # 添加 sum 和 count
        lines.append(f'{name}_sum{labels_str} {data["sum"]}')
        lines.append(f'{name}_count{labels_str} {data["count"]}')

        return lines

    def export_prometheus(self) -> str:
        """
        导出 Prometheus 格式的指标

        Returns:
            Prometheus 文本格式字符串
        """
        lines = []

        # 添加帮助文本
        lines.append("# HELP sageflow_info SageFlow application info")
        lines.append("# TYPE sageflow_info gauge")
        lines.append('sageflow_info{version="0.5.0"} 1')
        lines.append("")

        # 导出计数器
        if self._counters:
            lines.append("# TYPE sageflow_http_requests_total counter")
            for name, metrics in self._counters.items():
                full_name = f"sageflow_{name}_total"
                for metric in metrics:
                    labels_str = self._format_labels(metric.labels)
                    lines.append(f"{full_name}{labels_str} {metric.value}")
            lines.append("")

        # 导出仪表
        if self._gauges:
            lines.append("# TYPE sageflow gauge")
            for name, metrics in self._gauges.items():
                full_name = f"sageflow_{name}"
                for metric in metrics:
                    labels_str = self._format_labels(metric.labels)
                    lines.append(f"{full_name}{labels_str} {metric.value}")
            lines.append("")

        # 导出直方图
        if self._histograms:
            for name, histograms in self._histograms.items():
                full_name = f"sageflow_{name}"
                lines.append(f"# TYPE {full_name} histogram")
                for key, data in histograms.items():
                    lines.extend(self._format_histogram(full_name, data))
                lines.append("")

        return "\n".join(lines)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """获取指标摘要"""
        with self._lock:
            return {
                "counters": {
                    name: [{"value": m.value, "labels": m.labels}
                           for m in metrics]
                    for name, metrics in self._counters.items()
                },
                "gauges": {
                    name: [{"value": m.value, "labels": m.labels}
                           for m in metrics]
                    for name, metrics in self._gauges.items()
                },
                "histograms": {
                    name: {
                        key: {
                            "count": data["count"],
                            "sum": data["sum"],
                            "labels": data["labels"]
                        }
                        for key, data in histograms.items()
                    }
                    for name, histograms in self._histograms.items()
                }
            }

    def reset(self):
        """重置所有指标"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


# 全局指标收集器
metrics = MetricsCollector()


class RequestMetricsMiddleware:
    """
    请求指标中间件
    自动收集 HTTP 请求的指标
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        method = scope["method"]
        path = scope["path"]

        # 简化路径（移除动态参数）
        simplified_path = self._simplify_path(path)

        # 调用下游应用
        status_code = 500
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # 记录指标
            duration = time.time() - start_time

            # 请求计数
            metrics.counter(
                "http_requests",
                labels={
                    "method": method,
                    "path": simplified_path,
                    "status": str(status_code)
                }
            )

            # 请求耗时
            metrics.histogram(
                "http_request_duration_seconds",
                duration,
                labels={
                    "method": method,
                    "path": simplified_path
                }
            )

    def _simplify_path(self, path: str) -> str:
        """简化路径，移除动态参数"""
        parts = path.split("/")
        simplified = []
        for part in parts:
            # 检测 UUID 或数字 ID
            if len(part) == 36 and part.count("-") == 4:
                simplified.append("{id}")
            elif part.isdigit():
                simplified.append("{id}")
            else:
                simplified.append(part)
        return "/".join(simplified)
