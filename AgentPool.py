# 导入requests模块
import json

import requests
# 从bs4中导入BeautifulSoup模块
from bs4 import BeautifulSoup

# 定义获取代理地址的方法
def get_proxy(pages, ua):
    # 定义proxy_ips列表存储代理地址
    proxy_ips = []
    # 设置headers
    headers = {"User-Agent" : ua}
    # 从第一页开始循环访问
    for page in range(1,pages+1):
        print(f"正在爬取第{page}页!")
        url = "https://www.89ip.cn/index_{page}.html"
        res = requests.get(url, headers=headers)
        # 使用.text属性获取网页内容，赋值给html
        html = res.text
        # 用BeautifulSoup()传入变量html和解析器lxml，赋值给soup
        soup = BeautifulSoup(html,"lxml")
        # 使用find_all()方法查找类名为layui-table的标签
        table = soup.find_all(class_ = "layui-table")[0]
        # 使用find_all()方法查找tr标签
        trs = table.find_all("tr")
        # 使用for循环逐个访问trs列表中的tr标签,一个tr代表一行，第一行为表头，不记录
        for i in range(1,len(trs)):
            # 使用find_all()方法查找td标签
            ip = trs[i].find_all("td")[0].text.strip()
            port = trs[i].find_all("td")[1].text.strip()
            # 拼接代理地址
            proxy_ip = f"http://{ip}:{port}"
            # 将获取的代理地址保存到proxy_ips列表
            proxy_ips.append(proxy_ip)
    # 返回proxy_ips列表
    return proxy_ips

# 定义代理地址有效性验证方法
def test_proxy(ip, ua):
    # 设置headers
    headers = {"User-Agent" : ua}
    url = "https://www.baidu.com"
    # 设置代理信息
    proxies = {"http": ip}
    # 通过请求百度首页来验证代理地址是否有效
    try:
        res = requests.get(url, headers=headers, proxies=proxies, timeout=3)
    except requests.exceptions.Timeout:
        # 超过3秒未返回，则请求超时
        print("请求超时")
        result_code = 0
    else:
        result_code = res.status_code
    # finally:
    #     return res.status_code
    # 返回请求状态
    return result_code

# 主函数
if __name__ == "__main__":
    # 定义good_ips列表用于存储有效的代理地址
    good_ips = []
    # 定义User-Agent参数
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    # 设置获取页面的数量
    pages = 5
    # 调用get_proxy方法获取网站上的免费代理
    proxy_list = get_proxy(pages, ua)
    # 输出获取结果
    print(f"共爬取了 {len(proxy_list)} 个代理地址!")

    # 对获取的代理地址逐个进行有效性验证
    for ip in proxy_list:
        # 调用验证方法
        result = test_proxy(ip, ua)
        # 判断返回状态是否为200
        if result == 200:
            # 如果返回状态是为200，则保存到good_ips列表中
            good_ips.append(ip)
        else:
            # 否则continue
            continue
    # 输出检测结果
    print(f"共有 {len(good_ips)} 个代理地址通过了检测!")

    # 保存到json文件中
    with open("./agentPool.json", "w") as fp:
        json.dump(good_ips, fp, ensure_ascii=False, indent=4)
    print(f"代理地址保存完毕,保存地址为agentPool.json")

    # 保存有效代理地址到文件中
    # with open("D:\学习资料\Python\VSCode\yequbiancheng\工作业务\csdn自动化脚本\代理池.txt", "a") as fp:
    #     # 将地址逐个写入txt文件中
    #     for i in good_ips:
    #         fp.write(f"{i}"+"\n")
    # print(f"代理地址保存完毕,保存地址为D:\学习资料\Python\VSCode\yequbiancheng\工作业务\csdn自动化脚本\代理池.txt")
