import json
import urllib.parse

import cv2
import numpy as np
import requests
from bs4 import BeautifulSoup


'''
获取单个数据页面API：https://yande.re/post/show/1194966

JS示范：document.querySelectorAll('a#highres.original-file-changed')[0].href
'''


def is_single_color_block(image_path, block_size=50, color_threshold=0.5):
    # 读取图像
    img = cv2.imread(image_path)
    img_height, img_width, _ = img.shape

    # 计算图像的总像素数
    total_pixels = img_width * img_height

    # 计算块的大小和所需颜色块的像素数
    block_pixel_count = block_size * block_size
    required_block_pixels = total_pixels * color_threshold

    # 创建一个布尔数组用于标记单一颜色区域
    color_blocks = np.zeros((img_height, img_width), dtype=bool)

    # 遍历图像中的每个块
    for y in range(0, img_height - block_size + 1, block_size):
        for x in range(0, img_width - block_size + 1, block_size):
            block = img[y:y + block_size, x:x + block_size]

            # 获取块的所有像素的颜色
            unique_colors = np.unique(block.reshape(-1, 3), axis=0)

            # 如果块中所有像素的颜色相同
            if len(unique_colors) == 1:
                # 标记块中的所有像素为单一颜色
                color_blocks[y:y + block_size, x:x + block_size] = True

    # 计算所有标记区域的像素数
    single_color_pixel_count = np.sum(color_blocks)

    # 如果符合条件，则返回True
    if single_color_pixel_count >= required_block_pixels:
        print(f"发现大块单一颜色区域，占比: {single_color_pixel_count / total_pixels:.2f}")
        return True

    return False


# 使用函数检测图像
# image_path = 'D:\\files\\yande\\Question\\109\\1096799.png'
# if is_single_color_block(image_path):
#     print("图像中存在大块单一颜色区域")
# else:
#     print("图像中没有大块单一颜色区域")


def download():
    pass


def main():
    pass



import re

text = ' Post.register_resp({"posts":[{"id":1194966,"tags":"fu_u03","created_at":1726568030,"updated_at":1726568033,"creator_id":175701,"approver_id":null,"author":"saemonnokami","change":6119099,"source":"https://i.pximg.net/img-original/img/2024/06/30/00/00/20/120094347_p0.jpg","score":19,"md5":"3cc60c29f1c04396ef29cc7db1f311a2","file_size":4119872,"file_ext":"jpg","file_url":"https://files.yande.re/image/3cc60c29f1c04396ef29cc7db1f311a2/yande.re%201194966%20fu_u03.jpg","is_shown_in_index":true,"preview_url":"https://assets.yande.re/data/preview/3c/c6/3cc60c29f1c04396ef29cc7db1f311a2.jpg","preview_width":86,"preview_height":150,"actual_preview_width":172,"actual_preview_height":300,"sample_url":"https://files.yande.re/sample/3cc60c29f1c04396ef29cc7db1f311a2/yande.re%201194966%20sample%20fu_u03.jpg","sample_width":858,"sample_height":1500,"sample_file_size":196860,"jpeg_url":"https://files.yande.re/image/3cc60c29f1c04396ef29cc7db1f311a2/yande.re%201194966%20fu_u03.jpg","jpeg_width":3049,"jpeg_height":5330,"jpeg_file_size":0,"rating":"s","is_rating_locked":false,"has_children":false,"parent_id":null,"status":"active","is_pending":false,"width":3049,"height":5330,"is_held":false,"frames_pending_string":"","frames_pending":[],"frames_string":"","frames":[],"is_note_locked":false,"last_noted_at":0,"last_commented_at":0}],"pool_posts":[],"pools":[],"tags":{"fu_u03":"artist"},"votes":{}}); '
pattern = r"Post.register_resp\(.*\)"  # 正则表达式，用于找到包含"test"的单词

matches = re.findall(pattern, text)

print(matches)  # 输出: ['test', 'string']
# 读取matches[0]中的json数据

print(json.loads(matches[0].replace("Post.register_resp(", "").replace(")", "")))

if __name__ == '__main__':
    pass
    try:
        response = requests.get(
            url=f'https://yande.re/post/show/1194966',
            headers={'User-Agent': "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)"},
            timeout=5
        )
        if not response.ok:
            print('error','下载历史错误图片失败')
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        # document.querySelectorAll('a#highres.original-file-changed')[0].href
        img_url = soup.select_one('a#highres.original-file-changed').get('href')
        print(img_url)
        print(urllib.parse.unquote(img_url))
    except Exception as e:
        print.log('error','下载历史错误图片失败')
