import cv2
import numpy as np

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
image_path = 'D:\\files\\yande\\Question\\109\\1092279.png'
if is_single_color_block(image_path):
    print("图像中存在大块单一颜色区域")
else:
    print("图像中没有大块单一颜色区域")
