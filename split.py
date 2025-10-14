import re
import json
import os
import socket
import time

def test_ip_connection(ip, port, timeout=3):
    """
    测试IP+端口的TCP连接
    :param ip: 目标IP
    :param port: 目标端口（int类型，如无端口可传None）
    :param timeout: 超时时间（秒）
    :return: (bool, str)：连接结果（True/False）、状态描述
    """
    if not port: port = 443
    
    try:
        # 创建TCP socket
        if '.' in ip:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # IPv4+TCP
            target_addr = (ip, int(port))
        else:
            sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            addr_info = socket.getaddrinfo(ip, int(port), socket.AF_INET6, socket.SOCK_STREAM)
            target_addr = addr_info[0][4]  # 提取IPv6地址元组（含scope_id）
        sock.settimeout(timeout)
        start_time = time.time()
        sock.connect(target_addr)  # 建立连接
        sock.close()
        cost_time = round(time.time() - start_time, 2)
        return True, f"连接成功 耗时：", cost_time
    except socket.timeout:
        return False, f"连接超时", -1
    except ConnectionRefusedError:
        return False, "端口拒绝连接（端口关闭或服务未启动）", -1
    except Exception as e:
        return False, f"连接失败：{str(e)}", -1

def extract_ip_port_name(s):
    """彻底修复括号问题，兼容IPv4/IPv6，简化正则结构"""
    pattern = r'^(?P<ip>(?:\[[0-9a-fA-F:]+\]|[0-9a-fA-F:]+|\d+\.\d+\.\d+\.\d+))(:(?P<port>\d+))?(#(?P<name>.+))?$'
    match = re.match(pattern, s.strip(), re.IGNORECASE)
    if not match:
        return None, None, None
    ip = match.group('ip')
    ip = ip[1:-1] if ip and ip.startswith('[') and ip.endswith(']') else ip
    return ip, match.group('port'), match.group('name')

# 1. 读取文件并解析
ip_list = []
goodip_path = 'goodips'

# 检查goodips文件是否存在
if not os.path.exists(goodip_path):
    print(f"错误：未找到{goodip_path}文件，路径：{os.path.abspath(goodip_path)}")
    exit(1)

try:
    with open(goodip_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]  # 过滤空行
except Exception as e:
    print(f"读取{goodip_path}文件失败！错误原因：{str(e)}")
    exit(1)

ipv4_list = []
ipv6_list = []
# 检查goodips文件是否为空
if not lines:
    print(f"警告：{goodip_path}文件为空，生成空JSON")
else:
    # 解析每行数据
    for line_num, line in enumerate(lines, 1):
        ip, port, name = extract_ip_port_name(line)
        success, msg, timeout = test_ip_connection(ip, port)
        if success:
            if ':' in ip:
                ipv6_list.append({"ip": ip, "port": port, "name": name, 'timeout': timeout})
            else:
                ipv4_list.append({"ip": ip, "port": port, "name": name, 'timeout': timeout})
        else:
            print(f'{ip}:{port)：{msg}')
            
ip_dict = {'ipv4': ipv4_list, 'ipv6': ipv6_list}

# 2. 保存为JSON文件（确保无论是否有数据都生成文件）
try:
    with open('ip_info.json', 'w', encoding='utf-8') as f:
        json.dump(ip_dict, f, indent=2, ensure_ascii=False)
    print(f"JSON文件生成成功！路径：{os.path.abspath('ip_info.json')}，有效数据条数：{len(ip_list)}")
except Exception as e:
    print(f"生成JSON文件失败！错误原因：{str(e)}")
    exit(1)
