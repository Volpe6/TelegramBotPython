import scrapy
from scraper.items import NoticeItem

class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def __init__(self, *args, **kwargs):
        super(QuotesSpider).__init__(*args, **kwargs)
        # self.start_urls = [f'https://g1.globo.com/busca/?q=teste']
        self.qu = termo
    

    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f'quotes-{page}.html'
        yield NoticeItem(url=response.url, titulo='', conteudo='', autor='')
