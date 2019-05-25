import sys
from functools import wraps

import redis


def singleton(cls):
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return get_instance


@singleton
class RedisInstant(object):
    """
    初始化Redis连接
    """

    def __init__(self, tp, website, rhost, rdb, rport, rpassword):
        self.redis = redis.StrictRedis(host=rhost, db=int(rdb), password=rpassword, port=int(rport),
                                       decode_responses=True)
        # 保存的类型
        self.type = tp
        # 保存的网站
        self.website = website

    @property
    def name(self):
        return "{}:{}".format(self.type, self.website)

    def set(self, key, value):
        # 注：
        # hmset(name, mapping)，在name对应的hash中 批量 设置键值对
        # hsetnx(name, key, value),当key对应的hash中不存在当前key时则创建（相当于添加）

        # 对应的hash中设置一个键值对（不存在，则创建；否则，修改）
        return self.redis.hset(self.name, key, value)

    def get(self, key):
        # 注：
        # hmget(name, keys, *args) 在name对应的hash中获取多个key的值
        # hgetall(name) 获取name对应hash的所有键值
        return self.redis.hget(self.name, key)

    def delete(self, key):
        return self.redis.hdel(self.name, key)

    def count(self):
        return self.redis.hlen(self.name)

    def exists(self, key):
        # 检查name对应的hash是否存在当前传入的key
        return self.redis.hexists(self.name, key)


if __name__ == '__main__':
    # r = RedisInstant('test', 'test.com')
    # print(r.name)
    print(sys.path)
