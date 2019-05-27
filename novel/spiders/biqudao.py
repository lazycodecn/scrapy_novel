# -*- coding: utf-8 -*-
import re
from datetime import datetime
from urllib.parse import urljoin

import requests

from novel.data.RedisFactory import AbstractRedis
import cn2an
import redis
import scrapy
from pyquery import PyQuery
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor

from novel.data.Login import Login
from novel.items import NovelItem


class BiqudaoSpider(scrapy.Spider):
    name = 'biqudao'
    allowed_domains = ['m.biqudao.com']
    start_urls = ['http://m.biqudao.com/']

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = cls(*args, **kwargs)
        spider._set_crawler(crawler)
        spider.set_redis(crawler)
        return spider

    def set_redis(self, crawler):
        # 此 spider禁止调用 get,set
        # todo:添加禁止的操作
        self.rds = AbstractRedis.create_redis_instant(crawler.settings, "", "hash")
        self.case_url = crawler.settings.get('NOVEL_CASE_URL')

    def parse(self, response):
        i = NovelItem()
        i['content'] = "\n".join(response.css('#chaptercontent::text').extract())
        i['gmtCreate'] = datetime.now()
        headline = response.css('title').extract_first()
        headlines = headline.split('_')
        chapter = headlines[0].split('章')[0]
        i['chapter'] = chapter
        i['title'] = headlines[0].split('章')[1]
        i['bookName'] = headlines[1].strip()
        self.rds.name = i.get('bookName')
        i['author'] = self.rds.get("author")
        # 处理 一二一二  这种诡异数据
        if chapter.find('十') > 0 or chapter.find('百') > 0 or chapter.find("千") > 0:
            i['number'] = cn2an.cn2an(re.sub('.*?第', '', chapter))
        else:
            i['number'] = int(self.convert_to_inter(chapter))

        i['ptPrev'] = urljoin(self.start_urls[0], response.css('#pt_prev::attr(href)').extract_first())
        i['url'] = response.url
        yield i

    def start_requests(self):
        username = self.settings.get('USERNAME')
        password = self.settings.get('PASSWORD')
        cookies = Login(username, password, self.settings, logger=self.logger).cookies
        headers = {
            "cache-control": "no-cache",
            "upgrade-insecure-requests": 1,
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                          'Chrome/74.0.3729.108 Safari/537.36',
        }
        rcase = requests.get(self.case_url, cookies=cookies, headers=headers)
        r = PyQuery(rcase.text)
        # 获取 个人书架列表
        hotSales = r('.hot_sale').items()

        for hot in hotSales:
            href = hot.find('a[style="color: Red;"]').attr('href')

            # 保存书籍的作者名
            bookName = hot('.title:first-child').text().strip()
            self.rds.name = bookName
            if not self.rds.exists('author'):
                author = hot('a>p.author').text().split('：')[1].strip()
                self.rds.set('author', author)
            # 请求生成器
            yield Request(url=urljoin(self.start_urls[0], href))

    @staticmethod
    def convert_to_inter(value):
        """
        将 一二一二这种去除个十百的数据转变成数字
        :param value: 一二一二
        :return: 1212
        """
        numberList = {
            "一": "1",
            "二": "2",
            "三": "3",
            "四": "4",
            "五": "5",
            "六": "6",
            "七": "7",
            "八": "8",
            "九": "9",
            "零": "0"
        }
        result = ""
        for i in value:
            if numberList.get(i) is not None:
                result += numberList.get(i)
        return int(result)

# if __name__ == '__main__':
#     link = LinkExtractor(allow=r'/bqge.*?/.*?\.html')
#     print(link.matches("/bqge123245/7026528.html"))
