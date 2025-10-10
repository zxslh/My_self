import re
import os
f_771 = ''
f_crv = ''
with open('index.html', 'r', encoding='utf-8') as read_file:
    for line in read_file:
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
