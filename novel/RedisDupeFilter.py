import logging
import redis
from scrapy.dupefilters import BaseDupeFilter

logger = logging.getLogger(__name__)


class RFPDupeFilter(BaseDupeFilter):
    """
    使用redsi进行url排重
    """
    # 日志
    logger = logger

    def __init__(self, redis, key, debug=False):
        self.fredis = redis
        self.key = key
        self.debug = debug
        self.logdupes = True

    @classmethod
    def from_settings(cls, settings):
        fh = settings.get('REDIS_HOST')
        fdb = int(settings.get('REDIS_DB_DATA'))
        fpw = settings.get('REDIS_PASSWORD')
        fpt = int(settings.get('REDIS_PORT'))
        frds = redis.StrictRedis(host=fh, port=fpt, db=fdb, password=fpw)
        return super().from_settings(settings)

    def request_seen(self, request):
        return super().request_seen(request)

    def open(self):
        super().open()

    def close(self, reason):
        super().close(reason)

    def log(self, request, spider):
        super().log(request, spider)
