import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from requests.exceptions import RequestException, Timeout, HTTPError


def download(url, path, proxies=None):
    """
    下载文件，并处理失败重试、超时、代理设置及请求头。
    :param url: 文件的URL
    :param path: 保存文件的本地路径
    :param proxies: 代理设置（字典），可选
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    session = requests.Session()

    # 设置重试机制
    retry_strategy = Retry(total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    # 配置代理（如果提供了）
    if proxies:
        session.proxies.update(proxies)

    session.headers.update(headers)

    try:
        # 发起请求
        response = session.get(url, timeout=5, stream=True)
        response.raise_for_status()  # 确保HTTP请求返回200状态码

        # 写入文件
        with open(path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"文件已成功下载到: {path}")

    except Timeout:
        print("请求超时，请检查网络连接和超时设置。")
    except HTTPError as http_err:
        print(f"HTTP错误发生: {http_err}")
    except ValueError as val_err:
        print(f"值错误: {val_err}")
    except RequestException as req_err:
        print(f"请求失败: {req_err}")
    except Exception as e:
        print(f"下载过程中发生错误: {e}")

#
def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
