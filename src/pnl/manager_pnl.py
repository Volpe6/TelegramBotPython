from pnl.sumarizador.resumo import SumarizadorPorRanking
from pnl.sumarizador.pipeline import Pipeline
from heapq import nlargest
from collections import Counter, OrderedDict, defaultdict
import pnl.texto_pnl as texto_pnl
import fasttext
import ftfy
from controller.contexto import Contexto
from util.mensagem import Mensagem

#fontes https://medium.com/@everton.tomalok/criando-seu-sumarizador-autom%C3%A1tico-de-textos-part-i-390744715744
#fontes https://github.com/EvertonTomalok/reader_rss/blob/1f7ee44825d6668d5cf438dd9b53352cc17a0ebd/controles/__init__.py#L28
#fontes https://medium.com/@viniljf/utilizando-processamento-de-linguagem-natural-para-criar-um-sumariza%C3%A7%C3%A3o-autom%C3%A1tica-de-textos-775cb428c84e

class Manager:
    LABEL_INCONCLUSIVO = 1
    LABEL_FALSO        = 2
    LABEL_VERDADEIRO   = 3
    #o minimo de similaridade que eu quero a noticia informado pelo usuario, tenha com a noticia recuperada
    TEXTO_SIMILARIDADE = 0.38

    nome = 'manager_pnl'

    def __init__(self, contexto = None, use_model_analise=True, use_resumo_tf_idf=False, use_ambos_resumos=False):
        """
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
        self.__use_model_analise = use_model_analise
        self.__use_resumo_tf_idf = use_resumo_tf_idf
        self.__use_ambos         = use_ambos_resumos

        self.__sumarizador = SumarizadorPorRanking()
        self.__contexto = contexto
        self.__texto    = None
        self.__modelo_analise = None
        if not self.__use_model_analise:
            return
        self._load_models()
    
    #Metodos publicos
    def load_model(self, model_path):
        """
        carrega o modelo informado
        
        "model_path": caminho onde se encontra o modelo a ser carregado
        """
        if not self.__use_model_analise:
            raise Exception(Mensagem.get_mensagem(501))
        self.__modelo_analise = fasttext.load_model(model_path)

    def set_contexto(self, ctx):
        self.__contexto = ctx

    def set_texto(self, texto):
        self.__texto = texto
    
    def get_texto(self):
        return self.__texto
    
    def extrair_fatos(self, texto):
        self._print_console('extraindo informações')
        self._bot_message('...')
        return self._extracao_simples(texto)
        
    def analisa_noticia(self):
        """
        Noticias resumidas utilizando o metodo simples aparentam ser melhores, ja que os textos
        nao sao tao grandes
        """
        self._print_console('analisando noticia')
        noticias_resu      = self._get_noticias_resumidas()
        noticias_similares = self._get_noticias_similares(noticias_resu)
        self._print_console('finalizando analise noticia')
        return self._analisa_texto(noticias_similares)
        
    #Metodos privados
    def _load_models(self):
        self.modelo_resumo_simples = fasttext.load_model('assets/model_fasttext/modelo_resumo_simples_30_por')
        #modelo de resumo simples com daset normalizado fornecido pelo corpus usado
        #tudo q tem norm segue a mesmo logica
        self.modelo_resumo_simples_norm = fasttext.load_model('assets/model_fasttext/modelo_resumo_simples_30_por_norm')
        
        self.modelo_resumo_tf_idf = fasttext.load_model('assets/model_fasttext/modelo_resumo_tf_idf_30_por')
        self.modelo_resumo_tf_idf_norm = fasttext.load_model('assets/model_fasttext/modelo_resumo_tf_idf_30_por_norm')

        self.modelo_texto_completo = fasttext.load_model('assets/model_fasttext/modelo_texto_completo_30_por')
        self.modelo_texto_completo_norm = fasttext.load_model('assets/model_fasttext/modelo_texto_completo_30_por_norm')

    def _get_contexto(self):
        return self.__contexto

    def _get_sumarizador(self):
        return self.__sumarizador

    def _get_noticias_resumidas(self):
        """
        resume os textos para que fiquem com um tamanho similar ao da noticia a ser analisada
        """
        self._print_console('resumindo noticias')
        self._bot_message('...')

        pipeline        = Pipeline()
        noticia_analise = self._get_contexto().get_texto_analise()
        sumarizador     = self._get_sumarizador()
        
        sumarizador.set_qtd_sent_resumo(len(pipeline.sent_tokenize(noticia_analise)))
        
        noticias_resumidas = []
        for item in self._get_contexto().get_all_notices():
            noticia = {}
            noticia.update(item)

            if self.__use_ambos:
                resumo_tf_idf, resumo_simples = sumarizador.resumir(item['conteudo'], use_ambos=True)
                noticia['conteudo_resumido_tf_idf']  = resumo_tf_idf
                noticia['conteudo_resumido_simples'] = resumo_simples
                noticia['conteudo'] = item['conteudo']
                noticias_resumidas.append(noticia)
                continue

            if self.__use_resumo_tf_idf:
                noticia['conteudo_resumido'] = sumarizador.resumir(item['conteudo'], use_tf_idf=True)
                noticia['conteudo'] = item['conteudo']
                noticias_resumidas.append(noticia)
                continue
            
            noticia['conteudo_resumido'] = sumarizador.resumir(item['conteudo'])
            noticia['conteudo'] = item['conteudo']
            noticias_resumidas.append(noticia)
                
        
        return noticias_resumidas

    def _get_noticias_similares(self, noticias_resumidas):
        """
        obtendo as noticias mais similares
        """
        self._print_console('obtendo noticias similares')
        self._bot_message('...')

        noticia_analise = self._get_contexto().get_texto_analise()

        noticias_similares = []
        for noticia in noticias_resumidas:
            resumo_similaridade = 0
            if self.__use_ambos:
                #se é para usar os dois, verifica a similaridade com ambos os resumos, e pega aquele com maior similaridade

                resumo_simples = texto_pnl.verifica_similaridade(noticia_analise, noticia['conteudo_resumido_simples'])
                resumo_tf_idf  = texto_pnl.verifica_similaridade(noticia_analise, noticia['conteudo_resumido_tf_idf'])
                #pega o resumo com a maior similaridade
                resumo_similaridade = resumo_simples if resumo_simples > resumo_tf_idf else resumo_tf_idf
            else:
                resumo_similaridade = texto_pnl.verifica_similaridade(noticia_analise, noticia['conteudo_resumido'])

            if(resumo_similaridade < Manager.TEXTO_SIMILARIDADE):
                continue
            noticias_similares.append(noticia)
        return noticias_similares
        

    def _analisa_texto(self, noticias_similares):
        """
        verifica se o texto informado pelo usuario é verdadeiro ou falso.
        retorna um boolean indicando se a noticia é verdadeira ou falsa
        """
        self._print_console('analisando o texto informado pelo usuario')
        self._bot_message('...')

        resultado = {}

        noticia_analise = self._get_contexto().get_texto_analise()
        noticia_analise = ftfy.fix_text(noticia_analise)
        noticia_analise = noticia_analise.replace('\n', ' ')
        noticia_analise = noticia_analise.lower()

        def get_label(lbl_analise):
            if lbl_analise == '__label__true':
                return 'verdadeiro'
            return 'falso'
        
        def get_codigo_label(lbl_analise):
            if lbl_analise == '__label__true':
                return Manager.LABEL_VERDADEIRO
            return Manager.LABEL_FALSO
        
        if self.__use_model_analise:
            modelos = self._analisar(noticia_analise)

            lbl = {}
            for key, modelo in modelos.items():
                lbl[key] = {
                    'cod': get_codigo_label(modelo[0]),
                    'label': get_label(modelo[0]),
                    'confianca': modelo[1]*100    
                }
            resultado['label'] = lbl


        url_noticia_similar = []
        for noticias in noticias_similares:
            if noticias['url'] not in url_noticia_similar:
                url_noticia_similar.append(noticias['url'])


        resultado['url'] = url_noticia_similar

        return resultado


    def _analisar(self, noticia):
        modelos = {}
        if self.__modelo_analise is not None:
            lbl, conf = self.__modelo_analise.predict(noticia)
            modelos['modelo'] = (lbl, conf[0])
            return modelos

        #resumo simples 
        lbl1, conf1 = self.modelo_resumo_simples.predict(noticia)
        #resumo simples com o dataset norm
        lbl2, conf2 = self.modelo_resumo_simples_norm.predict(noticia)
        #resumo tf-idf
        lbl3, conf3 = self.modelo_resumo_tf_idf.predict(noticia)
        #resumo tf-idf norm
        lbl4, conf4 = self.modelo_resumo_tf_idf_norm.predict(noticia)
        #noticia completa
        lbl5, conf5 = self.modelo_texto_completo.predict(noticia)
        #noticia completa norm 
        lbl6, conf6 = self.modelo_texto_completo_norm.predict(noticia)
        
        modelos['modelo_resu_simples'] = (lbl1, conf1[0])
        modelos['modelo_resu_simples_norm'] = (lbl2, conf2[0])
        modelos['modelo_resumo_tf_idf'] = (lbl3, conf3[0])
        modelos['modelo_resumo_tf_idf_norm'] = (lbl4, conf4[0])
        modelos['modelo_txt_completo'] = (lbl5, conf5[0])
        modelos['modelo_txt_completo_norm'] = (lbl6, conf6[0])

        return modelos

    def _get_update(self):
        return self._get_contexto().get_update()
    
    def _extracao_com_tf_idf(self, texto):
        """
        usa a tecnica tf-idf. Dependendo do tamanho do texto pode ter um processamento lento.
        Aparenta mostrar uma desvantagem quando o texto informado é muito pequeno.
        Sendo mais viavel a utilizacao da extracao_simples. Quando o texto é muito pequeno, 
        aparenta dar um peso maior as sentencas menores, que nao necessariamente é
        a sentenca mais importante
        """
        pipeline = Pipeline()
        pipeline.set_texto(texto)
        txt = pipeline.process_tf_idx()
        
        ranking   = txt.ranking
        sentencas = txt.sentencas

        stops = pipeline.get_stop_words()

        idx_sentencas_importantes = nlargest(1, ranking, key=ranking.get)
        #aqui eu pego a sentenca mais importante, de acordo com meu sistema de rankeamento
        #que utiliza o tf-idf
        sentenca_mais_importante  = sentencas[idx_sentencas_importantes[0]]
        #aqui eu pego todas as palavras da sentenca mais importante
        sent_imp_palavras = pipeline.tokenize(sentenca_mais_importante)
        #aqui eu removo as palavras de parada
        sent_imp_palavras = [plvr for plvr in sent_imp_palavras if plvr not in stops]

        #aqui eu pego as tag associadas as palavras
        tag_token = pipeline.tag(sent_imp_palavras)
        entidades_nomeadas = []#esse é o array onde eu vou colocar as palavras identificadas como "N" ou "NPROP"
        for token, tag in tag_token:
            #aqui eu pego as palavras que possouem a tag de nome proprio
            if tag == 'N' or tag == 'NPROP':
                entidades_nomeadas.append(token)
        
        txt_final = ' '.join(entidades_nomeadas[:6])
        self._print_console('finalizando extração de informacao')
        self._bot_message('...')
        return txt_final

    def _extracao_simples(self, texto):
        """
        usa um sistema mais simples de seleção da sentenca mais importante, onde ele conta
        a frequencia de uma palavra no texto, essa frequencia entao se torna a pontuação da palavra, onde
        a pontuação da sentenca é a soma das pontuações de suas palavras, é bem rapido. Esse sistema 
        tem uma desvantagem, ele tende a favorecer sentencas mais longas, ou seja aquelas que contem mais 
        palavras
        """
        pipeline = Pipeline()
        
        txt       = texto#texto forneceido pelo usuario
        stops     = pipeline.get_stop_words()
        sentencas = pipeline.sent_tokenize(txt)
        palavras  = pipeline.tokenize(txt.lower()) 
        #remove stop words as palavras
        palavras_sem_stops  = [plvr for plvr in palavras if plvr not in stops]
        frequencia          = pipeline.get_dict_ocorrencia_palavras(palavras_sem_stops)

        #################################
        #sentencas importantes
        ranking = defaultdict(int)
        #ranqueia as sentenças
        for i, sentenca in enumerate(sentencas):
            for palavra in pipeline.tokenize(sentenca.lower()):
                if palavra in frequencia:
                    ranking[i] += frequencia[palavra] 

        idx_sentencas_importantes = nlargest(1, ranking, key=ranking.get)
        #aqui eu pego a sentenca mais importante, de acordo com meu sistema de rankeamento
        sentenca_mais_importante  = sentencas[idx_sentencas_importantes[0]]
        #aqui eu pego todas as palavras da sntenca mais importante
        sent_imp_palavras = pipeline.tokenize(sentenca_mais_importante)
        #aqui eu removo as palavras de parada
        sent_imp_palavras = [plvr for plvr in sent_imp_palavras if plvr not in stops]

        #aqui eu pego as tag associadas as palavras
        tag_token = pipeline.tag(sent_imp_palavras)
        entidades_nomeadas = []#esse é o array onde eu vou colocar as palavras identificadas como "N" ou "NPROP"
        for token, tag in tag_token:
            #aqui eu pego as palavras que possouem a tag de nome proprio
            if tag == 'N' or tag == 'NPROP':
                entidades_nomeadas.append(token)
        
        txt_final = ' '.join(entidades_nomeadas[:6])
        self._print_console('finalizando extração de informacao')
        self._bot_message('...')
        return txt_final
    
    def _print_console(self, msg):
        Contexto.print_console(self.nome, msg)
    
    def _bot_message(self, msg):
        self._get_contexto().bot_message(msg)

 




"""
foram pesquisadas outras abordagens de extracao de informação porem devido a complexidade
foi adotada uma abordagem mais simples.
sumaraizador automatico
avaliar similaridade de strings
sklear vs outro
"""