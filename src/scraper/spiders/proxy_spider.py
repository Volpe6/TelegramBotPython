import scrapy
import requests
from scraper.items import ProxyItem

from util.gerencia_arquivo import GerenciaArquivo as gm
from util.conf import Configuracao as conf
from controller.contexto import Contexto

def get_quantidade_proxies():
    data = gm.abir_arquivo_json(conf.ARQ_PROXY)
    return len(data)

class ProxySpider(scrapy.Spider):
    name = 'proxy_spider'
    start_urls = [
        'https://free-proxy-list.net/'
    ]

    def parse(self, response):

        if get_quantidade_proxies() > conf.PROXYS:
            return
        
        proxys = []
        for proxy in response.css('table tr'):
            proxys.append(proxy.css('td ::text').get())
        yield ProxyItem(proxys=self.get_proxys_ativos(proxys))

    def get_proxys_ativos(self, proxys):
        """
        testa a lista de proxy passada e retorna apenas os proxys ativos
        """
        #url utilizada para testar se um proxy esta ativo
        url = 'https://httpbin.org/ip'
        total_proxys = len(proxys)
        proxys_ativos = []
        for idx, proxy in enumerate(proxys):
            self._print_console(f'analisando {(idx+1)} de {total_proxys} proxys')
            try:
                response = requests.get(url,proxies={"http": proxy, "https": proxy}, timeout=3)
                # response = requests.get(url,proxies={"http": proxy, "https": proxy})
                proxys_ativos.append(proxy)
                self._print_console('{}'.format(response.json()))
                if len(proxys_ativos) > conf.PROXYS:
                    break
            except:
                self._print_console(f'este proxy não funcionou: {proxy}')
        return proxys_ativos
    
    def _print_console(self, msg):
        nome = 'proxy_spider'
        Contexto.print_console(nome, msg)
