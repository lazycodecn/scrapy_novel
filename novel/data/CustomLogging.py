import logging
import sys


class Logging(object):

    def __init__(self, name, dir="/data", log_name="data"):
        self.__init_log(name, dir, log_name)

    @property
    def lg(self):
        return self.logger

    def __init_log(self, name="", dir="/data", log_name="data"):
        app_name = name
        self.logger = logging.getLogger(app_name)

        # fmt:定义输出的日志信息的格式
        # datefmt：定义时间信息的格式，默认为：%Y-%m-%d %H:%M:%S
        # style:定义格式化输出的占位符，默认是%(name)格式，可选{}或$格式
        formatter = logging.Formatter(fmt='%(asctime)s    %(levelname)s:  %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S',
                                      style='%')
        # 文件
        file_handle = logging.FileHandler(f"{dir}/{log_name}.log")
        file_handle.setFormatter(formatter)

        # 控制台日志
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.formatter = formatter

        self.logger.addHandler(file_handle)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)
