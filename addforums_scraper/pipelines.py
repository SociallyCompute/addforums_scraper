# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import csv


# class CsvWriterPipeline(object):
#
#     def __init__(self):
#         self.csvwriter = csv.writer(open('addforums_posts.csv', 'wb'))
#         self.csvwriter.writerow(['qid', 'localID', 'title', 'poster', 'date', 'replyTo', 'content'])
#
#     def process_item(self, item, addforums):
#         self.csvwriter.writerow([item['qid'], item['localID'], item['title'], item['poster'], item['date'], item['replyTo'], item['content']])
#         return item


class AddforumsScraperPipeline(object):
    def process_item(self, item, spider):
        return item
