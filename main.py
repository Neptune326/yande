import atexit
import os
import random
import threading
import time

import bs4
import requests
from requests import Timeout

from agent_pool import AgentPool
from clash_proxy import switch_proxy
from download_task import DownloadTaskThread
from mysql_tool import MySqlTool
from yande_logger import YandeLogger

# 循环次数
YANDE_RUN_CIRCULATE_COUNT = 3
# 每次循环时间
YANDE_RUNT_TIME_MINUTE = 60
# 起始分页
YANDE_PAGE = 0
# 评分
YANDE_SCORE = 100
# 页面爬取错误次数
YANDE_PAGE_FAIL_COUNT = 0
# 下载失败最大次数
YANDE_IMG_FAIL_MAX = 3
# 文件下载路径
YANDE_FILE_PATH = 'D:\\files\\yande\\'
MYSQL = MySqlTool(host='localhost', user='root', password='admin', database='neptune')
config_data = MYSQL.query('select page, score from yande_config')
if config_data:
    YANDE_PAGE = int(config_data[0][0])
    YANDE_SCORE = int(config_data[0][1])

YANDE_LOGGER = YandeLogger(file_path='D:\\files\\logs\\yande')
YANDE_AGENT_POOL = AgentPool()
DOWNLOAD_INFO_LIST = []

# 锁
YANDE_PROXY_LOCK = threading.Lock()


def main():
    global YANDE_RUN_CIRCULATE_COUNT
    for i in range(YANDE_RUN_CIRCULATE_COUNT):
        YANDE_LOGGER.log('info', f'第{i + 1}次循环开始')
        start_crawler()
        YANDE_LOGGER.log('info', f'第{i + 1}次循环结束')
        time.sleep(10)


# 开始爬虫
def start_crawler():
    global YANDE_PAGE
    start_time_stamp = time.time()
    try:
        while True:
            crawler_page()
            YANDE_PAGE += 1

            run_time_stamp = time.time()
            if run_time_stamp - start_time_stamp >= YANDE_RUNT_TIME_MINUTE * 60:
                stop()
                return

            time.sleep(random.randint(2, 5))
    except Exception as e:
        save_config_db_data()
        YANDE_LOGGER.log('error', f'发生异常: {e}')
        switch_clash_proxy()
        time.sleep(random.randint(20 * YANDE_PAGE_FAIL_COUNT, 30 * YANDE_PAGE_FAIL_COUNT))


# 分页爬取
def crawler_page():
    global YANDE_PAGE_FAIL_COUNT, YANDE_PAGE
    url = f'https://yande.re/post.xml?limit=100&page={YANDE_PAGE}'
    header = {
        'User-Agent': YANDE_AGENT_POOL.get()
    }
    with requests.get(url=url, headers=header, timeout=5) as response:
        if not response.ok:
            MYSQL.execute('update yande_config set page = %s where id = 1', YANDE_PAGE)

            switch_clash_proxy()

            YANDE_PAGE_FAIL_COUNT += 1
            if YANDE_PAGE_FAIL_COUNT > 5:
                YANDE_LOGGER.log('error', f'连续访问失败超过5次，当前页面：{YANDE_PAGE}')
                raise Exception(f'当前页面：{YANDE_PAGE} ,访问失败')
            else:
                YANDE_PAGE -= 1
                return
        soup = bs4.BeautifulSoup(response.text, 'xml')
        dom = soup.select('post')
        for item in dom:
            id = int(item['id'])
            YANDE_LOGGER.log('info', f'page:{YANDE_PAGE} id:{id} score:{item["score"]} rating:{item["rating"]}')
            if int(item['score']) < YANDE_SCORE:
                continue

            rating = item['rating']
            tags = item['tags']
            file_url = item['file_url']
            file_ext = item['file_ext']
            YANDE_LOGGER.log('info',
                             f'page:{YANDE_PAGE} id:{id} score:{item["score"]} rating:{item["rating"]} tags:{item["tags"]} file_url:{item["file_url"]} file_ext:{item["file_ext"]}')
            en_tag = '|'.join(tags.split(' '))
            name = f'{id}.{file_ext}'

            dir_name = len(item['id']) < 4 and 'default' or item['id'][:len(item['id']) - 4]
            dir_name = os.path.join(YANDE_FILE_PATH, rating == 's' and 'Safe' or 'Question', dir_name)
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            path = os.path.join(dir_name, name)

            data_exist_result = exist_db_data(id)
            file_exist_result = os.path.exists(path)

            if data_exist_result and file_exist_result:
                if data_exist_result:
                    YANDE_LOGGER.log('info', f'IMAGE-id:{id}已存在[数据]')
                if file_exist_result:
                    YANDE_LOGGER.log('info', f'IMAGE-id:{id}已存在[文件]')
                continue

            DOWNLOAD_INFO_LIST.append({
                'id': id,
                'name': name,
                'ext': file_ext,
                'path': path,
                'tags': en_tag,
                'file_url': file_url
            })

            if len(DOWNLOAD_INFO_LIST) >= 8:
                download_result = threading_download_image()
                if not download_result:
                    MYSQL.execute('update yande_config set page = %s where id = 1', YANDE_PAGE)
                    YANDE_LOGGER.log('error', f'threading_download_image failed')
                    raise Exception('threading_download_image failed')
                else:
                    DOWNLOAD_INFO_LIST.clear()
                    time.sleep(random.randint(2, 3))


# 多线程下载
def threading_download_image():
    total_result = True
    thread_pool = []
    for info in DOWNLOAD_INFO_LIST:
        thread = DownloadTaskThread(download_img, args=(info['file_url'], info['path'], YANDE_AGENT_POOL.get()))
        thread_pool.append(thread)
        thread.start()

    for index, thread in enumerate(thread_pool):
        info = DOWNLOAD_INFO_LIST[index]
        thread.join()
        YANDE_LOGGER.log('info', f'download {info["id"]} {info["name"]},result {thread.get_result()}')
        if not thread.get_result():
            total_result = False
            MYSQL.execute(
                'insert into yande_download_error(yande_id,name,ext,en_tag,file_url) values (%s,%s,%s,%s,%s)',
                (info['id'], info['name'], info['ext'], info['tags'], info['file_url'])
            )
        else:
            MYSQL.execute(
                'insert into yande_img(yande_id,name,ext,en_tag) values (%s,%s,%s,%s)',
                (info['id'], info['name'], info['ext'], info['tags'])
            )

    return total_result


# 下载
def download_img(file_url: str, path: str, user_agent: str):
    download_fail_count = 0
    while download_fail_count < YANDE_IMG_FAIL_MAX:
        try:
            response = requests.get(
                url=file_url,
                headers={'User-Agent': user_agent},
                timeout=10
            )
            if not response.ok:
                download_fail_count += 1
                switch_clash_proxy()
                time.sleep(random.randint(20 * download_fail_count, 30 * download_fail_count))
                continue
            with open(path, 'wb') as f:
                f.write(response.content)
                return True
        except Timeout as e:
            YANDE_LOGGER.log('error', f'下载图片超时异常：{e}')
            download_fail_count += 1
            switch_clash_proxy()
        except Exception as e:
            YANDE_LOGGER.log('error', f'下载图片异常：{e}')
            download_fail_count += 1
            switch_clash_proxy()
    return False


# 判断数据是否已存在
def exist_db_data(yande_id: int):
    db_data = MYSQL.query('select count(1) as num from yande_img where yande_id = %s', yande_id)
    if db_data[0][0] is not None:
        return db_data[0][0] > 0
    return False


# 切换clash节点
def switch_clash_proxy():
    with YANDE_PROXY_LOCK:
        switch_result = switch_proxy()
        if switch_result:
            YANDE_LOGGER.log('info', '切换代理节点成功')
        else:
            YANDE_LOGGER.log('error', '切换代理节点失败')
            raise Exception('切换代理节点失败')


# 停止
def stop():
    YANDE_LOGGER.log('info', f'程序结束前是否有需要下载的图片:{len(DOWNLOAD_INFO_LIST) > 0}')
    if len(DOWNLOAD_INFO_LIST) > 0:
        threading_download_image()
    save_config_db_data()
    YANDE_LOGGER.log('info', '程序结束')
    # sys.exit(0)


# 保存数据库配置数据
def save_config_db_data():
    MYSQL.execute('update yande_config set page = %s where id = 1', YANDE_PAGE)
    YANDE_LOGGER.log('info', f'保存当前页数{YANDE_PAGE}')


if __name__ == '__main__':
    atexit.register(save_config_db_data)
    # threading.Timer(60 * 120, stop).start()
    main()
