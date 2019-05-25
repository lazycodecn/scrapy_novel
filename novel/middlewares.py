# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import random

import redis
from scrapy import signals
from scrapy.http import Request
from scrapy.exceptions import IgnoreRequest
from scrapy import Item
from scrapy.xlib.pydispatch import dispatcher
from scrapy.utils.request import request_fingerprint


class RandomUserAgentMiddleware(object):
    def __init__(self):
        self.user_agents = [
            ' Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
            'User-Agent:Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) ' +
            'AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'User-Agent:Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;'
        ]

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(self.user_agents)


class RequestCheckMiddleWare(object):
    def __init__(self, host, passwd, db, port):
        self.rds = redis.StrictRedis(host=host, db=db, port=port, password=passwd, decode_responses=True)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        h = crawler.settings.get('REDIS_HOST')
        db = crawler.settings.get('REDIS_DB_REQUEST')
        pw = crawler.settings.get('REDIS_PASSWORD')
        pt = int(crawler.settings.get('REDIS_PORT'))
        s = cls(host=h, db=db, passwd=pw, port=pt)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        if self.rds.get(request_fingerprint(request)) is not None:
            #     已经读取过该url
            spider.logger.error(f'已经读取过 : {request.url}')
            raise IgnoreRequest()
        else:
            self.rds.set(request_fingerprint(request), 1, ex=604800, nx=True)
        return None

    def process_response(self, request, response, spider):
        headline = response.css('title').extract_first()
        if headline.find('第') < 0 and headline.find('章') < 0:
            raise IgnoreRequest(f'无效的章节 : {headline}')
        return response

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    @staticmethod
    def request_fingerprint(request):
        """Returns a fingerprint for a given request.

        Parameters
        ----------
        request : scrapy.http.Request

        Returns
        -------
        str

        """
        return request_fingerprint(request)


class PostponeChapterSpiderMiddleware(object):

    def __init__(self, host, passwd, db, port):
        self.rds = redis.StrictRedis(host=host, db=db, port=port, password=passwd, decode_responses=True)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        h = crawler.settings.get('REDIS_HOST')
        db = crawler.settings.get('REDIS_DB_DATA')
        pw = crawler.settings.get('REDIS_PASSWORD')
        pt = int(crawler.settings.get('REDIS_PORT'))
        s = cls(host=h, db=db, passwd=pw, port=pt)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        dispatcher.connect(s.add_delay_number, signals.item_scraped)
        return s

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        global it
        for it in result:
            if isinstance(it, Item):
                bookName = it.get('bookName')
                current_number = it.get('number')
                old_number = self.rds.hget(bookName, 'flag')
                # 第一次读取
                if old_number is None:
                    self.rds.hset(bookName, 'flag', current_number)
                    self.rds.hset(bookName, 'delay', 0)
                else:
                    # 离这一次更新偏离
                    number_offset = int(current_number) - int(old_number)
                    number_delay = int(self.rds.hget(bookName, 'delay'))
                    # 处理延迟章节
                    if number_delay == 0:
                        # 正常更新或者章节换章
                        if number_offset == 1 or number_offset < 0:
                            self.rds.hset(bookName, 'flag', current_number)
                        # 多章为读取
                        elif number_offset > 0:
                            spider.logger.info(f"修复读取 {bookName} 第 {current_number - 1}")
                            self.rds.hset(bookName, 'delay', number_offset - 1)
                            self.rds.hset('delay', bookName, number_offset)
                            yield Request(url=it.get('ptPrev'))
                    elif number_delay > 0:
                        self.rds.hincrby(bookName, 'delay', -1)
                        spider.logger.info(f"修复读取 {bookName} 第 {current_number - 1}")
                        yield Request(url=it.get('ptPrev'))
        yield it

    def add_delay_number(self):
        book_delay_dist = self.rds.hgetall('delay')
        for v, k in book_delay_dist.items():
            self.rds.hincrby(v, 'flag', int(k))
        self.rds.delete('delay')

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class NovelSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class NovelDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
