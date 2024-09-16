import re

import bs4
import requests

from mysql_tool import MySqlTool

resp = requests.get(
    url='https://github.com/zhzwz/yande-re-chinese-patch',
    headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
)
soup = bs4.BeautifulSoup(resp.text, 'lxml')
dom = soup.select('markdown-accessiblity-table>table tr')
en = ''
cn = ''
mysql = MySqlTool(host='localhost', user='root', password='admin', database='neptune')
mysql.execute('delete from yande_tag')
for index, tr in enumerate(dom):
    if not tr.select('td[align="left"]'):
        continue
    en = tr.select('td[align="left"]')[0].text.strip()
    en = re.sub(r'\s+', '_', en)
    cn = tr.select('td[align="left"]')[1].text.strip()
    print(f"{en} : {cn}")
    mysql.execute("insert into yande_tag(en, cn) values (%s, %s)", (en, cn))
