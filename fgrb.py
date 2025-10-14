# 1. 读取文件，按完整格式（含端口和后缀）去重
with open('bad_ips', 'r', encoding='utf-8') as f:
    # 过滤空行，strip()仅去除首尾空白（保留格式中的:和#）
    bad_ips = set(line.strip() for line in f if line.strip())

with open('good_ips', 'r', encoding='utf-8') as f:
    good_ips = set(line.strip() for line in f if line.strip())

# 2. 计算差集：保留在good_ips中但不在bad_ips中的完整IP条目
filtered_ips = good_ips - bad_ips

# 3. 写回结果（按原格式保留，可选排序）
with open('good_ips', 'w', encoding='utf-8') as f:
    for ip in sorted(filtered_ips):  # sorted()可选，按字符顺序排列
        f.write(ip + '\n')

# 输出处理信息
removed_count = len(good_ips) - len(filtered_ips)
print(f"处理完成！原{len(good_ips)}个IP，移除{removed_count}个匹配条目，剩余{len(filtered_ips)}个有效IP。")
