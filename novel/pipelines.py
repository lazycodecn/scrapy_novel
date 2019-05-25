# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import os
import re


class ReCleanPipeline(object):
    def __init__(self):
        # self.number_pattern = re.compile('^\\d*$')
        # self.chapter_pattern = re.compile('^第.*')
        self.content_clean_pattern = re.compile("<p.*?></p>", re.M)
        self.content_br_pattern = re.compile('<br.?>')
        self.content_line_pattern = re.compile(r"^\n[\s]+?\n", re.S)

    def process_item(self, item, spider):
        # if re.fullmatch(self.number_pattern, item['number']) is None \
        #         or re.fullmatch(self.chapter_pattern, item['chapter']):
        #     spider.logger.error("错误的获取数据: " + json.dumps(item))
        #     return DropItem("错误的解析数据")
        # item['content'] = re.sub(self.content_clean_pattern, '', item.get('content'))
        # item['content'] = re.sub(self.content_br_pattern, '', item.get('content'))
        item['content'] = re.sub(self.content_line_pattern, '', item.get('content')).strip()
        item['title'] = item.get('title').strip()
        item['bookName'] = item.get('bookName').strip()
        return item


class TextPipeline(object):

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            base_url=crawler.settings.get('BASE_URL')
        )

    def __init__(self, base_url):
        self.base_url = base_url

    def process_item(self, item, spider):
        title = item.get('bookName') + '-' + item.get('title')
        author = item.get('author')
        headline = title + '.txt'
        dist = self.base_url + headline
        with open(dist, 'w') as f:
            f.write(item.get('content'))
        os.system(f"sh auto_send.sh {title} {author} {self.base_url} ")
