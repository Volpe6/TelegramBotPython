from scrapy.utils.project import get_project_settings  

class Configuracao:
    #arquivo onde sao salvos os proxies para fazer a rotacao de proxies
    ARQ_PROXY = 'proxy.json'
    #arquivo onde sao salvos os dados recuperados pelas spiders
    ARQ_DATA  = 'data.json' 
    #quantidade maxima de proxies a utilizar
    PROXYS = 10

    __dict_middleware_useragent_proxy_setting = {
        #pesquisar mais sobre essa parte
        'DOWNLOADER_MIDDLEWARES' : {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
            'rotating_proxies.middlewares.RotatingProxyMiddleware': 610
        },
        #os user agentes a serem rotacionados, na hora de enviar o cabecalho,
        #para evitar que a conexao do bot seja negada
        'USER_AGENTS' :  [
            ('Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/57.0.2987.110 '
            'Safari/537.36'),  # chrome
            ('Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/61.0.3163.79 '
            'Safari/537.36'),  # chrome
            ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) '
            'Gecko/20100101 '
            'Firefox/55.0')  # firefox
        ],
    }
    
    __dict_default_settings = {
        'ITEM_PIPELINES' : {
            'scraper.pipelines.NoticiaPipeline' : 300 
        },
        'COOKIES_ENABLED': False,
        'DOWNLOAD_DELAY' : 2       
    }
    __settings = None

    def __init__(self):
        self._conf_padrao()
    
    #Metodos publicos
    def sobreescreve_configuracao(self, conf):
        for key, value in conf.items():
            self.__settings[key] = value    
    
    def get_project_settings(self):
        return self.__settings

    def get_dict_middleware_useragent_proxy_settings(self):
        return self.__dict_middleware_useragent_proxy_setting
        
    #Metodos privados
    def _conf_padrao(self):
        default_settings = get_project_settings()
        for key, value in self.__dict_default_settings.items():
            default_settings[key] = value
        self.__settings = default_settings
    