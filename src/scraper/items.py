# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ProxyItem(scrapy.Item):
    proxys = scrapy.Field()
    
class NoticeItem(scrapy.Item):
    url      = scrapy.Field()
    titulo   = scrapy.Field()
    conteudo = scrapy.Field()
    autor    = scrapy.Field()

class ScraperItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
