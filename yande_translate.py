import random
import time
from hashlib import md5

import requests

from mysql_tool import MySqlTool


def translate():
    mysql = MySqlTool(host='localhost', user='root', password='admin', database='neptune')

    translate_fail_list = []

    tag_dict = {}
    tag_data = mysql.query('SELECT en, cn FROM yande_tag')
    for tag in tag_data:
        tag_dict[tag[0]] = tag[1]

    update_data = mysql.query('SELECT id, en_tag FROM yande_img WHERE cn_tag IS NULL')
    if not update_data:
        return
    for data in update_data:
        data_id = data[0]
        en_tag = data[1]
        if not en_tag:
            continue
        en_tag_list = en_tag.split('|')
        if not en_tag_list:
            continue
        cn_tag_list = []
        for en in en_tag_list:
            cn = '*'
            if en in tag_dict:
                cn = tag_dict[en]
            else:
                if en not in translate_fail_list:
                    try:
                        translate_fail_list.append(en)
                        continue
                        cn = you_dao_translate(en)
                        tag_dict[en] = cn
                        mysql.execute('INSERT INTO yande_tag(en, cn) VALUES(%s, %s)', (en, cn))

                    except Exception as e:
                        print('翻译失败', e)
                        translate_fail_list.append(en)
                        cn = '*'
                else:
                    cn = '*'

            cn_tag_list.append(cn)

        cn_tag = '|'.join(cn_tag_list)
        # mysql.execute('UPDATE yande_img SET cn_tag = %s WHERE id = %s', (cn_tag, data_id))

    # translate_fail_list去重
    translate_fail_list = list(set(translate_fail_list))
    print(translate_fail_list)


def you_dao_translate(en_text: str):
    time.sleep(random.randint(2, 3))

    headers = {
        'Cookie': 'OUTFOX_SEARCH_USER_ID=-690213934@10.108.162.139; OUTFOX_SEARCH_USER_ID_NCOO=1273672853.5782404; fanyi-ad-id=308216; fanyi-ad-closed=1; ___rl__test__cookies=1659506664755',
        'Host': 'fanyi.youdao.com',
        'Origin': 'https://fanyi.youdao.com',
        'Referer': 'https://fanyi.youdao.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    key = en_text
    lts = str(int(time.time() * 100))
    salt = lts + str(random.randint(0, 9))
    sign_data = 'fanyideskweb' + key + salt + 'Ygy_4c=r#e#4EX^NUGUc5'
    sign = md5(sign_data.encode()).hexdigest()
    data = {
        'i': key,
        'from': 'AUTO',
        'to': 'AUTO',
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        # 时间戳  1970  秒
        'salt': salt,
        # 加密
        'sign': sign,
        # 时间戳
        'lts': lts,
        # 加密的数据
        'bv': 'f0819a82107e6150005e75ef5fddcc3b',
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_REALTlME',
    }

    # 获取到资源地址
    url = 'https://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'
    response = requests.post(url, headers=headers, data=data)
    res_json = response.json()
    return res_json['translateResult'][0][0]['tgt']


if __name__ == '__main__':
    translate()
