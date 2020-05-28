# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import base64
import time
import hashlib
from random import choice
import datetime


class ScrapySpidersSpiderMiddleware(object):
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

        # Should return either None or an iterable of Request, dict
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


class ScrapySpidersDownloaderMiddleware(object):
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


class SuperProxy(object):
    def proxy_kuai(self):
        # 隧道服务器
        tunnel_host = "tps136.kdlapi.com"
        tunnel_port = "***********"

        # 隧道id和密码
        tid = "***********"
        password = "***********"
        proxy_server = 'http://%s:%s@%s:%s' % (tid, password, tunnel_host, tunnel_port)
        proxy_auth = "Basic %s" % (base64.b64encode(('%s:%s' % (tid, password)).encode('utf-8'))).decode('utf-8')
        return proxy_server, proxy_auth, "kuai"

    def proxy_abu(self):
        # 代理服务器
        proxy_server = "http://http-dyn.abuyun.com:9020"
        # 代理隧道验证信息
        proxy_user = "***********"
        proxy_pass = "***********"
        proxy_auth = "Basic " + base64.urlsafe_b64encode(bytes((proxy_user + ":" + proxy_pass), "ascii")).decode("utf8")
        return proxy_server, proxy_auth, "abu"

    def proxy_xun(self):
        # 讯代理服务器
        proxy_server = "http://forward.xdaili.cn:80"
        # 代理隧道验证信息
        proxy_user = "ZF201932107811lGLxU"  # 订单号
        proxy_pass = "c8b46593a14f4f368aa7873b9daa509c"  # 秘钥

        timestamp = str(int(time.time()))  # 计算时间戳
        string = "orderno=" + proxy_user + "," + "secret=" + proxy_pass + "," + "timestamp=" + timestamp
        string = string.encode()
        md5_string = hashlib.md5(string).hexdigest()  # 计算sign
        sign = md5_string.upper()  # 转换成大写
        proxyAuth = "sign=" + sign + "&" + "orderno=" + proxy_user + "&" + "timestamp=" + timestamp
        return proxy_server, proxyAuth, "xun"

    def process_request(self, request, spider):
        # 随机选择
        # if "cnca.cn" in request.url:
            proxy_server, proxy_auth, name = choice([self.proxy_xun])()
            request.meta["proxy"] = proxy_server
            request.headers["Proxy-Authorization"] = proxy_auth
            print("---- super请求请求 {} 正在使用代理隧道-{} 请求地址：{} ----".format(
                datetime.datetime.now(), name, request.url)
            )