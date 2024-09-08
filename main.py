import atexit
import json
import os
import random
import sys
import threading
import time

import bs4
import requests
from requests import Timeout, HTTPError, RequestException
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from AgentTool import AgentTool
from MySqlTool import MySqlTool
from RedisTool import RedisTool

# print("Hello, World!")
# download(
#     url='https://yande.re/post',
#     path='D:\\files\\test\\test.txt'
# )
#
page = 0
GLOBAL_PATH = 'D:\\files\\yande\\'


def main():
    print("hello world")

    mysql = MySqlTool(host='localhost', user='root', password='admin', database='neptune')

    config_data = mysql.query('select page, score from yande_config')
    global page
    page = int(config_data[0][0])
    score = int(config_data[0][1])

    max_data = mysql.query('select max(yande_id),min(yande_id) from yande_img')
    max_id = 0
    min_id = 0
    if max_data[0][0] is not None:
        max_id = int(max_data[0][0])

    if max_data[0][1] is not None:
        min_id = int(max_data[0][1])

    redis = RedisTool(host='localhost', port=6379, db=5)
    tag_data = mysql.query('select en, cn from yande_tag')
    for tag in tag_data:
        redis.set(tag[0], tag[1])

    with open('agentPool.json', 'r', encoding='utf-8') as agent_file:
        pool = json.load(agent_file)

    try:
        while True:
            # 休眠
            time.sleep(random.randint(2, 5))
            crawler(page, score, max_id, min_id, mysql, redis, pool)
            page += 1
    except Exception as e:
        mysql.execute('update yande_config set page = %s where id = 1', (page))
        print(e)


def crawler(page: int, score: int, max_id: int, min_id: int, mysql: MySqlTool, redis: RedisTool, proxy_pool: dict):
    agent_pool = AgentTool()

    url = f'https://yande.re/post.xml?page={page}'
    header = {
        'User-Agent': agent_pool.get()
    }
    with requests.get(
            url=url,
            headers=header,
            proxies={
                'http': proxy_pool[random.randint(0, len(proxy_pool) - 1)]
            }
    ) as response:
        if not response.ok:
            mysql.execute('update yande_config set page = %s where id = 1', (page))
            raise Exception(f'当前页面：{page} ,访问失败')
        soup = bs4.BeautifulSoup(response.text, 'xml')
        dom = soup.select('post')
        for item in dom:
            id = int(item['id'])
            print('page:', page, 'max_id:', max_id, 'id:', id, 'score:', item['score'])
            if min_id <= id <= max_id:
                continue
            if int(item['score']) < score:
                continue

            rating = item['rating']
            tags = item['tags']
            file_url = item['file_url']
            file_ext = item['file_ext']
            print(rating, id, tags, file_url, file_ext, int(item['score']))
            en_tag = '|'.join(tags.split(' '))
            name = f'{id}.{file_ext}'
            dir_name = len(item['id']) < 4 and 'open' or item['id'][:len(item['id']) - 4]
            if rating == 's':
                dir_name = f'{GLOBAL_PATH}\\Safe\\{dir_name}'
            else:
                dir_name = f'{GLOBAL_PATH}\\Question\\{dir_name}'
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            path = f'{dir_name}\\{name}'
            print(rating, id, path)

            try:
                download(
                    file_url,
                    path,
                    proxies={
                        'http': proxy_pool[random.randint(0, len(proxy_pool) - 1)]
                    }
                )
                mysql.execute('insert into yande_img(yande_id,name,ext,en_tag) values (%s,%s,%s,%s)',
                              (id, name, file_ext, en_tag))
                time.sleep(random.randint(2, 5))
            except Exception as e:
                mysql.execute(
                    'insert into yande_download_error(yande_id,name,ext,en_tag,file_url) values (%s,%s,%s,%s,%s)',
                    (id, name, file_ext, en_tag, file_url))
                print(e)


def download(url: str, path: str, proxies=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'
    }
    session = requests.Session()

    # 设置重试机制
    retry_strategy = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    if proxies:
        session.proxies.update(proxies)

    session.headers.update(headers)

    response = session.get(url, timeout=5, stream=True)
    response.raise_for_status()  # 确保HTTP请求返回200状态码

    # 写入文件
    with open(path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    print(f"文件已成功下载到: {path}")


def stop():
    print("关闭程序")
    other = MySqlTool(host='localhost', user='root', password='admin', database='neptune')
    other.execute('update yande_config set page = %s where id = 1', (page))
    sys.exit(0)


def save_data():
    other = MySqlTool(host='localhost', user='root', password='admin', database='neptune')
    other.execute('update yande_config set page = %s where id = 1', (page))


if __name__ == '__main__':
    atexit.register(save_data)
    threading.Timer(60 * 10, stop).start()
    main()
