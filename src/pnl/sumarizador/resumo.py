from heapq import nlargest
import re
# import networkx as nx
import math
from pnl.sumarizador.pipeline import Pipeline

class Sumarizador:

    __qtd_sent_resumo = None

    def __init__(self):
        self.pipeline = Pipeline()

    #metodos publicos
    def resumir(self, texto):
        pass

    def set_qtd_sent_resumo(self, qtd):
        self.__qtd_sent_resumo = qtd

    #metodos privados
    def _get_num_sentencas_resumo(self, num_sent):
        """
        retorna o numero de sentencas que o resumo deve possuir, com base
        no total de sentencas informado
        """
        if self.__qtd_sent_resumo is not None:
            return self.__qtd_sent_resumo
        return 2 if 2 < num_sent < 5 else 3

class SumarizadorPorRanking(Sumarizador):
    
    #metodos publicos 
    def resumir(self, texto, use_tf_idf=False, use_ambos=False ):   
        """
        use_tf_idf=False
        caso se deseje usar o resumo com tf-idf

        use_ambos=False
        caso queira q sejam retornado os dois tipos de resumo
        """
        # qtd_sent = len(self.pipeline.sent_tokenize(texto))#quantidades de sentencas no texto

        # if qtd_sent <= 2:
        #     return texto

        self.pipeline.set_texto(texto)

        #utilizar extracoes mais simples aparenta funcionar melhor com textos menores,
        #enquanto a abordagem que utiliza o tf-idf, funcionou melhor com textos grandes.
        if use_ambos:
            return self._get_resumo_tf_idf(), self._get_resumo_simples()

        if use_tf_idf:
            return self._get_resumo_tf_idf()

        return self._get_resumo_simples()
    
    def _get_resumo_tf_idf(self):
        oTexto = self.pipeline.process_tf_idx()

        sentencas = oTexto.sentencas
        ranking   = oTexto.ranking

        qtd_sent_resu = self._get_num_sentencas_resumo(len(sentencas))

        idx_sentencas_importantes = nlargest(qtd_sent_resu, ranking, key=ranking.get)
        resumo = " ".join(
            [sentencas[i] for i in sorted(idx_sentencas_importantes)]
        )

        return resumo

    def _get_resumo_simples(self):
        oTexto = self.pipeline.process()
        
        sentencas = oTexto.sentencas
        ranking   = oTexto.ranking

        qtd_sent_resu = self._get_num_sentencas_resumo(len(sentencas))

        idx_sentencas_importantes = nlargest(qtd_sent_resu, ranking, key=ranking.get)
        resumo = " ".join(
            [sentencas[i] for i in sorted(idx_sentencas_importantes)]
        )
        return resumo

# class SumarizadorPorGrafo(Sumarizador):
#     __sentencas = None
#     __grafo     = None

#     #metodos publicos
#     def execute(self, param=None):
#         return self.resumir(param)
    
#     def resumir(self, texto):
#         """
#         Aqui a gente extrai as frases com maior pontuação.
#         O tamanho do resumo será 20% do número de frases original
#         """
#         self.pipeline.set_texto(texto)
#         self._carrega_dados()
#         sentencass = self.pipeline.sent_tokenize(texto)
        
#         qtd_sent_resu = self._get_num_sentencas_resumo(len(sentencass))
#         # ordenando as frases de acordo com a pontuação
#         # e extraindo a quantidade desejada.
#         sentencas = sorted(sentencass, key=lambda s: s.get_pontuacao(), reverse=True)[:qtd_sent_resu]

#         # ordenando as sentenças de acordo com a ordem no texto
#         # original.
#         ordenadas = sorted(sentencas, key=lambda s: sentencass.index(s))

#         return ' '.join([sentenca.get_sentenca() for sentenca in ordenadas])
  
#     #metodos privados
#     def _carrega_dados(self):
#         self._get_sentencas()
#         self._get_grafo()

#     def _get_num_sentencas_resumo(self, num_sent):
#         """
#         Aqui a gente extrai as frases com maior pontuação.
#         O tamanho do resumo será 20% do número de frases original
#         """
#         return int(num_sent * 0.2) or 1

#     def _get_sentencas(self):
#         if self.__sentencas is None:
#             preprocess = self._get_preprocessamento()
#             self.__sentencas = preprocess.quebra_sentencas()
#             self.__sentencas = [Sentenca(preprocess.get_texto(), sent, preprocess) for sent in self.__sentencas]
#         return self.__sentencas

#     def _get_grafo(self):
#         if self.__grafo is not None:
#             return self.__grafo
        
#         grafo = nx.Graph()
#         # Aqui é o primeiro passo descrito acima. Estamos criando os
#         # nós com as unidades de texto relevantes, no nosso caso as
#         # sentenças.
#         for sentenca in self._get_sentencas():
#             grafo.add_node(sentenca)
#         # Aqui é o segundo passo. Criamos as arestas do grafo
#         # baseadas nas relações entre as unidades de texto, no nosso caso
#         # é a semelhança entre sentenças.
#         for node in grafo.nodes():
#             for n in grafo.nodes():
#                 if node == n:
#                     continue
#                 semelhanca = self._calcula_similaridade(node, n)
#                 if semelhanca:
#                     grafo.add_edge(node, n, weight=semelhanca)
        
#         for sentenca in self._get_sentencas():
#             sentenca.set_grafo(grafo)

#         self.__grafo = grafo
#         return self.__grafo

#     def _calcula_similaridade(self, sentenca1, sentenca2):
#         """
#         Implementação da fórmula de semelhança entre duas sentenças.
#         """
#         plvr1, plvr2 = set(sentenca1.get_palavras()), set(sentenca2.get_palavras())
#         # Aqui a gente vê quantas palavras que estão nas frases se
#         # repetem.
#         repeticao = len(plvr1.intersection(plvr2))
#         # Aqui a normalização.
#         semelhanca = repeticao / (math.log(len(plvr1)) + math.log(len(plvr2)))
#         return semelhanca

# class Sentenca:

#     def __init__(self, texto_completo, sentenca, preprocess=None, grafo=None):
#         self.preprocess  = preprocess
#         self.grafo       = grafo
#         self.__texto     = texto_completo
#         self.__sentenca  = sentenca
#         self.__palavras  = None
#         self.__pontuacao = None

#     def __hash__(self):
#         """
#         Esse hash aqui é pra funcionar como nó no grafo.
#         Os nós do NetworkX tem que ser 'hasheáveis'
#         """
#         return hash(self.__sentenca)
    
#     #metodos publicos
#     def get_sentenca(self):
#         return self.__sentenca

#     def set_preprocessamento(self, preprocess):
#         self.preprocess = preprocess
    
#     def get_preprocessamento(self):
#         return self.preprocess
    
#     def set_grafo(self, grafo):
#         self.grafo = grafo
    
#     def get_grafo(self):
#         return self.grafo

#     def get_palavras(self):
#         """
#         Quebrando as sentenças em palavras. As palavras
#         da sentença serão usadas para calcular a semelhança.
#         """
#         if self.__palavras is None:
#             self._palavras = self.preprocess.custom_tokenize(self.__sentenca)
#         return self._palavras
    
#     def get_pontuacao(self):
#         """
#         Implementação do algorítimo simplificado para pontuação
#         dos nós do grafo.
#         """
#         if self.__pontuacao is None:
#             # aqui a gente simplesmente soma o peso das arestas
#             # relacionadas a este nó.
#             pontuacao = 0.0
#             for n in self.grafo.neighbors(self):
#                 pontuacao += self.grafo.get_edge_data(self, n)['weight']
#             self.__pontuacao = pontuacao
        
#         return self.__pontuacao