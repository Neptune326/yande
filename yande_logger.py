import inspect
import logging
import os
import time


class YandeLogger:
    def __init__(self, file_path='D:\\files\\logs\\yande'):
        # log_file根据项目实际情况设置，建议配置文件获取
        self.logger = logging.getLogger("YANDE")
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]%(message)s')
        # 写入日志文件

        log_file = self.get_log_file_path(file_path)

        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.stream = open(log_file, 'w', encoding='utf-8')
        # 设置handler的fsync参数为True，实现实时写入
        file_handler.stream.flush()
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # 写入控制台（可选）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def get_log_file_path(self, file_path):
        file_dir_path = os.path.join(file_path, time.strftime('%Y%m%d', time.localtime()))
        if not os.path.exists(file_dir_path):
            os.makedirs(file_dir_path)

        # 找到该路径下序号最大的数字，格式为 yande_20240916_0.log
        max_num = -1
        for file_name in os.listdir(file_dir_path):
            if file_name.startswith('yande_') and file_name.endswith('.log'):
                num = int(file_name.replace('yande_', '').replace('.log', '').split('_')[1])
                if num > max_num:
                    max_num = num

        log_file = os.path.join(
            file_dir_path,
            'yande_' + time.strftime('%Y%m%d', time.localtime()) + '_' + str(max_num + 1) + '.log'
        )
        return log_file

    def log(self, level, message):
        frame = inspect.stack()[1]
        function_name = frame[3]
        line_number = frame[2]

        log_message = f" Function: {function_name}, Line: {line_number} \n{message} "
        getattr(self.logger, level)(log_message)
