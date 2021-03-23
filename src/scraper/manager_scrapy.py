from multiprocessing import Process, Queue, Pipe
from scrapy.crawler  import CrawlerProcess

from util.conf import Configuracao
from util.gerencia_arquivo import GerenciaArquivo as gm
import json

from threading import Thread
import time
import random

from controller.contexto import Contexto

def notifica(contexto):
    while continuar_notificacao:
        qtd_pontos = random.randint(1, 3)
        txt = 'Buscando noticias similares'
        for i in range(qtd_pontos):
           txt += '.' 

        contexto.bot_message(txt, True)

        time.sleep(0.02)

    contexto.bot_message('Busca finalizada...', True)


def execute_spider(queue, *args):
    try:
        process = CrawlerProcess(args[0])
        spiders = args[1]
        for spider in spiders:
            process.crawl(spider, args[2])
        process.start()
        queue.put(None)
    except Exception as e:
        queue.put(e)

class Manager:
    nome = 'manager_scrapy'

    __contexto     = None
    __spiders      = None
    __configuracao = None

    def __init__(self, contexto = None):
        self.__spiders      = []
        self.__contexto     = contexto
        self.__configuracao = Configuracao()
    
    #Metodos publicos
    def set_contexto(self, ctx):
        self.__contexto = ctx

    def add_spider(self, spider):
        self._print_console('adicionando spider')
        self.__spiders.append(spider)

    def remove_spider(self, spider):
        self._print_console('removendo spider')
        self.__spiders.remove(spider)
    
    def set_configuracao(self, conf):
        self._print_console('setando configuração')
        self.get_configuracao().sobreescreve_configuracao(conf)

    def get_configuracao(self):
        return self.__configuracao

    def only_run_spiders(self):
        """
        apenas executa os spiders sem fazer mais nada
        """
        self._run_spiders()

    def process(self):
        self._bot_message('...')
        self._print_console('iniciando scraping')
        self._run_spiders_notification()
        self._print_console('finalizando scraping')
        self._add_contexto()
        self._print_console('scraping finalizado')

    #Metodos privados
    def _get_contexto(self):
        return self.__contexto
    
    def _add_contexto(self):
        self._print_console('adicionando o conteudo recuperado ao contexto')
        ctx = self._get_contexto()
        if not gm.existe_diretorio(Configuracao.ARQ_DATA):
            return
        data = gm.abir_arquivo_json(Configuracao.ARQ_DATA)
        ctx.set_notices(data)
        ctx.set_configuracao(self.get_configuracao())

    def _run_spiders_notification(self):
        """
        executa os spiders com a thread de notificacao
        """
        self._bot_message('...')
        global continuar_notificacao
        continuar_notificacao = True
        notificacao = Thread(target=notifica, args=(self._get_contexto(),))
        notificacao.start()

        queue   = Queue()
        process = Process(target=execute_spider, args=(
            queue,
            self.get_configuracao().get_project_settings(),
            self.__spiders,
            self._get_contexto().get_termo_busca()
        ))
        process.start()
        result = queue.get()

        continuar_notificacao = False
        notificacao.join()
        process.join()

        if result is not None:
            raise result


    def _run_spiders(self, use_thred_notificacao=True):
        self._bot_message('...')
        queue   = Queue()
        process = Process(target=execute_spider, args=(
            queue,
            self.get_configuracao().get_project_settings(),
            self.__spiders,
            self._get_contexto().get_termo_busca()
        ))
        process.start()
        result = queue.get()

        process.join()

        if result is not None:
            raise result
    
    def _print_console(self, msg):
        Contexto.print_console(self.nome, msg)

    def _bot_message(self, msg, edit_msg=False):
        self._get_contexto().bot_message(msg, edit_msg)
        