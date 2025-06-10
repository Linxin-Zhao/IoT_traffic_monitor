import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np

class TrafficVisualizer:
    """流量可视化模块"""
    
    def __init__(self):
        plt.style.use('seaborn-v0_8')
        
    def plot_traffic_timeline(self, traffic_data: Dict, device_id: str):
        """绘制流量时间线"""
        if device_id not in traffic_data:
            print(f"设备 {device_id} 无数据")
            return
            
        data = list(traffic_data[device_id])
        if not data:
            return
            
        timestamps = [d["timestamp"] for d in data]
        bytes_sent = [d["bytes_sent"] for d in data]
        bytes_received = [d["bytes_received"] for d in data]
        
        plt.figure(figsize=(12, 6))
        plt.plot(timestamps, bytes_sent, label="发送字节", color="blue")
        plt.plot(timestamps, bytes_received, label="接收字节", color="red")
        plt.title(f"设备 {device_id} 流量时间线")
        plt.xlabel("时间")
        plt.ylabel("字节数")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
    def plot_device_comparison(self, traffic_data: Dict):
        """绘制设备流量对比"""
        device_stats = {}
        
        for device_id, data in traffic_data.items():
            if data:
                recent_data = list(data)[-10:]  # 最近10条记录
                avg_sent = np.mean([d["bytes_sent"] for d in recent_data])
                avg_received = np.mean([d["bytes_received"] for d in recent_data])
                device_stats[device_id] = {"sent": avg_sent, "received": avg_received}
        
        if not device_stats:
            print("无设备数据")
            return
            
        devices = list(device_stats.keys())
        sent_values = [device_stats[d]["sent"] for d in devices]
        received_values = [device_stats[d]["received"] for d in devices]
        
        x = np.arange(len(devices))
        width = 0.35
        
        plt.figure(figsize=(10, 6))
        plt.bar(x - width/2, sent_values, width, label="平均发送", color="skyblue")
        plt.bar(x + width/2, received_values, width, label="平均接收", color="lightcoral")
        
        plt.title("设备流量对比")
        plt.xlabel("设备ID")
        plt.ylabel("平均字节数")
        plt.xticks(x, devices, rotation=45)
        plt.legend()
        plt.tight_layout()
        plt.show()
        
    def plot_anomaly_detection(self, anomaly_scores: Dict):
        """绘制异常检测结果"""
        devices = list(anomaly_scores.keys())
        scores = list(anomaly_scores.values())
        
        colors = ['red' if score > 0.1 else 'green' for score in scores]
        
        plt.figure(figsize=(10, 6))
        bars = plt.bar(devices, scores, color=colors)
        plt.axhline(y=0.1, color='red', linestyle='--', label='异常阈值')
        plt.title("设备异常检测分数")
        plt.xlabel("设备ID")
        plt.ylabel("异常分数")
        plt.xticks(rotation=45)
        plt.legend()
        
        # 添加数值标签
        for bar, score in zip(bars, scores):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{score:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.show()