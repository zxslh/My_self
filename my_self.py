import requests
import json
import re
import os
import random

def get_ips(worker='', worker_token=''):
    global unique_ips
    global node_num
    update_list = [
        {'domain': 'cf-zxs.dynv6.net', 'url': 'https://ip.164746.xyz'},
        {'domain': 'cf-zxs.v6.army', 'url': 'https://ipdb.api.030101.xyz/?type=bestcf&country=true'},
        {'domain': 'cf-zxs.dns.army', 'url': 'https://ip.164746.xyz/ipTop10.html'},
        {'domain': 'cf-zxs.dns.navy', 'url': 'https://www.wetest.vip/page/cloudflare/total_v4.html'},
        {'domain': 'cf-zxs.v6.navy', 'url': 'https://api.uouin.com/cloudflare.html'},
        {'domain': 'ljk-clouflare.dns.army', 'url': 'https://addressesapi.090227.xyz/CloudFlareYes'},
        {'domain': 'live-zxs.dns.army', 'url': 'https://vps789.com/openApi/cfIpApi'}
    ]
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'

    for list in update_list:
        try:
            response = requests.get(list['url'], timeout=10).text
            ip_matches = re.findall(ip_pattern, response, re.IGNORECASE)
        except Exception as e:
            print(f"❌ 失败: {str(e)}")
            continue
        if ip_matches:
            if not worker:
                unique_ips.update(ip_matches)
                continue
            try:
                ipv4 = ip_matches[0]
                update_url = f"http://dynv6.com/api/update?token={DYNV6_TOKEN}&hostname={list['domain']}&ipv4={ipv4}"
                response = requests.get(update_url, timeout=10).text.strip()
                if any(keyword in response for keyword in ["good", "Ok", "nochg", "updated", "unchanged"]):
                    print(f"✅ {list['domain']}：{response}")
                    unique_ips.update(ip_matches[1:])
                else:
                    raise Exception({response})
            except Exception as e:
                unique_ips.update(ip_matches)
                print(f"❌ {list['domain']}: {str(e)}")
            finally:
                node_num -= 1
                bulid_vless_urls(list['domain'].split(".", 1)[0], list['domain'].split(".", 1)[1], worker, worker_token)
        else:
            print(f"❌ {list['url']}未返回IP")
            
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
        sub_name = 11
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
                r_name: str(sub_name),
                r_type: "A",
                r_data: current_ip,
                "ttl": 3600,
            }

            try:
                for record in all_records:
                    if record[r_name] == str(sub_name) and record[r_type] == "A":
                        act_url = f"{url}/{record['id']}"
                        if host == 'dynv6': act = 'patch'
                        break
                update_response = getattr(requests, act)(act_url, headers=headers, data=json.dumps(record_data))
                update_response.raise_for_status()
                print(f"✅ 成功：{sub_name}.{domain} → {current_ip}")
                sub_name += 1
            except Exception as e:
                if "501 S" in str(e) or "401 E" in str(e): break
                print(f"❌ {sub_name}.{domain} 操作失败：{str(e)}")
            finally:
                node_num -= 1
                bulid_vless_urls(str(sub_name), domain, worker, worker_token)

def bulid_vless_urls(a, b, c, d):
    global vless_urls
    global vless_urls_771
    global vless_urls_crv
    ports = ['443','2053','2083','2087','2096','8443']
    port = random.choice(ports)
    port = 443  # 固定端口，随机端口请注销此项
    vless_url = f"vless://{d}@{a}.{b}:{port}?path=%2F%3Fed%3D2560&security=tls&encryption=none&host={c}&type=ws&sni={c}#{c[0:3]}-{b[0]}-{a}"
    vless_urls += f'{vless_url}\n'
    if c == '771.qq-zxs.dns.army':
        vless_urls_771 += f'{vless_url}\n'
    if c == 'crv.live-zxs.dns.army':
        vless_urls_crv += f'{vless_url}\n'
            
if __name__ == "__main__":
    vless_urls = ''
    vless_urls_771 = ''
    vless_urls_crv = ''
    unique_ips = set()
    DYNV6_TOKEN = os.getenv('DYNV6_TOKEN')
    DYNU_TOKEN = os.getenv('DYNU_TOKEN')
    QQ_771_TOKEN = os.getenv('QQ_771_TOKEN')
    QQ_771_HOST = '771.qq-zxs.dns.army'
    LIVE_CFV_TOKEN = os.getenv('LIVE_CFV_TOKEN')
    LIVE_CFV_HOST = 'cfv.live-zxs.dns.army'
    node_num = 65  # 改变节点数量后需注消exit（）运行一次
    
    get_ips('771.qq-zxs.dns.army', QQ_771_TOKEN)
 #   get_ips()

    if unique_ips:
        update_A('dynu', '', DYNU_TOKEN, LIVE_CFV_HOST, LIVE_CFV_TOKEN)  # 因DYNU有限制，先执行，剩余使用DYNV6
        update_A('dynv6', 'cf-zxs.dns.army', DYNV6_TOKEN, QQ_771_HOST, QQ_771_TOKEN)

    if vless_urls:
        with open('docs/index.html', 'w', encoding='utf-8') as file:
            file.write(vless_urls)
            print(f'✅ 写入index成功！')
       # exit()
        with open('docs/index_5', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:5]))
            print(f'✅ 写入index_5成功！')
        with open('docs/index_10', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:10]))
            print(f'✅ 写入index_10成功！')
        with open('docs/index_15', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:15]))
            print(f'✅ 写入index_15成功！')
        with open('docs/index_20', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:20]))
            print(f'✅ 写入index_20成功！')
        with open('docs/index_25', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:25]))
            print(f'✅ 写入index_25成功！')
        with open('docs/index_30', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:30]))
            print(f'✅ 写入index_30成功！')
        with open('docs/index_35', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:35]))
            print(f'✅ 写入index_35成功！')
        with open('docs/index_40', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:40]))
            print(f'✅ 写入index_40成功！')
        with open('docs/index_45', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:45]))
            print(f'✅ 写入index_45成功！')
        with open('docs/index_50', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:50]))
            print(f'✅ 写入index_50成功！')
        with open('docs/index_55', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:55]))
            print(f'✅ 写入index_55成功！')
        with open('docs/index_60', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls.split('\n')[:60]))
            print(f'✅ 写入index_60成功！')
            
    if vless_urls_771:
        with open('docs/f_771', 'w', encoding='utf-8') as file:
            file.write(vless_urls_771)
            print(f'✅ 写入f_771成功！')
        with open('docs/f_771_5', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls_771.split('\n')[:5]))
            print(f'✅ 写入f_771_5成功！')
        with open('docs/f_771_10', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls_771.split('\n')[:10]))
            print(f'✅ 写入f_771_10成功！')
        with open('docs/f_771_15', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls_771.split('\n')[:15]))
            print(f'✅ 写入f_771_15成功！')
        with open('docs/f_771_20', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls_771.split('\n')[:20]))
            print(f'✅ 写入f_771_20成功！')
        with open('docs/f_771_25', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls_771.split('\n')[:25]))
            print(f'✅ 写入f_771_25成功！')
        with open('docs/f_771_30', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls_771.split('\n')[:30]))
            print(f'✅ 写入f_771_30成功！')
            
    if vless_urls_crv:
        with open('docs/f_crv', 'w', encoding='utf-8') as file:
            file.write(vless_urls_crv)
            print(f'✅ 写入f_crv成功！')
        with open('docs/f_crv_5', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls_crv.split('\n')[:5]))
            print(f'✅ 写入f_crv_5成功！')
        with open('docs/f_crv_10', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls_crv.split('\n')[:10]))
            print(f'✅ 写入f_crv_10成功！')
        with open('docs/f_crv_15', 'w', encoding='utf-8') as file:
            file.write('\n'.join(vless_urls_crv.split('\n')[:15]))
            print(f'✅ 写入f_crv_15成功！')

