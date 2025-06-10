#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
物联网安全监控系统 GUI 启动脚本
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """检查依赖库"""
    required_modules = [
        'numpy', 'sklearn', 'matplotlib', 'tkinter'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"缺少以下依赖库: {', '.join(missing_modules)}\n\n"
        error_msg += "请运行以下命令安装:\n"
        error_msg += "pip install -r requirements.txt"
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("依赖错误", error_msg)
        return False
    
    return True

def main():
    """主函数"""
    print("🚀 启动物联网安全监控系统 GUI...")
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败")
        return
    
    try:
        # 导入GUI模块
        from iot_gui import main as gui_main
        
        print("✅ 依赖检查通过")
        print("🖥️ 启动图形界面...")
        
        # 启动GUI
        gui_main()
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保所有文件都在正确位置")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()