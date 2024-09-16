import threading


class DownloadTaskThread(threading.Thread):
    def __init__(self, func, args=()):
        super(DownloadTaskThread, self).__init__()
        self.func = func  # 要执行的task类型
        self.args = args  # 要传入的参数

    def run(self):
        # 线程类实例调用start()方法将执行run()方法,这里定义具体要做的异步任务
        print("start func {}".format(self.func.__name__))  # 打印task名字　用方法名.__name__
        self.result = self.func(*self.args)  # 将任务执行结果赋值给self.result变量

    def get_result(self):
        # 改方法返回task函数的执行结果,方法名不是非要get_result
        try:
            return self.result
        except Exception as ex:
            print(ex)
            return "ERROR"
