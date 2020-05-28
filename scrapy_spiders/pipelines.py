# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request


class ScrapySpidersPipeline(object):
    def process_item(self, item, spider):
        return item


import json
import os


class JsonWriterPipeline(object):
    def process_item(self, item, spider):
        info_json = item["info_json"]
        file_name = "infos.json"
        FILE_STORE = "/Users/xudashuai/Downloads/cosmetics/" + f"{info_json['brand_name']}/{info_json['title']}/"
        path = os.path.join(FILE_STORE, file_name)
        if not os.path.exists(FILE_STORE):
            os.makedirs(FILE_STORE)
        with open(path, "a+", encoding="utf8") as f:
            line = json.dumps(info_json, indent=4, ensure_ascii=False)
            f.write(line)
        f.close()
        return item


class CosmeImagesPipeline(ImagesPipeline):
    # 重命名
    def file_path(self, request, response=None, info=None):
        image_guid = request.url.split("/")[-1] if request.meta["type"] == "img" else "logo.jpg"
        if request.meta["type"] == "img":
            return 'cosmetics/%s/%s/imgs/%s' % (
                request.meta["brand_name"],
                request.meta["title"],
                image_guid
            )
        else:
            return 'cosmetics/%s/%s' % (
                request.meta["brand_name"],
                image_guid
            )

    # 下载请求
    def get_media_requests(self, item, info):
        info_json = item["info_json"]
        if item["imgs"]:
            for image_url in item['imgs']:
                yield Request(
                    image_url,
                    meta={
                        "brand_name": info_json["brand_name"],
                        "title": info_json["title"],
                        "type": "img"
                    }
                )
        if item["logo"]:
            for image_url in item['logo']:
                yield Request(
                    image_url,
                    meta={
                        "brand_name": info_json["brand_name"],
                        "title": info_json["title"],
                        "type": "logo"
                    }
                )

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            # raise DropItem("Item contains no images")
            print("Item contains no images")
        return item