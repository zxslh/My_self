import re
import json

def extract_ip_port_name(s):
    """彻底修复括号问题，兼容IPv4/IPv6，简化正则结构"""
    # 简化正则：移除IPv6模式中所有冗余括号，仅保留必要分组
    pattern = r'^(?P<ip>(?:\[[0-9a-fA-F:]+\]|[0-9a-fA-F:]+|\d+\.\d+\.\d+\.\d+))(:(?P<port>\d+))?(#(?P<name>.+))?$'
    # 不再使用re.VERBOSE，避免换行缩进干扰括号解析
    match = re.match(pattern, s.strip(), re.IGNORECASE)
    if not match:
        return None, None, None
    ip = match.group('ip')
    # 移除IPv6可能的[]
    ip = ip[1:-1] if ip and ip.startswith('[') and ip.endswith(']') else ip
    return ip, match.group('port'), match.group('name')

    
# 1. 读取文件并解析
ip_list = []
try:
    with open('goodips', 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:  # 跳过空行
                continue
            ip, port, name = extract_ip_port_name(line)
            if ip:  # 仅保留解析成功的条目
                ip_list.append({
                    "ip": ip,
                    "port": port,  # 无端口时为None
                    "name": name   # 无名称时为None
                })
            else:
                print(f"警告：第{line_num}行格式无效，已跳过 → {line}")
except FileNotFoundError:
    print("错误：未找到'goodip'文件，请确认文件路径正确")
    exit()

# 2. 保存为JSON文件
with open('ip_info.json', 'w', encoding='utf-8') as f:
    # indent=2 用于格式化JSON，增强可读性；ensure_ascii=False 支持中文名称
    json.dump(ip_list, f, indent=2, ensure_ascii=False)

print(f"处理完成！共解析{len(ip_list)}条有效数据，已保存至'ip_info.json'")
