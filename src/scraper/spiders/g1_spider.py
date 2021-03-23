import scrapy
from scraper.items import NoticeItem

class G1Spider(scrapy.Spider):
    name = 'G1'

    def __init__(self, *args, **kwargs):
        termo = args[0]
        self.start_urls = [f'https://g1.globo.com/busca/?q={termo}']
    
    def parse(self, response):
        ancoras = []
        for infoItem in response.css('.widget--info'):
            # se for video, provavelmente nao tera texto, ou tera pouco texto.
            # entao nao vale a pena visitar esses links
            if (infoItem.css('.widget--info__media--video').get() is not None):
                continue
            ancoras.append(infoItem.css('a::attr(href)').get())
        ancorass = []
        for ancora in ancoras:
            if ancora not in ancorass:
                ancorass.append(ancora)
        ancorass = ancorass[:5]
        yield from response.follow_all(ancorass, callback=self.parse_noticia)

    def parse_noticia(self, response):
        url_origin = response.url
        titulo     = response.css('.content-head__title ::text').get()

        txt = ''
        for text in response.css('article[itemprop=articleBody] p.content-text__container::text').getall():
            txt += text

        conteudo   = txt
        autor      = response.css('p.content-publication-data__from::attr(title)').get().split(',')[0]
        yield NoticeItem(url=url_origin, titulo=titulo, conteudo=conteudo, autor=autor)