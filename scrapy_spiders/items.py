# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapySpidersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class CosmeItem(scrapy.Item):
    logo = scrapy.Field()
    info_json = scrapy.Field()
    imgs = scrapy.Field()
