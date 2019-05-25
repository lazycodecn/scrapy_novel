# -*- coding: utf-8 -*-
import re
from datetime import datetime
from urllib.parse import urljoin

import cn2an
import redis
import scrapy
from pyquery import PyQuery
from scrapy.http import Request

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
        h = self.settings.get('REDIS_HOST')
        db = self.settings.get('REDIS_DB_DATA')
        pw = self.settings.get('REDIS_PASSWORD')
        self.rds = redis.StrictRedis(host=h, db=db, password=pw)

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
        i['author'] = self.rds.hget(i.get('bookName'), "author").decode('utf-8')
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
        cookies = Login(username, password).cookies
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                          'Chrome/74.0.3729.108 Safari/537.36',
        }
        r = PyQuery('https://m.biqudao.com/case.php', cookies=cookies, headers=headers)
        hotSales = r('.hot_sale').items()

        for hot in hotSales:
            href = hot.find('a[style="color: Red;"]').attr('href')
            bookName = hot('.title:first-child').text().strip()
            if not self.rds.hexists(bookName, 'author'):
                author = hot('a>p.author').text().split('：')[1].strip()
                self.rds.hset(bookName, 'author', author)
            yield Request(url=urljoin(self.start_urls[0], href))

    def convert_to_inter(self, value):
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
