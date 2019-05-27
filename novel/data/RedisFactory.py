from abc import ABCMeta, abstractmethod

import redis


class AbstractRedis(metaclass=ABCMeta):

    def __init__(self, bind_key, rhost, rdb, rport, rpassword):
        # 保存的类型
        self.type = bind_key
        self.rds = redis.StrictRedis(host=rhost, db=rdb, port=rport,
                                     password=rpassword, decode_responses=True)

    @property
    def name(self):
        return self.type

    @name.setter
    def name(self, value):
        self.type = value

    @staticmethod
    def create_redis_instant(settings, bind_key, ty):
        h = settings.get('REDIS_HOST')
        db = int(settings.get('REDIS_DB_DATA'))
        pw = settings.get('REDIS_PASSWORD')
        pt = int(settings.get('REDIS_PORT'))
        if ty == "hash":
            return RedisHashInstant(bind_key, h, db, pt, pw)
        if ty == "string":
            return RedisStringInstant(bind_key, h, db, pt, pw)

    @staticmethod
    def create_redis_instant_no_bind_key(settings, ty):
        h = settings.get('REDIS_HOST')
        db = int(settings.get('REDIS_DB_DATA'))
        pw = settings.get('REDIS_PASSWORD')
        pt = int(settings.get('REDIS_PORT'))
        if ty == "hash":
            return RedisHashInstant("", h, db, pt, pw)
        if ty == "string":
            return redis.StrictRedis(h, pt, db, pw, decode_responses=True)

    @abstractmethod
    def get(self, key=None):
        pass

    @abstractmethod
    def set(self, key, value):
        pass

    @abstractmethod
    def exists(self, key):
        pass


class RedisStringInstant(AbstractRedis):

    def __init__(self, bind_key, rhost, rdb, rport, rpassword):
        super().__init__(bind_key, rhost, rdb, rport, rpassword)

    def get(self, key=None):
        self.rds.get(self.name)

    def set(self, key, value):
        pass

    def exists(self, key):
        pass


class RedisHashInstant(AbstractRedis):
    """
    初始化Redis连接
    """

    def __init__(self, bind_key, rhost, rdb, rport, rpassword):
        super().__init__(bind_key, rhost, rdb, rport, rpassword)

    def set(self, key, value):
        # 注：
        # hmset(name, mapping)，在name对应的hash中 批量 设置键值对
        # hsetnx(name, key, value),当key对应的hash中不存在当前key时则创建（相当于添加）

        # 对应的hash中设置一个键值对（不存在，则创建；否则，修改）
        return self.rds.hset(self.name, key, value)

    def hset(self, name, key, value):
        """
        适配方法
        :param name: 表名
        :param key: key
        :param value:  value
        :return: redis.hset
        """

        return self.rds.hset(name, key, value)

    def hget(self, name, key):
        """
        适配方法
        :param name: name
        :param key: key
        :return: redis.hget(name,key)
        """

        return self.rds.hget(name, key)

    def get(self, key=None):
        # 注：
        # hmget(name, keys, *args) 在name对应的hash中获取多个key的值
        # hgetall(name) 获取name对应hash的所有键值
        return self.rds.hget(self.name, key)

    def delete(self, key):
        return self.rds.hdel(self.name, key)

    def count(self):
        return self.rds.hlen(self.name)

    def exists(self, key):
        # 检查name对应的hash是否存在当前传入的key
        return self.rds.hexists(self.name, key)

    def incrby(self, key, amount):
        return self.rds.hincrby(self.name, key, amount)

    def hincrby(self, name, key, amount):
        return self.rds.hincrby(name, key, amount)


if __name__ == '__main__':
    ss = {
        "REDIS_HOST": "localhost",
        "REDIS_PORT": 6379,
        "REDIS_PASSWORD ": "",
        # db1 储存常规数据
        "REDIS_DB_DATA": 3
    }
    rds = AbstractRedis.create_redis_instant(ss, "test", "hash")
    rds.set("test", "test")
