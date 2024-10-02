import json

import requests

from mysql_tool import MySqlTool

API_KEY = 'string'
API_URL = 'http://ip:port/api'
url = "http://ip:port/api/search/metadata"

payload = json.dumps({
    "deviceId": "string",
    "order": "desc",
    "page": 1,
    "size": 100
})
headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'x-api-key': '9IP9zlGrvPwZSOLMKJRZcEkiFsSSGPBiZd2PTrJ4'
}

mysql = MySqlTool(host='localhost', user='root', password='admin', database='neptune')

LOCAL_TAG_DICT = {}
tag_data = mysql.query('SELECT en, cn FROM yande_tag')
for tag in tag_data:
    LOCAL_TAG_DICT[tag[0]] = tag[1]

TAG_DICT = {}
response = requests.request("GET", f'{API_URL}/tags', headers=headers, data={})
tags = response.json()
for tag in tags:
    TAG_DICT[tag['name']] = tag['id']

page = 1
while True:

    response = requests.request(
        "POST",
        f'{API_URL}/search/metadata',
        headers=headers,
        data=json.dumps({
            "deviceId": "Library Import",
            "order": "desc",
            "page": page,
            "size": 100
        }),
        timeout=10
    )
    datas = response.json()
    assets = datas['assets']
    items = assets['items']
    if not items or len(items) == 0:
        break

    for item in items:
        assetId = item['id']
        original_file_name = item['originalFileName']
        yande_id = int(original_file_name.split('.')[0])

        select_data = mysql.query('select en_tag from yande_img where yande_id = %s', (yande_id))
        if not select_data:
            continue
        en_tag = select_data[0][0]
        if not en_tag:
            continue
        en_tag_list = en_tag.split('|')
        if len(en_tag_list) == 0:
            continue
        cn_tag_list = []
        for en in en_tag_list:
            if en in LOCAL_TAG_DICT:
                cn = LOCAL_TAG_DICT[en]
                cns = cn.split('/')
                for cn in cns:

                    if cn not in TAG_DICT:
                        response = requests.request(
                            "POST",
                            f'{API_URL}/tags',
                            headers=headers,
                            data=json.dumps({"name": cn})
                        )
                        tag_json = response.json()
                        TAG_DICT[cn] = tag_json['id']

                    cn_tag_list.append(cn)

        if len(cn_tag_list) == 0:
            continue

        tagIds = []
        for cn_tag in cn_tag_list:
            tagIds.append(TAG_DICT[cn_tag])

        requests.request(
            "PUT",
            f'{API_URL}/tags/assets',
            headers=headers,
            data=json.dumps({
                "assetIds": [
                    assetId
                ],
                "tagIds": tagIds
            })
        )

    page += 1
