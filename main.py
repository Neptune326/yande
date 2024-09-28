import atexit
import json
import os
import random
import re
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
YANDE_RUN_CIRCULATE_COUNT = 2
# 每次循环时间
YANDE_RUNT_TIME_MINUTE = 30
# 起始分页
YANDE_PAGE = 0
# 评分
YANDE_E_SCORE = 250
# 评分
YANDE_S_SCORE = 150
# 页面爬取错误次数
YANDE_PAGE_FAIL_COUNT = 0
# 下载失败最大次数
YANDE_IMG_FAIL_MAX = 3
# 下载失败总次数
YANDE_IMG_FAIL_TOTAL = 0
# 文件下载路径
YANDE_FILE_PATH = 'D:\\files\\yande\\'
MYSQL = MySqlTool(host='localhost', user='root', password='admin', database='neptune')
config_data = MYSQL.query('select page, score from yande_config')
if config_data:
    YANDE_PAGE = int(config_data[0][0])
    # YANDE_SCORE = int(config_data[0][1])

YANDE_LOGGER = YandeLogger(file_path='D:\\files\\logs\\yande')
YANDE_AGENT_POOL = AgentPool()
DOWNLOAD_INFO_LIST = []

# 锁
YANDE_PROXY_LOCK = threading.Lock()


def main():
    global YANDE_RUN_CIRCULATE_COUNT, YANDE_PAGE_FAIL_COUNT, YANDE_IMG_FAIL_TOTAL
    for i in range(YANDE_RUN_CIRCULATE_COUNT):
        YANDE_LOGGER.log('info', f'第{i + 1}次循环开始')
        start_crawler()
        YANDE_LOGGER.log('info', f'第{i + 1}次循环结束')
        time.sleep(10)

        YANDE_PAGE_FAIL_COUNT = 0
        YANDE_IMG_FAIL_TOTAL = 0


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
    global YANDE_PAGE_FAIL_COUNT, YANDE_PAGE, YANDE_IMG_FAIL_TOTAL
    url = f'https://yande.re/post.xml?limit=1000&page={YANDE_PAGE}'
    header = {
        'User-Agent': YANDE_AGENT_POOL.get()
    }
    with requests.get(url=url, headers=header, timeout=5) as response:
        if not response.ok:
            save_config_db_data()

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
            rating = item['rating']

            tags = item['tags']
            file_url = item['file_url']
            file_ext = item['file_ext']

            en_tag = '|'.join(tags.split(' '))
            name = f'{id}.{file_ext}'

            last_level_dir_name = len(item['id']) < 4 and '0' or item['id'][:len(item['id']) - 4]
            dir_name = os.path.join(
                YANDE_FILE_PATH,
                rating == 's' and 'Safe' or rating == 'e' and 'Explicit' or 'Questionable',
                last_level_dir_name
            )
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            path = os.path.join(dir_name, name)

            if rating == 's':
                if int(item['score']) < YANDE_S_SCORE:
                    continue
            else:
                if int(item['score']) < YANDE_E_SCORE:
                    if os.path.exists(path):
                        os.remove(path)
                    continue

            if os.path.exists(path):
                YANDE_LOGGER.log('info', f'IMAGE-id:{id}已存在[文件]')

                if not exist_db_data(id):
                    MYSQL.execute(
                        'insert into yande_img(yande_id,rating,name,ext,en_tag) values (%s,%s,%s,%s,%s)',
                        (id, rating, name, file_ext, en_tag)
                    )
                else:
                    MYSQL.execute(
                        'update yande_img set rating = %s, name = %s, ext = %s, en_tag = %s where yande_id = %s',
                        (rating, name, file_ext, en_tag, id)
                    )
                continue
            else:
                if rating != 's':
                    old_path = os.path.join(YANDE_FILE_PATH, 'Question', last_level_dir_name, name)
                    if os.path.exists(old_path):
                        YANDE_LOGGER.log('info', f'IMAGE-id:{id}已存在[文件]于旧目录中')
                        os.rename(old_path, path)
                        if not exist_db_data(id):
                            MYSQL.execute(
                                'insert into yande_img(yande_id,rating,name,ext,en_tag) values (%s,%s,%s,%s,%s)',
                                (id, rating, name, file_ext, en_tag)
                            )
                        else:
                            MYSQL.execute(
                                'update yande_img set rating = %s, name = %s, ext = %s, en_tag = %s where yande_id = %s',
                                (rating, name, file_ext, en_tag, id)
                            )
                        continue

            YANDE_LOGGER.log('info',
                             f'page:{YANDE_PAGE} id:{id} score:{item["score"]} rating:{item["rating"]} tags:{item["tags"]} file_url:{item["file_url"]} file_ext:{item["file_ext"]}')

            DOWNLOAD_INFO_LIST.append({
                'id': id,
                'name': name,
                'rating': rating,
                'ext': file_ext,
                'path': path,
                'tags': en_tag,
                'file_url': file_url
            })

            if len(DOWNLOAD_INFO_LIST) >= 8:
                download_result = threading_download_image()
                if not download_result:
                    YANDE_IMG_FAIL_TOTAL += 1
                    if YANDE_IMG_FAIL_TOTAL >= 5:
                        save_config_db_data()
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
        thread = DownloadTaskThread(download_img, args=(info['file_url'], info['path']))
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
                'insert into yande_img(yande_id,name,rating,ext,en_tag) values (%s,%s,%s,%s,%s)',
                (info['id'], info['name'], info['rating'], info['ext'], info['tags'])
            )

    return total_result


# 下载
def download_img(file_url: str, path: str):
    download_fail_count = 0
    while download_fail_count < YANDE_IMG_FAIL_MAX:
        try:
            response = requests.get(
                url=file_url,
                headers={'User-Agent': YANDE_AGENT_POOL.get()},
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
    global YANDE_PROXY_LOCK
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


@atexit.register
def save_before_close():
    save_config_db_data()


def download_error_image():
    error_data = MYSQL.query("select yande_id from yande_download_error")
    if not error_data:
        return
    for error_item in error_data:
        yande_id = error_item[0]
        try:
            response = requests.get(
                url=f'https://yande.re/post/show/{yande_id}',
                headers={'User-Agent': YANDE_AGENT_POOL.get()},
                timeout=5
            )
            if not response.ok:
                switch_clash_proxy()
                time.sleep(2)
                YANDE_LOGGER.log('error', '下载历史错误图片失败')
                continue
            html = response.text

            matches = re.findall(r"Post.register_resp\(.*\)", html)
            if len(matches) == 0:
                continue
            match = matches[0].replace("Post.register_resp(", "").replace(")", "")
            post_json = json.loads(match)
            if not post_json or not post_json['posts'] or not len(post_json['posts']):
                continue
            post_data = post_json['posts'][0]

            file_ext = post_data['file_ext']
            file_url = post_data['file_url']
            rating = post_data['rating']
            tags = '|'.join(post_data['tags'].split(' '))
            name = f'{yande_id}.{file_ext}'

            last_level_dir_name = len(str(yande_id)) < 4 and '0' or str(yande_id)[:len(str(yande_id)) - 4]
            dir_name = os.path.join(
                YANDE_FILE_PATH,
                rating == 's' and 'Safe' or rating == 'e' and 'Explicit' or 'Questionable',
                last_level_dir_name
            )
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)

            path = os.path.join(dir_name, name)

            if rating == 's':
                if int(post_data['score']) < YANDE_S_SCORE:
                    continue
            else:
                if int(post_data['score']) < YANDE_E_SCORE:
                    if os.path.exists(path):
                        os.remove(path)
                    continue

            if os.path.exists(path):
                MYSQL.execute('delete from yande_download_error where yande_id = %s', yande_id)
                continue

            for i in range(5):
                try:
                    response = requests.get(
                        url=file_url,
                        headers={'User-Agent': YANDE_AGENT_POOL.get()},
                        timeout=10
                    )
                    if not response.ok:
                        switch_clash_proxy()
                        time.sleep(2)
                        continue
                    with open(path, 'wb') as f:
                        f.write(response.content)
                        if not exist_db_data(yande_id):
                            MYSQL.execute(
                                'insert into yande_img(yande_id,name,rating,ext,en_tag) values (%s,%s,%s,%s,%s)',
                                (yande_id, name, rating, file_ext, tags)
                            )
                        MYSQL.execute('delete from yande_download_error where yande_id = %s', yande_id)
                        YANDE_LOGGER.log('info', f'下载历史图片成功: {name}')
                        time.sleep(2)
                        break
                except Exception as e:
                    switch_clash_proxy()
                    time.sleep(2)

        except Exception as e:
            switch_clash_proxy()
            YANDE_LOGGER.log('error', '下载历史错误图片失败')
            time.sleep(2)
            continue


if __name__ == '__main__':
    atexit.register(save_before_close)
    # threading.Timer(60 * 120, stop).start()
    main()
    download_error_image()
