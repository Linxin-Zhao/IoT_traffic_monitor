import json
import time
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import numpy as np
from sklearn.ensemble import IsolationForest

class IoTTrafficMonitor:
    """物联网流量监控系统"""
    
    def __init__(self, window_size: int = 300):
        self.window_size = window_size  # 5分钟窗口
        self.traffic_data = defaultdict(lambda: deque(maxlen=window_size))
        self.baseline_models = {}
        self.alert_threshold = 0.1
        self.running = False
        
    def start_monitoring(self):
        """开始监控"""
        self.running = True
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
    def _monitor_loop(self):
        """监控主循环"""
        while self.running:
            current_time = datetime.now()
            
            # 收集当前时间窗口的流量数据
            traffic_stats = self._collect_traffic_stats()
            
            # 检测异常
            for device_id, stats in traffic_stats.items():
                anomaly_score = self._detect_anomaly(device_id, stats)
                if anomaly_score > self.alert_threshold:
                    self._trigger_alert(device_id, stats, anomaly_score)
            
            time.sleep(60)  # 每分钟检查一次
    
    def _collect_traffic_stats(self) -> Dict:
        """收集流量统计信息"""
        # 模拟流量数据收集
        stats = {}
        
        # 这里应该从实际网络接口收集数据
        # 示例数据结构
        for device_id in self._get_active_devices():
            stats[device_id] = {
                "bytes_sent": np.random.normal(1000, 200),
                "bytes_received": np.random.normal(800, 150),
                "packets_sent": np.random.normal(50, 10),
                "packets_received": np.random.normal(40, 8),
                "connection_count": np.random.poisson(5),
                "unique_destinations": np.random.poisson(3)
            }
            
            # 添加到历史数据
            self.traffic_data[device_id].append({
                "timestamp": datetime.now(),
                **stats[device_id]
            })
        
        return stats
    
    def _detect_anomaly(self, device_id: str, current_stats: Dict) -> float:
        """检测异常流量"""
        if device_id not in self.baseline_models:
            self._build_baseline_model(device_id)
            return 0.0
        
        # 提取特征向量
        features = np.array([
            current_stats["bytes_sent"],
            current_stats["bytes_received"],
            current_stats["packets_sent"],
            current_stats["packets_received"],
            current_stats["connection_count"],
            current_stats["unique_destinations"]
        ]).reshape(1, -1)
        
        # 计算异常分数
        model = self.baseline_models[device_id]
        anomaly_score = model.decision_function(features)[0]
        
        return abs(anomaly_score)
    
    def _build_baseline_model(self, device_id: str):
        """构建基线模型"""
        if len(self.traffic_data[device_id]) < 50:  # 需要足够的历史数据
            return
        
        # 提取历史特征
        features = []
        for record in self.traffic_data[device_id]:
            features.append([
                record["bytes_sent"],
                record["bytes_received"],
                record["packets_sent"],
                record["packets_received"],
                record["connection_count"],
                record["unique_destinations"]
            ])
        
        # 训练异常检测模型
        X = np.array(features)
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X)
        
        self.baseline_models[device_id] = model
    
    def _trigger_alert(self, device_id: str, stats: Dict, score: float):
        """触发安全警报"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "device_id": device_id,
            "alert_type": "traffic_anomaly",
            "severity": "high" if score > 0.5 else "medium",
            "anomaly_score": score,
            "traffic_stats": stats,
            "recommended_actions": [
                "检查设备状态",
                "验证网络连接",
                "检查是否存在恶意软件"
            ]
        }
        
        print(f"🚨 安全警报: {json.dumps(alert, indent=2, ensure_ascii=False)}")
        
        # 这里可以集成更多响应机制
        self._auto_response(device_id, alert)
    
    def _auto_response(self, device_id: str, alert: Dict):
        """自动响应机制"""
        if alert["severity"] == "high":
            # 高风险：临时隔离设备
            print(f"⚠️ 自动响应: 设备 {device_id} 已被临时隔离")
            # 实际实现中会调用网络隔离API
        
        # 记录到安全日志
        self._log_security_event(alert)
    
    def _get_active_devices(self) -> List[str]:
        """获取活跃设备列表"""
        # 模拟活跃设备列表
        # 实际实现中应该从网络扫描或设备注册表获取
        return ["device_001", "device_002", "device_003", "sensor_001", "camera_001"]
    
    def _log_security_event(self, event: Dict):
        """记录安全事件到日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "security_alert",
            "details": event
        }
        
        # 写入日志文件
        with open("security_events.log", "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        print(f"📝 安全事件已记录: {event['alert_type']}")
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        print("🛑 流量监控已停止")
    
    def get_device_statistics(self, device_id: str) -> Dict:
        """获取设备统计信息"""
        if device_id not in self.traffic_data:
            return {}
        
        data = list(self.traffic_data[device_id])
        if not data:
            return {}
        
        # 计算统计信息
        stats = {
            "total_records": len(data),
            "avg_bytes_sent": np.mean([d["bytes_sent"] for d in data]),
            "avg_bytes_received": np.mean([d["bytes_received"] for d in data]),
            "max_connections": max([d["connection_count"] for d in data]),
            "last_seen": data[-1]["timestamp"].isoformat() if data else None
        }
        
        return stats
    
    def get_system_status(self) -> Dict:
        """获取系统状态"""
        return {
            "running": self.running,
            "monitored_devices": len(self.traffic_data),
            "trained_models": len(self.baseline_models),
            "alert_threshold": self.alert_threshold,
            "window_size": self.window_size
        }
    
    def update_alert_threshold(self, threshold: float):
        """更新警报阈值"""
        self.alert_threshold = threshold
        print(f"📊 警报阈值已更新为: {threshold}")
    
    def export_traffic_data(self, device_id: str = None) -> Dict:
        """导出流量数据"""
        if device_id:
            if device_id in self.traffic_data:
                return {device_id: list(self.traffic_data[device_id])}
            else:
                return {}
        else:
            # 导出所有设备数据
            export_data = {}
            for dev_id, data in self.traffic_data.items():
                export_data[dev_id] = list(data)
            return export_data

# 主程序入口
if __name__ == "__main__":
    print("🚀 启动物联网流量监控系统...")
    
    # 创建监控实例
    monitor = IoTTrafficMonitor(window_size=300)
    
    try:
        # 开始监控
        monitor.start_monitoring()
        print("✅ 流量监控系统已启动")
        print("📊 系统状态:", monitor.get_system_status())
        print("按 Ctrl+C 停止监控...")
        
        # 保持程序运行并显示实时状态
        while True:
            time.sleep(10)
            
            # 每10秒显示一次系统状态
            status = monitor.get_system_status()
            print(f"\n📈 监控状态: 设备数 {status['monitored_devices']}, 模型数 {status['trained_models']}")
            
            # 显示设备统计
            for device_id in monitor._get_active_devices():
                stats = monitor.get_device_statistics(device_id)
                if stats and stats['total_records'] > 0:
                    print(f"📱 {device_id}: {stats['total_records']} 条记录, 平均发送 {stats['avg_bytes_sent']:.1f} 字节")
            
    except KeyboardInterrupt:
        print("\n🛑 收到停止信号...")
        monitor.stop_monitoring()
        print("👋 流量监控系统已关闭")
        
        # 导出最终数据
        final_data = monitor.export_traffic_data()
        print(f"📁 共收集了 {len(final_data)} 个设备的流量数据")