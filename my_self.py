import requests
import json
import re
import os
import random

def get_ips(token=''):
    global unique_ips
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
            print(f"❌ 失败: {e}")
            continue
        if ip_matches:
            if not token:
                unique_ips.update(ip_matches)
                continue
            try:
                ipv4 = ip_matches[0]
                update_url = f"http://dynv6.com/api/update?token={token}&hostname={list['domain']}&ipv4={ipv4}"
                response = requests.get(update_url, timeout=10).text.strip()
                if any(keyword in response for keyword in ["good", "Ok", "nochg", "updated", "unchanged"]):
                    print(f"✅ {list['domain']}：{response}")
                    unique_ips.update(ip_matches[1:])
                else:
                    raise
            except Exception as e:
                unique_ips.update(ip_matches)
                print(f"❌ {list['domain']}: {e}")
            finally:
                bulid_vless_urls(list['domain'].split(".", 1)[0], list['domain'].split(".", 1)[1], 'cfv.live-zxs.dns.army', 'LIVE_CFV_TOKEN')
        else:
            print(f"❌ {list['url']}未返回IP")
            
def update_A(host, domain=''):
    act = 'post'

    if host == 'dynv6':
        api_token = os.getenv('DYNV6_TOKEN')
        base_url = 'https://dynv6.com/api/v2/zones'
        headers = {
           "Authorization": f"Bearer {api_token}",
           "Content-Type": "application/json"
        }
        r_record = 'records'
        r_limit = 41  # 节点数量30（41-11）
        r_name = 'name'
        r_type = 'type'
        r_data = 'data'
        r_worker = '771.qq-zxs.dns.army'
        r_token = 'QQ_771_TOKEN'
    elif host == 'dynu':
        api_token = os.getenv('DYNU_TOKEN')
        base_url = 'https://api.dynu.com/v2/dns'
        headers = {
            "accept": "application/json",
            "API-Key": api_token
        }
        r_record = 'record'
        r_limit = 15  # 节点数量4（15-11）
        r_name = 'nodeName'
        r_type = 'recordType'
        r_data = 'ipv4Address'
        r_worker = 'cfv.live-zxs.dns.army'
        r_token = 'LIVE_CFV_TOKEN'
    else:
        return

    try:
        response = requests.get(base_url, headers=headers)
        response.raise_for_status()
        all_domains = response.json()
        if isinstance(all_domains, dict): all_domains = all_domains['domains']
    except Exception as e:
        print(f'❌ 获取区域信息失败：{str(e)}')
        return

    for domain_data in all_domains:
        if domain and domain != domain_data['name']: continue
        zoneID = domain_data['id']
        name = domain_data['name']  # 和参数domain冲突，改名name
        sub_name = 11
        url = f"{base_url}/{zoneID}/{r_record}"
        act_url = url
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            all_records = response.json()
            if isinstance(all_records, dict): all_records = all_records['dnsRecords']
        except Exception as e:
            print(f"❌ {name} 获取domain记录信息失败：{str(e)}")
            return

        while sub_name < r_limit:
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
                print(f"✅ 成功：{sub_name}.{name} → {current_ip}")
            except Exception as e:
                print(f"❌ {sub_name}.{name} 操作失败：{str(e)}")
            finally:
                sub_name += 1
                bulid_vless_urls(str(sub_name), name, r_worker, r_token)

def bulid_vless_urls(a, b, c, d):
    global vless_urls
    global vless_urls_771
    global vless_urls_crv
    ports = ['443','2053','2083','2087','2096','8443']
    port = random.choice(ports)
    port = 443  # 固定端口，随机端口请注销此项
    uuid = os.getenv(d)
    if not uuid: return
    vless_url = f"vless://{uuid}@{a}.{b}:{port}?path=%2F%3Fed%3D2560&security=tls&encryption=none&host={c}&type=ws&sni={c}#{c[0:3]}-{b[0]}-{a}"
    vless_urls += f'{vless_url}\n'
    if c == '771.qq':
        vless_urls_771 += f'{vless_url}\n'
    if c == 'cfv.live':
        vless_urls_crv += f'{vless_url}\n'
            
if __name__ == "__main__":
    vless_urls = ''
    vless_urls_771 = ''
    vless_urls_crv = ''
    unique_ips = set()

    get_ips(os.getenv('DYNV6_TOKEN'))

    if unique_ips:
        update_A('dynv6', 'cf-zxs.dns.army')
        update_A('dynu')

    if vless_urls:
        with open('docs/index.html', 'w', encoding='utf-8') as file:
            file.write(vless_urls)
            print(f'✅ 写入index成功！')
            
    if vless_urls_771:
        with open('docs/f_771', 'w', encoding='utf-8') as file:
            file.write(vless_urls_771)
            print(f'✅ 写入f_771成功！')
            
    if vless_urls_crv:
        with open('docs/f_crv', 'w', encoding='utf-8') as file:
            file.write(vless_urls_crv)
            print(f'✅ 写入f_crv成功！')

