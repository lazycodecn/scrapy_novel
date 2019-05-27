import json
from functools import wraps

import requests

from novel.data.RedisFactory import AbstractRedis


def singleton(cls):
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return get_instance


@singleton
class Login(object):  # self._cookies_file_url = 'cookies.txt'
    """
    1.复习 Cookies的保存和设置
    2.复习redis的使用
    """

    def __init__(self, username='', password='', settings="", logger=None):
        self.logger = logger
        self.credis = AbstractRedis.create_redis_instant(settings, 'cookies:m.biqudao.com', "hash")
        self.username = username
        self.password = password
        self._cookies = None
        self._login_url = 'https://m.biqudao.com/Dologin.php'
        self._user_profile = 'https://m.biqudao.com/case.php'
        # True 表示已经从file中读取过,可以解决 失效 的问题
        self._already_read_file = False

    @property
    def cookies(self):
        # 检查是否存在cookies
        if self.__check_cookies():
            return self._cookies
        else:
            if self.get_cookies_web():
                return self._cookies
        raise RuntimeError("无法获取数据")

    @cookies.setter
    def cookies(self, value):
        self._cookies = value

    def __check_cookies(self):
        if self._cookies is not None:
            return True
        else:
            return self.get_cookies_from_redis()

    @staticmethod
    def check_status(status_code):
        """
        判断返回信息的状态码,如果为302,则返回 False
        :param status_code: 状态码
        :return: True
        """
        if status_code == requests.codes.ok:
            return True
        else:
            return False

    def get_cookies_from_redis(self):
        """
            1.0尝试从文件中读取 Cookies ，成功返回True
            2.0尝试从Redis中读取 Cookies
        :return: true
        """
        self._already_read_file = True
        if self.credis.exists(self.username):
            # if os.path.isfile(self._cookies_file_url):
            self.logger.info('读取保存的Cookies')
            j_cookies = self.credis.get(self.username)
            j_jar = requests.utils.cookiejar_from_dict(json.loads(j_cookies))
            self.cookies = j_jar
            return True

        return False

    def get_cookies_web(self):
        """
            从网站获取Cookies
        :return true
        """
        data = {
            'username': self.username,
            'password': self.password,
            'login_hold': 1,
            'bk': '/',
            'action': 'login'
        }
        headers = {
            'Referer': 'https://m.biqudao.com/login.php',
            # 'origin': 'https://m.biqudao.com',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                          'Chrome/74.0.3729.108 Safari/537.36',
        }
        try:
            r = requests.post(self._login_url, data=data, headers=headers)
            self.cookies = r.cookies
            j_cookies = requests.utils.dict_from_cookiejar(r.cookies)
            self.credis.set(self.username, json.dumps(j_cookies))
            self.logger.info("从服务器获取 Cookies 成功")
            self._already_read_file = False
            # print(type(result.cookies), result.cookies)
            return True
        except Exception:
            return False
