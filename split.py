import re
import json
import os

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

# 检查goodip文件是否存在
if not os.path.exists(goodip_path):
    print(f"错误：未找到{goodip_path}文件，路径：{os.path.abspath(goodip_path)}")
    exit(1)

try:
    with open(goodip_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]  # 过滤空行
except Exception as e:
    print(f"读取{goodip_path}文件失败！错误原因：{str(e)}")
    exit(1)

# 检查goodip文件是否为空
if not lines:
    print(f"警告：{goodip_path}文件为空，生成空JSON")
    ip_list = []
else:
    # 解析每行数据
    for line_num, line in enumerate(lines, 1):
        ip, port, name = extract_ip_port_name(line)
        if ip:
            ip_list.append({"ip": ip, "port": port, "name": name})
        else:
            print(f"警告：第{line_num}行格式无效 → {line}")

# 新增：判断ip_list是否为空（所有行解析失败）
if not ip_list:
    print("警告：ip_list为空（无有效IP解析结果），生成空JSON")

# 2. 保存为JSON文件（确保无论是否有数据都生成文件）
try:
    with open('ip_info.json', 'w', encoding='utf-8') as f:
        json.dump(ip_list, f, indent=2, ensure_ascii=False)
    print(f"JSON文件生成成功！路径：{os.path.abspath('ip_info.json')}，有效数据条数：{len(ip_list)}")
except Exception as e:
    print(f"生成JSON文件失败！错误原因：{str(e)}")
    exit(1)
