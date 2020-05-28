# -*- coding: utf-8 -*-
import scrapy


class CosmeSpider(scrapy.Spider):
    name = 'cosme'
    allowed_domains = ['cosme.com']
    start_urls = ['http://cosme.com/']

    def parse(self, response):
        pass
