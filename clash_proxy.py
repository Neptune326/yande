import json
import random

import requests

'''
测试延迟：http://127.0.0.1:9097/proxies/代理节点的名称/delay?url=http://www.gstatic.com/generate_204&timeout=5000
'''

# 定义 Clash API 的基本信息
CLASH_API_URL = 'http://127.0.0.1:9097'
CLASH_API_SWITCH = f'{CLASH_API_URL}/proxies/GLOBAL'
CLASH_API_PROXIES = f'{CLASH_API_URL}/proxies'

CLASH_API_HEADERS = {'Authorization': 'Bearer ', 'Content-Type': 'application/json'}

CLASH_PROXIES_LIST = [
    "HongKong-IPLC-HK-BETA1-Rate:1.0",
    "HongKong-IPLC-HK-BETA2-Rate:1.0",
    "HongKong-IPLC-HK-BETA3-Rate:1.0",
    "HongKong-IPLC-HK-BETA4-Rate:1.0",
    "HongKong-IPLC-HK-BETA5-Rate:1.0",
    "HongKong-HK-1-Rate:0.5",
    "HongKong-HK-2-Rate:0.5",
    "Japan-OS-1-Rate:1.0",
    "Japan-OS-2-Rate:1.0",
    "Japan-OS-3-Rate:1.0",
    "Taiwan-TW-1-Rate:1.0",
    "Taiwan-TW-2-Rate:1.0"
]


# 获取节点数据
def get_proxies():
    response = requests.get(
        url=CLASH_API_PROXIES,
        headers=CLASH_API_HEADERS
    )
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('Failed to fetch proxies')


# 切换节点
def switch_proxy():
    proxy_name = random.choice(CLASH_PROXIES_LIST)
    response = requests.put(
        url=CLASH_API_SWITCH,
        headers=CLASH_API_HEADERS,
        data=json.dumps({"name": proxy_name})
    )
    if response.status_code == 204:
        print(f'Successfully switched to {proxy_name}')
        return True
    else:
        print(f'Failed to switch to {proxy_name}')
        return False

# if __name__ == "__main__":
#     proxies = get_proxies()
#     print('Available proxies:', proxies)
#
#     switch_proxy()
