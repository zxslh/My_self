def extract_ip_core(full_ip: str) -> str:
    """从完整格式（如4.4.4.4:4#iii）中提取核心IP地址（4.4.4.4）"""
    # 按":"分割，取第一部分即为IP（忽略后续端口和后缀）
    return full_ip.split(':')[0].strip()

# 1. 读取bad_ips（仅含IP，如4.4.4.4）
with open('bad_ips', 'r', encoding='utf-8') as f:
    bad_ips = set(line.strip() for line in f if line.strip())  # 存储纯IP集合

# 2. 读取good_ips（完整格式），并记录"完整条目→核心IP"的映射
good_ip_mapping = {}
with open('good_ips', 'r', encoding='utf-8') as f:
    for line in f:
        full_ip = line.strip()
        if not full_ip:
            continue
        ip_core = extract_ip_core(full_ip)
        good_ip_mapping[full_ip] = ip_core  # 键：完整条目，值：核心IP

# 3. 过滤：保留核心IP不在bad_ips中的完整条目
filtered_ips = [full_ip for full_ip, ip_core in good_ip_mapping.items() if ip_core not in bad_ips]

# 4. 写回结果（按原格式保留，可选排序）
with open('good_ips', 'w', encoding='utf-8') as f:
    for ip in sorted(filtered_ips):
        f.write(ip + '\n')

# 输出统计信息
original_count = len(good_ip_mapping)
removed_count = original_count - len(filtered_ips)
print(f"处理完成！原{original_count}个IP，移除{removed_count}个匹配条目，剩余{len(filtered_ips)}个有效IP。")
