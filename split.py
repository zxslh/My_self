import re
import os
f_771 = ''
f_crv = ''
ip_info = {}
ip_group = []
with open('goodips', 'r', encoding='utf-8') as read_file:
    for line in read_file:
        pattern = r'^(?P<ip>\d+\.\d+\.\d+\.\d+)(:(?P<port>\d+))?(#(?P<name>.+))?$'
        match = re.match(pattern, s)
        if match:
            ip = match.group('ip')       # 提取IP地址
            port = match.group('port')   # 提取端口（不存在时为None）
            name = match.group('name')   # 提取名称（不存在时为None）
            ip_info = {'IP': ip, '端口': port, '名称': 'name'}
            ip_group.append(ip_info)
            
        
        if '771' in line:
            f_771 += f'{line}\n'  # 新行追加到末尾，保持原顺序
        if 'crv' in line:
            f_crv += f'{line}\n'

# 用rstrip移除末尾空行，写入更整洁
with open('f_crv', 'w', encoding='utf-8') as fcrv:
    fcrv.write(f_crv.rstrip('\n'))
with open('f_771', 'w', encoding='utf-8') as f771:
    f771.write(f_771.rstrip('\n'))
       
    print(f'✅ 写入成功！')
