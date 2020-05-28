# -*- coding: utf-8 -*-
import scrapy
from scrapy_spiders import settings
from scrapy.cmdline import execute
from bs4 import BeautifulSoup
import math
from scrapy_spiders.items import CosmeItem


settings.DOWNLOADER_MIDDLEWARES = {
    'scrapy_spiders.middlewares.SuperProxy': 543,
}

settings.ITEM_PIPELINES = {
   'scrapy_spiders.pipelines.JsonWriterPipeline': 301,
   'scrapy_spiders.pipelines.CosmeImagesPipeline': 300,
}


class CosmeSpider(scrapy.Spider):
    name = 'cosme'
    allowed_domains = []
    start_urls = ['https://cosme.pclady.com.cn/brand_list.html']

    def parse(self, response):
        """
        处理品牌列表，获取品牌名称+链接
        :param response:
        :return:
        """
        soup = BeautifulSoup(response.text, "lxml")
        part = soup.find_all(class_="part")
        for p in part:
            a_tags = p.find_all("a")
            for a in a_tags:
                spans = a.find_all("span")
                # 品牌名称
                n = " ".join([s["title"] for s in spans])
                yield scrapy.Request(
                    url="https:" + a["href"],
                    meta={
                        "brand_name": n,
                    },
                    callback=self.parse_list
                )
                # break
            # break

    def parse_list(self, response):
        """
        获取每个产品的产品列表
        :param response:
        :return:
        """
        soup = BeautifulSoup(response.text, "lxml")
        # 所有产品列表-页面链接
        all_pro = soup.find(class_="allPro")["href"]
        url_tail = all_pro.split("/")[-1].split("_")[0].replace("br", "")
        url = f"https://cosme.pclady.com.cn/products_list/{url_tail}/"
        meta = {
            "brand_name": response.meta["brand_name"],
            "logo": "https:" + soup.find(class_="proMode").find("img")["src"],  # logo图片链接
            "story": "https:" + soup.find(class_="typeMode").find("a", text="品牌故事")["href"],    # 品牌故事链接
            "index_url": response.url   # 品牌链接
        }
        yield scrapy.Request(url=url, meta=meta, callback=self.parse_product_list)

    def parse_product_list(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        count = soup.find(class_="dNub").find("em").text
        next_url = "https://cosme.pclady.com.cn/products_list/{}/p{}.html#productList"
        id = response.url.strip("/").split("/")[-1]
        for page in range(1, math.ceil(int(count) / 10) + 1):
            url = next_url.format(id, page)
            yield scrapy.Request(url=url, meta=response.meta, callback=self.parse_all_pro)
            # break

    def parse_all_pro(self, response):
        """
        获取单个产品的信息
        :param response:
        :return:
        """
        soup = BeautifulSoup(response.text, "lxml")
        product_list = soup.find(class_="dList").find("ul").find_all("li")
        brand_name = response.meta["brand_name"]
        logo = response.meta["logo"]
        story = response.meta["story"]
        index_url = response.meta["index_url"]
        for p in product_list:
            title = p.find(class_="sTit").find("a").text
            href = "https:" + p.find(class_="sTit").find("a")["href"]
            tags = ",".join([a.text for a in p.find(class_="sKey").find_all("a")])
            pays = p.find(class_="sPay").text
            meta = {
                "brand_name": brand_name,   # 品牌名称
                "title": title,     # 产品名称
                "tags": tags,       # 产品标签
                "pays": pays,       # 价格-规格
                "logo": logo,       # logo图片
                "story": story,     # 品牌故事
                "index_url": index_url,     # 品牌主页
            }
            yield scrapy.Request(url=href, meta=meta, callback=self.parse_product)
            # break
        # next page

    def parse_product(self, response):
        """
        处理产品详情页面
        :param response:
        :return:
        """
        soup = BeautifulSoup(response.text, "lxml")
        # 产品图集
        photo_list = "https:" + soup.find(class_="mod_view_photos")["href"]
        yield scrapy.Request(url=photo_list, meta=response.meta, callback=self.parse_photo)

    def parse_photo(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        pics = soup.find(class_="pics").find_all("img")
        meta = response.meta
        meta["pics"] = ["https:"+p["src"] for p in pics]
        pic_list = soup.find_all(class_="linkImg")
        for pic in pic_list:
            href = "https:" + pic["href"]
            yield scrapy.Request(url=href, meta=meta, callback=self.parse_photo_list)

    def parse_photo_list(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        photos = soup.find(class_="overview").find_all("img")
        photos = [p["src"] for p in photos]
        meta = response.meta
        meta["pics"] += photos
        # print(json.dumps(meta, ensure_ascii=False, indent=4))
        yield scrapy.Request(url=meta["story"], callback=self.parse_story, meta=meta, dont_filter=True)

    def parse_story(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        meta = response.meta
        meta["story_text"] = soup.find(class_="topStory").text
        meta["brand_infos"] = soup.find(class_="topInfo").text
        item = CosmeItem()
        item["info_json"] = meta
        item["logo"] = [meta["logo"]]
        item["imgs"] = meta["pics"]
        yield item


if __name__ == '__main__':
    execute("scrapy crawl cosme".split())