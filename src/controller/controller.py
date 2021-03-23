from util.mensagem    import Mensagem
from util.conf        import Configuracao as conf

from scraper.spiders.quotes_spider import QuotesSpider  
from scraper.spiders.g1_spider     import G1Spider
from scraper.spiders.proxy_spider  import ProxySpider

from controller.contexto    import Contexto
from util.gerencia_arquivo  import GerenciaArquivo as gm
from scraper.manager_scrapy import Manager as ManagerScrapy
from pnl.manager_pnl        import Manager as ManagerPnl

import os.path
import json

from threading import Thread

import traceback

def load_middleware_config(contexto):
    def carrega_proxys():
        manager = ManagerScrapy(contexto)
        manager.add_spider(ProxySpider)
        manager.set_configuracao({
            'ITEM_PIPELINES' : {
                'scraper.pipelines.ProxyPipeline' : 300 
            }
        })
        manager.only_run_spiders()
        
    carrega_proxys()
    contexto.print_console(Controller.nome, 'carregamento do middleware finalizado')


class Controller:

    RODAPE = 'O g1 disponibiliza um sitema de checagem. Você pode conferí-lo aqui: https://g1.globo.com/fato-ou-fake/noticia/2018/07/30/g1-lanca-fato-ou-fake-novo-servico-de-checagem-de-conteudos-suspeitos.ghtml'

    nome = 'controller'

    __contexto       = None
    __manager_scrapy = None
    __manager_pnl    = None

    def __init__(self, b_evitar_ser_banido = False, use_model_analise=False, use_resumo_tf_idf=False, use_ambos_resumos=False):
        """
        o argumento 'b_evitar_ser_banido', deve ser usado quando se quer rotacionar proxies e
        user-agents. Usar isso faz com q a inicializacao fique mais lenta. Nao deve ser usado
        quando esta se mexendo com sites que vc tem q se autenticar, pois vc sera facilmente identificado
        como bot e pode ser banido

        'use_model_analise' default= True
        se marcado retorna o resulta do da analise do modelo, sem textos adicionais, 
        que informa se a noticia é
        verdadeira ou falsa e a confianca no rotulo

        'use_resumo_tf_idf' default= False
        Por padrao é usado a tecnica de resumo simples, a desvantagem dessa abordagem
        é que ela tende a fovorecer sentencas mais longas, em detrimento das sentencas mais 
        curtas, porem ela aparenta ser a melhor opção nos casos de textos mais curtos, que é
        a maioria dos casos nesse sistema.
        O tf-idf parece funcionar melhor em textos mais longos, por isso nesse sistema ele
        aparentou nao funcionar tao bem

        'use_ambos_resumos'=False
        caso queira q sejam processados os dois tipos de resumo.
        use ambos tem maior prioridade, se for marcado o "use_resumo_tf_idf" e "use_ambos_resumo",
        sera usado os dois resumos idependente se "use_resumo_tf_idf" for "false" ou "true"
        """
        self.__b_evitar_ser_banido = b_evitar_ser_banido
        self.__use_model_analise   = use_model_analise
        self.__use_resumo_tf_idf   = use_resumo_tf_idf
        self.__use_ambos           = use_ambos_resumos
        if not b_evitar_ser_banido:
            return
        self.__proxy_inicializado = False
        self._print_console('middleware e outras coisas sendo ativado')
        self._reset_proxy_file()
        self._load_config_middleware()

    #Metodos publicos
    def set_contexto(self, ctx):
        self.__contexto = ctx
    
    def add_update(self, update):
        self.get_contexto().set_update(update)
    
    def get_update(self):
        return self.get_contexto().get_update()

    def define_texto_analise(self, texto):
        self.get_contexto().set_texto_analise(texto)

    def get_contexto(self):
        if self.__contexto is None:
            self.__contexto = Contexto()
        return self.__contexto
    
    def get_all_url_links(self):
        ctx   = self.get_contexto()
        links = []
        for notice in ctx.get_all_notices():
            links.append(notice['url'])
        return links

    def process(self):
        try:
            self._show_boas_vindas_msg()
            if not self._validate():
                return
            
            self._define_proxy_conf()

            self._bot_message('Analisando...')
            self._print_console('iniciando o processamento')

            self._extrair_informacao()
            self._process_manager_scrapy()
            self._analisa_noticia()

            self._print_console('finalizando o processamento')
            self._finaliza()
            self._print_console('scraping finalizado')
        except:
            self._bot_message(Mensagem.get_mensagem(401), True)
            self._print_console('houve um erro no metodo "process"')
            traceback.print_exc()
        
    #Metodos privados
    def _validate(self):
        return self._valida_quantidade_caracter()

    def _valida_quantidade_caracter(self):
        """
        verifica se a quantidade de caracteres corresponde ao que é esperado
        """
        qtd_texto_analise = len(self.get_contexto().get_texto_analise())
        self._print_console(f'quantidade de caracteres infomada: {qtd_texto_analise}')
        if qtd_texto_analise < 140:
            self._bot_message(Mensagem.get_mensagem(400, f' Quantidade mínima esperada 140. Quantidade informada: {qtd_texto_analise}'))
            return False
        
        if qtd_texto_analise > 500:
            self._bot_message(Mensagem.get_mensagem(400, f' Quantidade máxima esperada 500. Quantidade informada: {qtd_texto_analise}'))
            return False
        
        return True
        
    def _load_config_middleware(self):
        middleware_config = Thread(target=load_middleware_config, args=(self.get_contexto(),))
        middleware_config.start()

    def _define_proxy_conf(self):
        """
        deve ser chamado apos a lista de proxy ja existir
        """
        if not self.__b_evitar_ser_banido or self.__proxy_inicializado:
            #self.__b_evitar_ser_banido para caso nao se deseje utilizar as conf de mid
            #self.__proxy_inicializado se essas conf ja foram carregadas nao precisam carregar
            #de novo
            return

        data = gm.abir_arquivo_json(conf.ARQ_PROXY)
        #verifica se tem algum proxy
        if len(data) == 0:
            return

        self.__proxy_inicializado = True
        self._print_console('definindo a configuracao de proxy')
        manager = self._get_manager_scrapy()
        
        #adiciona a lista de proxies para rotacao
        manager.get_configuracao().get_dict_middleware_useragent_proxy_settings()['ROTATING_PROXY_LIST'] = data
        manager.set_configuracao(
            manager.get_configuracao().get_dict_middleware_useragent_proxy_settings()
        )
        self._print_console('definicao de proxy finalizada')

    def _extrair_informacao(self):
        contexto = self.get_contexto()
        self._print_console('iniciando extração de informação')
        fatos_noticias = self._get_manager_pnl().extrair_fatos(contexto.get_texto_analise())
        contexto.set_termo_busca(fatos_noticias)
        self._print_console('finalizando extração de informação')

    def _analisa_noticia(self):
        self._print_console('iniciando analise da noticia')
        contexto  = self.get_contexto()
        resultado = self._get_manager_pnl().analisa_noticia()
        contexto.set_resultado(resultado)
        self._print_console('finalizando analise da noticia')

    def _process_manager_scrapy(self):
        self._reset_data_file()
        manager = self._get_manager_scrapy()
        # manager.add_spider(QuotesSpider)
        manager.add_spider(G1Spider)
        manager.process()

    def _get_manager_scrapy(self):
        if self.__manager_scrapy is None:
            self.__manager_scrapy = ManagerScrapy(self.get_contexto())
        return self.__manager_scrapy
    
    def _get_manager_pnl(self):
        if self.__manager_pnl is None:
            self.__manager_pnl = ManagerPnl(self.get_contexto(), use_model_analise=self.__use_model_analise, use_resumo_tf_idf=self.__use_resumo_tf_idf, use_ambos_resumos=self.__use_ambos)
        return self.__manager_pnl
    
    def _reset_json_file(self):
        self._reset_data_file()
        self._reset_json_file()
    
    def _reset_proxy_file(self):
        gm.salva_arquivo_json(conf.ARQ_PROXY, [])

    def _reset_data_file(self):
        gm.salva_arquivo_json(conf.ARQ_DATA, [])

    def _finaliza(self):
        resultado = self.get_contexto().get_resultado()
        if len(resultado['url']) == 0:
            self._sem_url()
            return
        
        if self.__use_model_analise:
            self._show_modelo_analise_resultado()
            return 
        
        self._show_msg_padrao()
    
    #mensagens a serem apresentadas ao usuario
    def _sem_url(self):
        resultado = self.get_contexto().get_resultado()
        txt = 'Não foram encontradas notícias similares. Pesquise em fontes confiáveis.'
        txt += Controller.RODAPE
        self._bot_message(txt)
            
    def _show_modelo_analise_resultado(self):
        resultado = self.get_contexto().get_resultado()
        txt = ''
        for key, modelo in resultado['label'].items():
            txt += f'Modelo {key}\n'
            txt += 'Rótulo:{}\n'.format(modelo['label'])
            txt += 'Confianca:{:.2f}\n'.format(modelo['confianca'])

        self._bot_message(txt)
    
    def _show_msg_padrao(self):
        resultado = self.get_contexto().get_resultado()
 
        # txt = 'Não confie cegamente no que lhe é dito, verifique por si mesmo. Aqui há alguns links pelos quais você pode começar: \n'
        txt = 'Essas foram as notícias que eu encontrei, dê uma olhada:\n'

        for i, link in enumerate(resultado['url']):
            txt += '{}º - {}\n'.format((i + 1), link)

        txt += Controller.RODAPE

        self._bot_message(txt)

    def _get_final_msg(self, tipo):
        estrategia = {
            f'{ManagerPnl.LABEL_INCONCLUSIVO}': lambda resu : self._msg_inconclusivo(resu),
            f'{ManagerPnl.LABEL_FALSO}': lambda resu : self._msg_falso(resu),
            f'{ManagerPnl.LABEL_VERDADEIRO}' : lambda resu : self._msg_verdadeiro(resu)
        }
        return estrategia[str(tipo)]

    def _msg_verdadeiro(self, resultado):
        label = resultado['label']
        txt = 'Rótulo da noticia: {}\n'.format(label['label'])
        txt += 'Confiança no rótulo: {:.2f}%\n'.format(label['confianca'])

        txt += 'Não confie cegamente no que lhe é dito, verifique por si mesmo. Aqui há alguns links pelos quais você pode começar: \n'

        for i, link in enumerate(resultado['url']):
            txt += '{}º - {}\n'.format((i + 1), link)

        txt += Controller.RODAPE
        
        return txt

    def _msg_falso(self, resultado):
        label = resultado['label']
        txt = 'Rótulo da noticia: {}\n'.format(label['label'])
        txt += 'Confiança no rótulo: {:.2f}\n%'.format(label['confianca'])

        txt += 'Não confie cegamente no que lhe é dito, verifique por si mesmo. Aqui há alguns links pelos quais você pode começar: \n'

        for i, link in enumerate(resultado['url']):
            txt += '{}º - {}\n'.format((i + 1), link)
        
        txt += Controller.RODAPE

        return txt

    def _msg_inconclusivo(self, resultado):
        label = resultado['label']
        txt = 'Rótulo da noticia: {}\n'.format(label['label'])

        txt += 'Verifique por si mesmo. Aqui há alguns links pelos quais você pode começar: \n'

        for i, link in enumerate(resultado['url']):
            txt += '{}º - {}\n'.format((i + 1), link)
        
        txt += Controller.RODAPE

        return txt

    def _show_boas_vindas_msg(self):
        user_name = self.get_contexto().get_user_name()
        txt = f'Olá {user_name}!! Analisarei a notícia que me informou'
        self._bot_message(txt)
    
    def _bot_message(self, msg, edit_message=False):
        self.get_contexto().bot_message(msg, edit_message)

    def _print_console(self, msg):
        Contexto.print_console(self.nome, msg)

    
