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
        cost_time = int(round(time.time() - start_time, 3)*1000)
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
    port = match.group('port')
    if not port: port = 443
    return ip, port, match.group('name')

# 1. 读取文件并解析
ip_list = []
allips_path = 'allips'
bad_ips_path = 'bad_ips'
with open(bad_ips_path, 'r', encoding='utf-8') as f:
    bad_ips = set(line.split('#')[0].split(':')[0].strip() for line in f if line.strip())
with open('docs/ip_info.json', 'r', encoding='utf-8') as f:
    good_ips_dict = json.load(f)
good_ipv4s_list = good_ips_dict['ipv4']
good_ipv6s_list = good_ips_dict['ipv6']
# 检查goodips文件是否存在
if not os.path.exists(allips_path):
    print(f"错误：未找到{allips_path}文件，路径：{os.path.abspath(allips_path)}")
    exit(1)
try:
    with open(allips_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]  # 过滤空行
except Exception as e:
    print(f"读取{allips_path}文件失败！错误原因：{str(e)}")
    exit(1)

# 检查allips文件是否为空
if not lines:
    print(f"警告：{allips_path}文件为空，生成空JSON")
else:
    # 解析每行数据
    for line_num, line in enumerate(lines, 1):
        ip, port, name = extract_ip_port_name(line)
        success, msg, timeout = test_ip_connection(ip, port)
        bad_ip = None  # 每次循环初始化，避免残留上一次的bad_ip
         
        if success:
            if ip not in bad_ips:
                ip_in_v4 = any(item.get("ip") == ip for item in good_ipv4s_list)
                ip_in_v6 = any(item.get("ip") == ip for item in good_ipv6s_list)
                if not ip_in_v4 and not ip_in_v6:  # 确保IP未在v4/v6列表中，避免重复添加
                    if ':' in ip:
                        good_ipv6s_list.append({"ip": ip, "port": port, "name": name, "timeout": timeout})
                    else:
                        good_ipv4s_list.append({"ip": ip, "port": port, "name": name, "timeout": timeout})
            else:
                print(f'{ip}重复或损坏，已记录至bad_ips')
                bad_ip = ip
        else:
            bad_ip = ip
            if bad_ip not in bad_ips:
                bad_ips.add(bad_ip)
            print(f"{ip}:{port}：{msg}")
         
        if bad_ip:
            target_list = good_ipv6s_list if ':' in bad_ip else good_ipv4s_list
            for item in target_list:
                if item.get("ip") == bad_ip:
                    target_list.remove(item)
                    break  # 仅删除第一个匹配项

good_ips_dict = {'ipv4': good_ipv4s_list, 'ipv6': good_ipv6s_list}

# 2. 保存为JSON文件（确保无论是否有数据都生成文件）
try:
    with open('bad_ips', 'w', encoding='utf-8') as f:
        bad_ips_str = "\n".join(bad_ips)
        f.write(bad_ips_str)
    with open('docs/ip_info.json', 'w', encoding='utf-8') as f:
        json.dump(good_ips_dict, f, indent=2, ensure_ascii=False)
    print(f"JSON文件生成成功！路径：{os.path.abspath('ip_info.json')}，有效数据条数：{len(ip_list)}")
except Exception as e:
    print(f"生成JSON文件失败！错误原因：{str(e)}")
    exit(1)
