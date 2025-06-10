import json
from typing import Dict, Any
from datetime import datetime

class ProtocolParser:
    """协议解析器"""
    
    def __init__(self):
        self.known_ports = {
            80: "HTTP",
            443: "HTTPS",
            22: "SSH",
            23: "Telnet",
            21: "FTP",
            25: "SMTP",
            53: "DNS",
            1883: "MQTT",
            5683: "CoAP"
        }
        
    def parse_packet(self, packet_info: Dict) -> Dict[str, Any]:
        """解析数据包信息"""
        parsed = {
            "timestamp": packet_info["timestamp"],
            "src_ip": packet_info["src_ip"],
            "dst_ip": packet_info["dst_ip"],
            "length": packet_info["length"],
            "protocol_name": self._get_protocol_name(packet_info),
            "is_iot_traffic": self._is_iot_traffic(packet_info),
            "risk_level": self._assess_risk(packet_info)
        }
        
        return parsed
        
    def _get_protocol_name(self, packet_info: Dict) -> str:
        """获取协议名称"""
        dst_port = packet_info.get("dst_port")
        src_port = packet_info.get("src_port")
        
        if dst_port in self.known_ports:
            return self.known_ports[dst_port]
        elif src_port in self.known_ports:
            return self.known_ports[src_port]
        else:
            return "Unknown"
            
    def _is_iot_traffic(self, packet_info: Dict) -> bool:
        """判断是否为IoT流量"""
        iot_ports = [1883, 5683, 8883]  # MQTT, CoAP, MQTT over SSL
        dst_port = packet_info.get("dst_port")
        src_port = packet_info.get("src_port")
        
        return dst_port in iot_ports or src_port in iot_ports
        
    def _assess_risk(self, packet_info: Dict) -> str:
        """评估风险等级"""
        # 简单的风险评估逻辑
        if packet_info.get("dst_port") == 23:  # Telnet
            return "high"
        elif packet_info.get("length", 0) > 1500:  # 大包
            return "medium"
        else:
            return "low"