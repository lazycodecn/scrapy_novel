# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NovelItem(scrapy.Item):
    chapter = scrapy.Field()
    title = scrapy.Field()
    bookName = scrapy.Field()
    author = scrapy.Field()
    gmtCreate = scrapy.Field()
    content = scrapy.Field()
    number = scrapy.Field()
    ptPrev = scrapy.Field()
    url = scrapy.Field()
