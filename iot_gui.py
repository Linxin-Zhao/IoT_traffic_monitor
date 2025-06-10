import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from iot_traffic_monitor import IoTTrafficMonitor
from traffic_visualizer import TrafficVisualizer
import time

class IoTMonitorGUI:
    """物联网流量监控系统GUI界面"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("物联网流量监控与安全系统")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 初始化监控系统
        self.monitor = IoTTrafficMonitor()
        self.visualizer = TrafficVisualizer()
        self.monitoring_active = False
        
        # 创建界面
        self.create_widgets()
        self.setup_layout()
        
        # 启动状态更新线程
        self.update_thread = threading.Thread(target=self.update_status_loop, daemon=True)
        self.update_thread.start()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主标题
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill='x', padx=5, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🛡️ 物联网安全监控系统", 
                              font=('Arial', 18, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(expand=True)
        
        # 创建主容器
        main_container = tk.Frame(self.root, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 左侧控制面板
        self.create_control_panel(main_container)
        
        # 右侧显示区域
        self.create_display_area(main_container)
    
    def create_control_panel(self, parent):
        """创建左侧控制面板"""
        control_frame = tk.LabelFrame(parent, text="控制面板", font=('Arial', 12, 'bold'),
                                     bg='#ecf0f1', fg='#2c3e50')
        control_frame.pack(side='left', fill='y', padx=(0, 5))
        
        # 监控控制
        monitor_frame = tk.LabelFrame(control_frame, text="监控控制", bg='#ecf0f1')
        monitor_frame.pack(fill='x', padx=10, pady=5)
        
        self.start_btn = tk.Button(monitor_frame, text="🚀 开始监控", 
                                  command=self.start_monitoring,
                                  bg='#27ae60', fg='white', font=('Arial', 10, 'bold'))
        self.start_btn.pack(fill='x', padx=5, pady=2)
        
        self.stop_btn = tk.Button(monitor_frame, text="🛑 停止监控", 
                                 command=self.stop_monitoring,
                                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                                 state='disabled')
        self.stop_btn.pack(fill='x', padx=5, pady=2)
        
        # 系统状态
        status_frame = tk.LabelFrame(control_frame, text="系统状态", bg='#ecf0f1')
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=8, width=30,
                                                    font=('Consolas', 9))
        self.status_text.pack(fill='both', padx=5, pady=5)
        
        # 设备管理
        device_frame = tk.LabelFrame(control_frame, text="设备管理", bg='#ecf0f1')
        device_frame.pack(fill='x', padx=10, pady=5)
        
        self.device_listbox = tk.Listbox(device_frame, height=6, font=('Arial', 9))
        self.device_listbox.pack(fill='x', padx=5, pady=5)
        self.device_listbox.bind('<<ListboxSelect>>', self.on_device_select)
        
        # 配置设置
        config_frame = tk.LabelFrame(control_frame, text="配置设置", bg='#ecf0f1')
        config_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(config_frame, text="警报阈值:", bg='#ecf0f1').pack(anchor='w', padx=5)
        self.threshold_var = tk.DoubleVar(value=0.1)
        threshold_scale = tk.Scale(config_frame, from_=0.01, to=1.0, resolution=0.01,
                                  orient='horizontal', variable=self.threshold_var,
                                  command=self.update_threshold)
        threshold_scale.pack(fill='x', padx=5, pady=2)
        
        # 操作按钮
        action_frame = tk.LabelFrame(control_frame, text="操作", bg='#ecf0f1')
        action_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(action_frame, text="📊 生成报告", command=self.generate_report,
                 bg='#3498db', fg='white').pack(fill='x', padx=5, pady=2)
        
        tk.Button(action_frame, text="📈 显示图表", command=self.show_charts,
                 bg='#9b59b6', fg='white').pack(fill='x', padx=5, pady=2)
        
        tk.Button(action_frame, text="💾 导出数据", command=self.export_data,
                 bg='#f39c12', fg='white').pack(fill='x', padx=5, pady=2)
    
    def create_display_area(self, parent):
        """创建右侧显示区域"""
        display_frame = tk.Frame(parent, bg='#f0f0f0')
        display_frame.pack(side='right', fill='both', expand=True)
        
        # 创建选项卡
        self.notebook = ttk.Notebook(display_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # 实时监控选项卡
        self.create_realtime_tab()
        
        # 设备详情选项卡
        self.create_device_tab()
        
        # 安全警报选项卡
        self.create_alert_tab()
        
        # 统计分析选项卡
        self.create_stats_tab()
    
    def create_realtime_tab(self):
        """创建实时监控选项卡"""
        realtime_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(realtime_frame, text="📡 实时监控")
        
        # 创建图表区域
        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, realtime_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)
        
        # 初始化子图
        self.ax1 = self.fig.add_subplot(221)
        self.ax2 = self.fig.add_subplot(222)
        self.ax3 = self.fig.add_subplot(223)
        self.ax4 = self.fig.add_subplot(224)
        
        self.fig.tight_layout()
    
    def create_device_tab(self):
        """创建设备详情选项卡"""
        device_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(device_frame, text="📱 设备详情")
        
        # 设备信息显示
        info_frame = tk.LabelFrame(device_frame, text="设备信息", font=('Arial', 12, 'bold'))
        info_frame.pack(fill='x', padx=10, pady=5)
        
        self.device_info_text = scrolledtext.ScrolledText(info_frame, height=15,
                                                         font=('Consolas', 10))
        self.device_info_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def create_alert_tab(self):
        """创建安全警报选项卡"""
        alert_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(alert_frame, text="🚨 安全警报")
        
        # 警报列表
        alert_list_frame = tk.LabelFrame(alert_frame, text="警报历史", font=('Arial', 12, 'bold'))
        alert_list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 创建树形视图显示警报
        columns = ('时间', '设备', '类型', '严重程度', '分数')
        self.alert_tree = ttk.Treeview(alert_list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.alert_tree.heading(col, text=col)
            self.alert_tree.column(col, width=120)
        
        # 添加滚动条
        alert_scrollbar = ttk.Scrollbar(alert_list_frame, orient='vertical', command=self.alert_tree.yview)
        self.alert_tree.configure(yscrollcommand=alert_scrollbar.set)
        
        self.alert_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        alert_scrollbar.pack(side='right', fill='y')
    
    def create_stats_tab(self):
        """创建统计分析选项卡"""
        stats_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(stats_frame, text="📊 统计分析")
        
        # 统计信息显示
        stats_info_frame = tk.LabelFrame(stats_frame, text="系统统计", font=('Arial', 12, 'bold'))
        stats_info_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.stats_text = scrolledtext.ScrolledText(stats_info_frame, height=20,
                                                   font=('Consolas', 10))
        self.stats_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def setup_layout(self):
        """设置布局"""
        # 初始化状态显示
        self.update_status("系统已初始化，等待开始监控...")
        self.update_device_list()
    
    def start_monitoring(self):
        """开始监控"""
        try:
            self.monitor.start_monitoring()
            self.monitoring_active = True
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.update_status("✅ 监控已开始")
            
            # 启动数据更新线程
            self.data_update_thread = threading.Thread(target=self.data_update_loop, daemon=True)
            self.data_update_thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"启动监控失败: {str(e)}")
    
    def stop_monitoring(self):
        """停止监控"""
        try:
            self.monitor.stop_monitoring()
            self.monitoring_active = False
            self.start_btn.config(state='normal')
            self.stop_btn.config(state='disabled')
            self.update_status("🛑 监控已停止")
            
        except Exception as e:
            messagebox.showerror("错误", f"停止监控失败: {str(e)}")
    
    def update_status(self, message):
        """更新状态显示"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        status_msg = f"[{timestamp}] {message}\n"
        
        self.status_text.insert(tk.END, status_msg)
        self.status_text.see(tk.END)
    
    def update_device_list(self):
        """更新设备列表"""
        self.device_listbox.delete(0, tk.END)
        devices = self.monitor._get_active_devices()
        for device in devices:
            self.device_listbox.insert(tk.END, device)
    
    def on_device_select(self, event):
        """设备选择事件"""
        selection = self.device_listbox.curselection()
        if selection:
            device_id = self.device_listbox.get(selection[0])
            self.show_device_details(device_id)
    
    def show_device_details(self, device_id):
        """显示设备详情"""
        stats = self.monitor.get_device_statistics(device_id)
        
        self.device_info_text.delete(1.0, tk.END)
        
        if stats:
            info = f"""设备ID: {device_id}
{'='*50}

📊 统计信息:
• 总记录数: {stats.get('total_records', 0)}
• 平均发送字节: {stats.get('avg_bytes_sent', 0):.2f}
• 平均接收字节: {stats.get('avg_bytes_received', 0):.2f}
• 最大连接数: {stats.get('max_connections', 0)}
• 最后活动: {stats.get('last_seen', 'N/A')}

📈 流量趋势:
"""
            
            # 添加历史数据
            if device_id in self.monitor.traffic_data:
                recent_data = list(self.monitor.traffic_data[device_id])[-10:]
                info += "\n最近10条记录:\n"
                for i, record in enumerate(recent_data, 1):
                    info += f"{i:2d}. {record['timestamp'].strftime('%H:%M:%S')} - "
                    info += f"发送: {record['bytes_sent']:.0f}B, 接收: {record['bytes_received']:.0f}B\n"
        else:
            info = f"设备 {device_id} 暂无数据"
        
        self.device_info_text.insert(1.0, info)
    
    def update_threshold(self, value):
        """更新警报阈值"""
        threshold = float(value)
        self.monitor.update_alert_threshold(threshold)
        self.update_status(f"📊 警报阈值已更新为: {threshold}")
    
    def generate_report(self):
        """生成报告"""
        try:
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "system_status": self.monitor.get_system_status(),
                "device_statistics": {},
                "alert_summary": {
                    "total_alerts": 0,
                    "high_severity": 0,
                    "medium_severity": 0
                }
            }
            
            # 收集设备统计
            for device_id in self.monitor._get_active_devices():
                stats = self.monitor.get_device_statistics(device_id)
                if stats:
                    report_data["device_statistics"][device_id] = stats
            
            # 保存报告
            filename = f"iot_security_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("成功", f"报告已生成: {filename}")
            self.update_status(f"📄 报告已生成: {filename}")
            
        except Exception as e:
            messagebox.showerror("错误", f"生成报告失败: {str(e)}")
    
    def show_charts(self):
        """显示图表"""
        try:
            # 清除现有图表
            for ax in [self.ax1, self.ax2, self.ax3, self.ax4]:
                ax.clear()
            
            devices = self.monitor._get_active_devices()
            
            if not devices:
                self.ax1.text(0.5, 0.5, '暂无设备数据', ha='center', va='center', transform=self.ax1.transAxes)
                self.canvas.draw()
                return
            
            # 图表1: 设备流量对比
            device_stats = {}
            for device_id in devices:
                stats = self.monitor.get_device_statistics(device_id)
                if stats and stats.get('total_records', 0) > 0:
                    device_stats[device_id] = {
                        'sent': stats.get('avg_bytes_sent', 0),
                        'received': stats.get('avg_bytes_received', 0)
                    }
            
            if device_stats:
                devices_list = list(device_stats.keys())
                sent_values = [device_stats[d]['sent'] for d in devices_list]
                received_values = [device_stats[d]['received'] for d in devices_list]
                
                x = np.arange(len(devices_list))
                width = 0.35
                
                self.ax1.bar(x - width/2, sent_values, width, label='发送', color='skyblue')
                self.ax1.bar(x + width/2, received_values, width, label='接收', color='lightcoral')
                self.ax1.set_title('设备流量对比')
                self.ax1.set_xlabel('设备')
                self.ax1.set_ylabel('字节数')
                self.ax1.set_xticks(x)
                self.ax1.set_xticklabels(devices_list, rotation=45)
                self.ax1.legend()
            
            # 图表2: 连接数统计
            if device_stats:
                connection_counts = []
                for device_id in devices_list:
                    if device_id in self.monitor.traffic_data:
                        recent_data = list(self.monitor.traffic_data[device_id])[-5:]
                        if recent_data:
                            avg_connections = np.mean([d['connection_count'] for d in recent_data])
                            connection_counts.append(avg_connections)
                        else:
                            connection_counts.append(0)
                    else:
                        connection_counts.append(0)
                
                self.ax2.pie(connection_counts, labels=devices_list, autopct='%1.1f%%')
                self.ax2.set_title('设备连接数分布')
            
            # 图表3: 时间序列（选择第一个有数据的设备）
            for device_id in devices:
                if device_id in self.monitor.traffic_data and self.monitor.traffic_data[device_id]:
                    data = list(self.monitor.traffic_data[device_id])[-20:]  # 最近20条记录
                    timestamps = [d['timestamp'] for d in data]
                    bytes_sent = [d['bytes_sent'] for d in data]
                    
                    self.ax3.plot(timestamps, bytes_sent, marker='o', label=device_id)
                    self.ax3.set_title(f'{device_id} 流量时间序列')
                    self.ax3.set_xlabel('时间')
                    self.ax3.set_ylabel('发送字节数')
                    self.ax3.tick_params(axis='x', rotation=45)
                    break
            
            # 图表4: 系统状态
            status = self.monitor.get_system_status()
            labels = ['监控设备', '训练模型']
            values = [status['monitored_devices'], status['trained_models']]
            colors = ['#3498db', '#2ecc71']
            
            self.ax4.bar(labels, values, color=colors)
            self.ax4.set_title('系统状态')
            self.ax4.set_ylabel('数量')
            
            self.fig.tight_layout()
            self.canvas.draw()
            
        except Exception as e:
            messagebox.showerror("错误", f"显示图表失败: {str(e)}")
    
    def export_data(self):
        """导出数据"""
        try:
            export_data = self.monitor.export_traffic_data()
            filename = f"iot_traffic_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # 转换datetime对象为字符串
            def convert_datetime(obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: convert_datetime(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_datetime(item) for item in obj]
                return obj
            
            converted_data = convert_datetime(export_data)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(converted_data, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("成功", f"数据已导出: {filename}")
            self.update_status(f"💾 数据已导出: {filename}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出数据失败: {str(e)}")
    
    def update_status_loop(self):
        """状态更新循环"""
        while True:
            try:
                if self.monitoring_active:
                    status = self.monitor.get_system_status()
                    self.root.after(0, lambda: self.update_stats_display(status))
                time.sleep(5)
            except Exception as e:
                print(f"状态更新错误: {e}")
    
    def data_update_loop(self):
        """数据更新循环"""
        while self.monitoring_active:
            try:
                # 更新设备列表
                self.root.after(0, self.update_device_list)
                
                # 更新图表（如果当前在实时监控选项卡）
                if self.notebook.index(self.notebook.select()) == 0:
                    self.root.after(0, self.show_charts)
                
                time.sleep(10)
            except Exception as e:
                print(f"数据更新错误: {e}")
    
    def update_stats_display(self, status):
        """更新统计显示"""
        stats_info = f"""系统统计信息
{'='*50}

🔧 系统状态:
• 监控状态: {'运行中' if status['running'] else '已停止'}
• 监控设备数: {status['monitored_devices']}
• 训练模型数: {status['trained_models']}
• 警报阈值: {status['alert_threshold']}
• 窗口大小: {status['window_size']}

📊 设备详情:
"""
        
        for device_id in self.monitor._get_active_devices():
            device_stats = self.monitor.get_device_statistics(device_id)
            if device_stats and device_stats.get('total_records', 0) > 0:
                stats_info += f"\n📱 {device_id}:"
                stats_info += f"\n  • 记录数: {device_stats['total_records']}"
                stats_info += f"\n  • 平均发送: {device_stats['avg_bytes_sent']:.1f} 字节"
                stats_info += f"\n  • 平均接收: {device_stats['avg_bytes_received']:.1f} 字节"
                stats_info += f"\n  • 最大连接: {device_stats['max_connections']}"
        
        stats_info += f"\n\n🕒 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(1.0, stats_info)

def main():
    """主函数"""
    root = tk.Tk()
    app = IoTMonitorGUI(root)
    
    # 设置窗口关闭事件
    def on_closing():
        if app.monitoring_active:
            app.stop_monitoring()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()