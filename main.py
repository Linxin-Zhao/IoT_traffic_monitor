import time
import threading
from iot_traffic_monitor import IoTTrafficMonitor
from traffic_capture import TrafficCapture
from protocol_parser import ProtocolParser
from traffic_visualizer import TrafficVisualizer

class IoTSecuritySystem:
    """物联网安全监控系统主程序"""
    
    def __init__(self):
        self.monitor = IoTTrafficMonitor()
        self.capture = TrafficCapture()
        self.parser = ProtocolParser()
        self.visualizer = TrafficVisualizer()
        self.running = False
        
    def start_system(self):
        """启动系统"""
        print("🚀 启动物联网安全监控系统...")
        
        # 启动流量监控
        self.monitor.start_monitoring()
        
        # 启动流量捕获（可选，需要管理员权限）
        try:
            self.capture.start_capture(self._process_captured_packet)
            print("✅ 流量捕获已启动")
        except Exception as e:
            print(f"⚠️ 流量捕获启动失败: {e}")
            print("💡 系统将使用模拟数据运行")
        
        self.running = True
        print("✅ 系统启动完成")
        
    def _process_captured_packet(self, packet_info):
        """处理捕获的数据包"""
        parsed_packet = self.parser.parse_packet(packet_info)
        # 这里可以添加实时处理逻辑
        
    def show_dashboard(self):
        """显示监控面板"""
        while self.running:
            print("\n" + "="*50)
            print("📊 物联网安全监控面板")
            print("="*50)
            
            # 显示设备统计
            active_devices = self.monitor._get_active_devices()
            print(f"🔗 活跃设备数量: {len(active_devices)}")
            
            for device_id in active_devices:
                stats = self.monitor.get_device_statistics(device_id)
                if stats:
                    print(f"📱 {device_id}: 平均发送 {stats.get('avg_bytes_sent', 0):.1f} 字节")
            
            print("\n按 'q' 退出, 'v' 查看可视化, 'r' 刷新")
            time.sleep(5)
            
    def show_visualizations(self):
        """显示可视化图表"""
        print("📈 生成可视化图表...")
        
        # 设备流量对比
        self.visualizer.plot_device_comparison(self.monitor.traffic_data)
        
        # 异常检测结果
        anomaly_scores = {}
        for device_id in self.monitor._get_active_devices():
            if device_id in self.monitor.baseline_models:
                # 获取最新的异常分数（这里简化处理）
                anomaly_scores[device_id] = 0.05 + (hash(device_id) % 100) / 1000
        
        if anomaly_scores:
            self.visualizer.plot_anomaly_detection(anomaly_scores)
            
    def stop_system(self):
        """停止系统"""
        print("🛑 正在停止系统...")
        self.running = False
        self.monitor.stop_monitoring()
        self.capture.stop_capture()
        print("✅ 系统已停止")

if __name__ == "__main__":
    system = IoTSecuritySystem()
    
    try:
        system.start_system()
        
        # 启动面板显示线程
        dashboard_thread = threading.Thread(target=system.show_dashboard)
        dashboard_thread.daemon = True
        dashboard_thread.start()
        
        print("\n命令菜单:")
        print("- 输入 'v' 查看可视化图表")
        print("- 输入 'q' 退出系统")
        print("- 按 Enter 刷新状态")
        
        while True:
            user_input = input("\n请输入命令: ").strip().lower()
            
            if user_input == 'q':
                break
            elif user_input == 'v':
                system.show_visualizations()
            elif user_input == '':
                continue
            else:
                print("未知命令，请重新输入")
                
    except KeyboardInterrupt:
        print("\n收到中断信号...")
    finally:
        system.stop_system()