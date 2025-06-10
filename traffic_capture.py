import scapy.all as scapy
import threading
import time
from collections import defaultdict
from datetime import datetime
from typing import Dict, Callable

class TrafficCapture:
    """网络流量采集模块"""
    
    def __init__(self, interface: str = None):
        self.interface = interface
        self.running = False
        self.packet_callback = None
        self.capture_thread = None
        
    def start_capture(self, callback: Callable):
        """开始抓包"""
        self.packet_callback = callback
        self.running = True
        
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
    def _capture_loop(self):
        """抓包循环"""
        try:
            scapy.sniff(
                iface=self.interface,
                prn=self._process_packet,
                stop_filter=lambda x: not self.running
            )
        except Exception as e:
            print(f"抓包错误: {e}")
            
    def _process_packet(self, packet):
        """处理数据包"""
        if self.packet_callback:
            packet_info = {
                "timestamp": datetime.now(),
                "src_ip": packet[scapy.IP].src if scapy.IP in packet else None,
                "dst_ip": packet[scapy.IP].dst if scapy.IP in packet else None,
                "protocol": packet[scapy.IP].proto if scapy.IP in packet else None,
                "length": len(packet),
                "src_port": packet[scapy.TCP].sport if scapy.TCP in packet else 
                           (packet[scapy.UDP].sport if scapy.UDP in packet else None),
                "dst_port": packet[scapy.TCP].dport if scapy.TCP in packet else 
                           (packet[scapy.UDP].dport if scapy.UDP in packet else None)
            }
            self.packet_callback(packet_info)
            
    def stop_capture(self):
        """停止抓包"""
        self.running = False