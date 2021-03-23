# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from util.gerencia_arquivo import GerenciaArquivo as gm
from util.conf import Configuracao as conf

class ProxyPipeline:

    def save_json_file(self, content = []): 
        #verifica se nao o existe
        if not gm.existe_diretorio(conf.ARQ_PROXY):
            #se o arquivo nao existe apenas o cria e salva o conteudo passado
            gm.salva_arquivo_json(conf.ARQ_PROXY, content)
            return 
        
        #carrega o conteudo q tem no arquivo
        data = gm.abir_arquivo_json(conf.ARQ_PROXY)
        #adiciona o novo conteudo ao conteudo que existia no arquivo
        json_data = data
        for item in content:
            json_data.append(item)
        gm.salva_arquivo_json(conf.ARQ_PROXY, json_data)
    

    def process_item(self, item, spider):
        proxys = []
        for proxy in item['proxys']:
            if proxy is None:
                continue
            proxys.append(proxy)
        self.save_json_file(proxys)
        return item

class NoticiaPipeline:

    def save_json_file(self, content = []): 
        #verifica se nao o existe
        if not gm.existe_diretorio(conf.ARQ_DATA):
            #se o arquivo nao existe apenas o cria e salva o conteudo passado
            gm.salva_arquivo_json(conf.ARQ_DATA, content)
        
        #carrega o conteudo q tem no arquivo
        data = gm.abir_arquivo_json(conf.ARQ_DATA)
        #adiciona o novo conteudo ao conteudo que existia no arquivo
        json_data = data
        for item in self.list_notice:
            json_data.append(item)
        gm.salva_arquivo_json(conf.ARQ_DATA, json_data)

    def open_spider(self, spider):
        self.list_notice = []

    def close_spider(self, spider):
        self.save_json_file(self.list_notice)
    
    def process_item(self, item, spider):
        self.list_notice.append({
            'url'     : item['url'],
            'titulo'  : item['titulo'],
            'conteudo': item['conteudo'],
            'autor'   : item['autor']
        })
        return item