import os
import time

# s = 'aaa bbb'
# # print(s.split(' '))
# # # 正则替换
# # print(re.sub('\s', '_', s))
# # print(s.replace('\s', '_'))
# s = '1189483'
# print(s[:len(s) - 4])

# with requests.get(url='https://yande.re/post.xml?page=99', headers={
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
# }, verify=False,
#                   proxies={
#                       'http': 'http://p.webshare.io',
#                       'https': 'http://p.webshare.io'
#                   }
#                   ) as response:
#     print(response.text)


# print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
# print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1636278400)))
# print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(1636278400 + 60 * 60 * 24)))
#
# # print(os.path.basename("D:\\files\\logs\\yande\\yande.log"))
# # print(os.path.dirname("D:\\files\\logs\\yande\\yande.log"))
#
# file_path='D:\\files\\logs\\yande'
# log_file = os.path.join(file_path,time.strftime('%Y-%m-%d', time.localtime()))
# print(log_file)
#
# if not os.path.exists(log_file):
#     os.makedirs(log_file)
# max_num = 0
# for file_name in os.listdir(log_file):
#     if file_name.startswith('yande.log_'):
#         num = int(file_name.split('_')[1].split('.')[0])
#         if num > max_num:
#             max_num = num
#
# print(max_num)

# rating = 's'
# test_file_name = rating == 's' and 'Safe' or 'Question'
# print(test_file_name)
# dir_name = 'test111'
# dir_name = os.path.join("D://test", rating == 's' and 'Safe' or 'Question', dir_name)
# print(dir_name)

# a = time.time()
# print(a)
# time.sleep(1)
# b = time.time()
# print(b)
# print(b - a)
# print(b - a > 60 * 60)
# print(b - a > 60 * 60 * 24 * 7)

# a = 'q'
# b = a == 's' and 'S' or a == 'e' and 'E' or 'Q'
# print(b)
#
# # 文件移动
# file1 = 'D:\\files\\flex\\logs\\app.log'
# file2 = 'D:\\files\\app.log'
# os.rename(file1, file2)

# import threading
#
# lock = threading.Lock()
#
# # 尝试获取锁
# if lock.acquire():  # 非阻塞尝试获取锁
#     print("锁未被占用，我们已获取到锁。")
#     lock.release()
# else:
#     print("锁已被占用，无法获取。")


print(os.path.exists("D:\\test\\aaa.txt"))