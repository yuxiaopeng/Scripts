#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import requests
import subprocess
from pathlib import Path
import json

# 配置参数
CHECK_INTERVAL = 300  # 检查间隔时间（秒）
IP_FILE = Path.home() / '.last_ip'  # 存储上次 IP 的文件
RECIPIENT = "uxiaopeng@gmail.com"  # 替换为你要发送 iMessage 的联系人

def get_public_ip():
    """获取外网 IP 地址，尝试多个服务以提高准确性"""
    ip_services = [
        'https://api.ipify.org',
        'https://ifconfig.me/ip',
        'https://icanhazip.com',
        'https://ident.me',
        'https://api.ip.sb/ip'
    ]
    
    for service in ip_services:
        try:
            response = requests.get(service, timeout=10)
            if response.status_code == 200:
                ip = response.text.strip()
                print(f"从 {service} 获取到 IP: {ip}")
                return ip
        except Exception as e:
            print(f"从 {service} 获取 IP 出错: {e}")
    
    return None

def is_vpn_active():
    """检查 VPN 或 Clash Verge 是否处于活动状态"""
    try:
        # 1. 首先检查常规 VPN 服务
        result = subprocess.run(['networksetup', '-listallnetworkservices'], 
                               capture_output=True, text=True, check=True)
        services = result.stdout.strip().split('\n')
        
        # 跳过第一行（标题行）
        for service in services[1:]:
            # 检查是否包含常见的 VPN 关键词
            if 'VPN' in service or 'Cisco' in service or 'Pulse' in service or 'OpenVPN' in service:
                # 检查该服务是否处于活动状态
                check_result = subprocess.run(['networksetup', '-getinfo', service], 
                                            capture_output=True, text=True)
                if 'IP address' in check_result.stdout and not 'IP address: none' in check_result.stdout:
                    print(f"检测到活动的 VPN 连接: {service}")
                    return True
        
        # 2. 检查 Clash Verge 代理设置
        # 检查系统代理设置
        proxy_check = subprocess.run(['scutil', '--proxy'], 
                                    capture_output=True, text=True)
        proxy_output = proxy_check.stdout
        
        # 如果有启用的 HTTP 或 SOCKS 代理，很可能是 Clash Verge
        if ('HTTPEnable : 1' in proxy_output or 'SOCKSEnable : 1' in proxy_output):
            print("检测到系统代理已启用，可能是 Clash Verge")
            return True
            
        # 3. 尝试检查 Clash Verge 进程
        process_check = subprocess.run(['pgrep', '-i', 'clash'], 
                                      capture_output=True, text=True)
        if process_check.stdout.strip():
            print("检测到 Clash 相关进程正在运行")
            return True
        
        return False
    except Exception as e:
        print(f"检查代理状态时出错: {e}")
        return False

def get_ip_info():
    """获取 IP 信息，包括原始 IP 和 VPN IP（如果有）"""
    ip_info = {"current_ip": None, "vpn_active": False, "original_ip": None}
    
    # 获取当前 IP（可能是 VPN IP 或原始 IP）
    ip_info["current_ip"] = get_public_ip()
    
    # 检查 VPN 是否活动
    ip_info["vpn_active"] = is_vpn_active()
    
    # 如果 VPN 活动，尝试获取原始 IP
    if ip_info["vpn_active"]:
        # 临时禁用 VPN 连接的请求（使用系统代理设置）
        original_session = requests.Session()
        original_session.trust_env = False  # 不使用系统代理
        
        try:
            for service in [
                'http://myip.ipip.net'
            ]:
                try:
                    response = original_session.get(service, timeout=5)
                    if response.status_code == 200:
                        ip = response.text.strip()
                        if ip and ip != ip_info["current_ip"]:  # 确保获取到的原始IP与当前IP不同
                            ip_info["original_ip"] = ip
                            print(f"获取到原始 IP: {ip_info['original_ip']}")
                            break
                except Exception as e:
                    print(f"从 {service} 获取原始 IP 出错: {e}")
                    continue
        except Exception as e:
            print(f"获取原始 IP 时出错: {e}")
    
    return ip_info

def send_imessage(recipient, message):
    """通过 iMessage 发送消息"""
    applescript = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{recipient}" of targetService
        send "{message}" to targetBuddy
    end tell
    '''
    try:
        subprocess.run(['osascript', '-e', applescript], check=True)
        print(f"iMessage 已发送到 {recipient}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"发送 iMessage 失败: {e}")
        return False

def read_last_ip_info():
    """读取上次记录的 IP 信息"""
    if IP_FILE.exists():
        try:
            return json.loads(IP_FILE.read_text())
        except:
            return None
    return None

def save_current_ip_info(ip_info):
    """保存当前 IP 信息"""
    IP_FILE.write_text(json.dumps(ip_info))

def main():
    print("开始监控外网 IP 变化...")
    
    while True:
        current_ip_info = get_ip_info()
        
        if current_ip_info["current_ip"]:
            last_ip_info = read_last_ip_info()
            
            if last_ip_info is None:
                # 首次运行
                print(f"首次检测到 IP 信息: {current_ip_info}")
                save_current_ip_info(current_ip_info)
                
                message = f"IP 监控已启动\n完整信息: {current_ip_info}"
                send_imessage(RECIPIENT, message)
            elif (current_ip_info["current_ip"] != last_ip_info.get("current_ip") or 
                  current_ip_info["original_ip"] != last_ip_info.get("original_ip") or
                  current_ip_info["vpn_active"] != last_ip_info.get("vpn_active")):
                # IP 信息已变化
                change_info = f"IP 信息已变化: {last_ip_info} -> {current_ip_info}"
                print(change_info)
                save_current_ip_info(current_ip_info)
                
                # 直接发送完整的变化信息
                send_imessage(RECIPIENT, change_info)
            else:
                print(f"IP 信息未变化: {current_ip_info}")
        else:
            print("无法获取当前 IP")
        
        # 等待下次检查
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()