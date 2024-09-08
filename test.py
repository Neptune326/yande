import random
import re

import requests

# s = 'aaa bbb'
# # print(s.split(' '))
# # # 正则替换
# # print(re.sub('\s', '_', s))
# # print(s.replace('\s', '_'))
# s = '1189483'
# print(s[:len(s) - 4])

with requests.get(url='https://yande.re/post.xml?page=99', headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}, verify=False,
                  proxies={
                      'http': 'http://p.webshare.io',
                      'https': 'http://p.webshare.io'
                  }
                  ) as response:
    print(response.text)
