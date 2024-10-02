import os.path

from mysql_tool import MySqlTool

mysql = MySqlTool(host='localhost', user='root', password='admin', database='neptune')
path = 'D:\\files\\yande'

# 遍历所有子目录的文件
yande_id_arr = []
for root, dirs, files in os.walk(path):
    if len(files) == 0 and len(dirs) == 0:
        os.rmdir(root)
    for file in files:
        # 获取文件名
        file_name = os.path.splitext(file)[0]
        yande_id_arr.append(file_name)

# 删除不在其中的数据
mysql.execute("DELETE FROM yande_img WHERE yande_id NOT IN (%s)" % ','.join(yande_id_arr))
