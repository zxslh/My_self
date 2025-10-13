import requests
import json
import re
import os
import random

def get_ips():
    global unique_ips
    update_list = [
        'https://ip.164746.xyz',
        'https://ipdb.api.030101.xyz/?type=bestcf&country=true',
        'https://ip.164746.xyz/ipTop10.html',
        'https://www.wetest.vip/page/cloudflare/total_v4.html',
        'https://addressesapi.090227.xyz/CloudFlareYes',
        'https://vps789.com/openApi/cfIpApi',
        'https://vps789.com/openApi/cfIpTop20',
        'https://raw.githubusercontent.com/NiREvil/vless/refs/heads/main/sub/Cf-ipv4.json',
    ]
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

    for list in update_list:
        ip_matches = ''
        try:
            response = requests.get(list['url'], timeout=10).text
            ip_matches = re.findall(ip_pattern, response, re.IGNORECASE)
            unique_ips.update(ip_matches)
        except Exception as e:
            print(f"❌ 失败: {str(e)}")

def update_A(host, host_domain, host_token, worker, worker_token):

    act = 'post'
    global node_num

    if host == 'dynv6':
        base_url = 'https://dynv6.com/api/v2/zones'
        headers = {
           "Authorization": f"Bearer {host_token}",
           "Content-Type": "application/json"
        }
        r_record = 'records'
        r_name = 'name'
        r_type = 'type'
        r_data = 'data'
    elif host == 'dynu':
        base_url = 'https://api.dynu.com/v2/dns'
        headers = {
            "accept": "application/json",
            "API-Key": host_token
        }
        r_record = 'record'
        r_name = 'nodeName'
        r_type = 'recordType'
        r_data = 'ipv4Address'
    else:
        return

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        all_domains = response.json()
        if isinstance(all_domains, dict): all_domains = all_domains['domains']
    except Exception as e:
        print(f'❌ 获取所有domain信息失败：{str(e)}')
        return

    for domain_data in all_domains:
        if host_domain and host_domain != domain_data['name']: continue
        zoneID = domain_data['id']
        domain = domain_data['name']
        sub_name = 1
        url = f"{base_url}/{zoneID}/{r_record}"
        act_url = url
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            all_records = response.json()
            if isinstance(all_records, dict): all_records = all_records['dnsRecords']
        except Exception as e:
            print(f"❌ {domain} 获取domain记录信息失败：{str(e)}")
            continue
        while int(node_num) > 0:
            current_ip = unique_ips.pop()
            if not current_ip: return

            record_data = {
                r_name: f'{sub_name:02d}',
                r_type: "A",
                r_data: current_ip,
                "ttl": 3600,
                "state": True
            }

            try:
                for record in all_records:
                    if record[r_name] == f'{sub_name:02d}' and record[r_type] == "A":
                        act_url = f"{url}/{record['id']}"
                        if host == 'dynv6': act = 'patch'
                        break
                update_response = getattr(requests, act)(act_url, headers=headers, data=json.dumps(record_data))
                update_response.raise_for_status()
                print(f"✅ 成功：{sub_name:02d}.{domain} → {current_ip}")
                bulid_vless_urls(f'{sub_name:02d}', domain, worker, worker_token)
                sub_name += 1
                node_num -= 1
            except Exception as e:
                if "501 S" not in str(e) and "401 E" not in str(e): 
                    print(f"❌ {sub_name:02d}.{domain} 操作失败：{str(e)}")
                break
                
def bulid_vless_urls(a, b, c, d):
 #   if True: return  # 需要生成文件注销此行
    global vless_urls
    global vless_urls_qq
    global vless_urls_live
    ports = ['443','2053','2083','2087','2096','8443']
    port = random.choice(ports)
    port = 443  # 固定端口，随机端口请注销此项
    vless_url = f"vless://{d}@{a}.{b}:{port}?path=%2F%3Fed%3D2560&security=tls&encryption=none&host={c}&type=ws&sni={c}#{c[0:3]}-{b[0]}-{a}"
    vless_urls += f'{vless_url}\n'
    if c == QQ_HOST:
        vless_urls_qq += f'{vless_url}\n'
    if c == LIVE_HOST:
        vless_urls_live += f'{vless_url}\n'
            
if __name__ == "__main__":
    vless_urls = ''
    vless_urls_qq = ''
    vless_urls_live = ''
    unique_ips = set()
    DYNV6_TOKEN = os.getenv('DYNV6_TOKEN')
    DYNU_TOKEN = os.getenv('DYNU_TOKEN')
    QQ_TOKEN = os.getenv('QQ_771_TOKEN')
    QQ_HOST = '771.qq-zxs.dns.army'
    LIVE_TOKEN = ''
    LIVE_HOST = ''
    DYNV6_domain = 'cf-zxs.dns.army'
    DYNU_domain = ''

    node_num = 50
    get_ips()

    if unique_ips:
       # update_A('dynu', DYNU_domain, DYNU_TOKEN, LIVE_HOST, LIVE_TOKEN)  # 因DYNU有限制，先执行，剩余使用DYNV6
        update_A('dynv6', DYNV6_domain, DYNV6_TOKEN, QQ_HOST, QQ_TOKEN)

    if vless_urls:
        with open('docs/index.html', 'w', encoding='utf-8') as file:
            file.write(vless_urls)
            print(f'✅ 写入index成功！')
        with open('docs/index5', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:5]))
            print(f'✅ 写入index5成功！')
        with open('docs/index10', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:10]))
            print(f'✅ 写入index10成功！')
        with open('docs/index15', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:15]))
            print(f'✅ 写入index15成功！')
        with open('docs/index20', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:20]))
            print(f'✅ 写入index20成功！')
        with open('docs/index25', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:25]))
            print(f'✅ 写入index25成功！')
        with open('docs/index30', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:30]))
            print(f'✅ 写入index30成功！')
        with open('docs/index35', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:35]))
            print(f'✅ 写入index35成功！')
        with open('docs/index40', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:40]))
            print(f'✅ 写入index40成功！')
        with open('docs/index45', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:45]))
            print(f'✅ 写入index45成功！')
        with open('docs/index50', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:50]))
            print(f'✅ 写入index50成功！')

