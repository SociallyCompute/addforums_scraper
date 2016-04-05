# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PostItem(scrapy.Item):
    unique_fields = ['uniqueID']

    uniqueID = scrapy.Field()
    qid = scrapy.Field()
    localID = scrapy.Field()
    title = scrapy.Field()
    poster = scrapy.Field()
    date = scrapy.Field()
    replyTo = scrapy.Field()
    content = scrapy.Field()
    inferred_replies = scrapy.Field()
