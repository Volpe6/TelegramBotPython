# 

import nltk
import pickle
from string import punctuation
from collections import Counter, OrderedDict, defaultdict
import math
from heapq import nlargest
from sklearn.feature_extraction.text import TfidfVectorizer


#https://towardsdatascience.com/text-summarization-using-tf-idf-e64a0644ace3

class Pipeline:

    PICKLE_ARQ = 'assets/tagger-portugues/POS_tagger_brill.pkl'

    __texto      = None
    #palavras que nao agregam muito na informacao contida no texto
    __stop_words = None
    #pontuacao contida no texto que nao agregam muito na informacao contida no texto
    __pontuacao  = None 
    #pos tagger personalizado
    __tagger     = None
    __stemmer    = None

    def __init__(self):
        self.__stop_words = nltk.corpus.stopwords.words('portuguese')
        self.__pontuacao  = list(punctuation)
        self.__stemmer    = nltk.stem.RSLPStemmer()
        self._load_tagger()

    # metodos publicos
    def process(self):
        self._validate()
        txt = Texto()
        #PRE-PROCESS
        txt.texto = self.get_texto()
        stops     = self.get_stop_words()
        txt.sentencas = self.sent_tokenize(txt.texto)
        palavras  = self.tokenize(txt.texto.lower()) 
        #remove stop words
        palavras_sem_stops = [plvr for plvr in palavras if plvr not in stops]

        #PROCESS
        txt.frequencia = self.get_dict_ocorrencia_palavras(palavras_sem_stops)
        #sentencas importantes
        txt.ranking = self.get_simple_rank_sentence(txt.sentencas, txt.frequencia)

        return txt
    
    def process_tf_idx(self):
        self._validate()
        txt = Texto()
        #PRE-PROCESS
        txt.texto = self.get_texto()
        stops     = self.get_stop_words()
        txt.sentencas = self.sent_tokenize(txt.texto)

        sent_score, ranking = self._get_simple_ponto_sentenca_tf_idf(txt.sentencas)
        txt.sent_score = sent_score
        txt.ranking = ranking
        
        return txt


    def get_simple_rank_sentence(self, sentencas, frequencia):
        """
        faz um rankeamento simples das sentencas passadas, com base na frequencias das palavras passadas.
        retorna o ranking das sentencas

        a frequencia é um dicionario onde a chave é a palavra e o valor é a frequencia.
        as palavras dentro do dicionario de frequencia devem estar minusculas
        """
        ranking = defaultdict(int)
        #popular dicionario de score(nao é TF-IDF)
        for i, sentenca in enumerate(sentencas):
            for palavra in self.tokenize(sentenca.lower()):
                if palavra in frequencia:
                    ranking[i] += frequencia[palavra]
        return ranking

    def set_texto(self, texto):
        self.__texto = texto
    
    def get_texto(self):
        return self.__texto

    def get_stop_words(self):
        return self.__stop_words + self.__pontuacao
    
    def get_dict_ocorrencia_palavras(self, tokens):
        """
        retorna um dicionario contendo a palavra e a ocorrencia dela no texto
        """
        return nltk.probability.FreqDist(tokens)

    def tag(self, tokens):
        """
        retorna a tag associoada a cada tag
        """
        return self.__tagger.tag(tokens)

    def stemming_all_tokens(self, tokens):
        return [self.stem(token) for token in tokens]

    def stem(self, word):
        """
        reduz uma palavra a seu radical
        """
        return self.__stemmer.stem(word)

    def tokenize(self, texto):
        return nltk.word_tokenize(texto)
    
    def sent_tokenize(self, texto):
        return nltk.sent_tokenize(texto)

    # metodos privados
    def _load_tagger(self):
        with open(Pipeline.PICKLE_ARQ, 'rb') as pickle_file:
            self.__tagger = pickle.load(pickle_file)   
    
    def _validate(self):
        if self.get_texto() is None:
            raise Exception("Não foi informado um texto.")


    #tf-idf
    # def _tokenize_tf_idf(self, texto):
    #     """
    #     quebra o texto em sentencas, quebra as sentencas em palavras, e reduz
    #     as palavras a seu radical
    #     """
    #     if texto in self._get_stop_words_stemming():
    #         return
            
    #     tokens = []
    #     #coloca todas palavras do texto em um array
    #     for sentenca in self.sent_tokenize(texto):
    #         #quebra o texto em sentencas
    #         for plvr in self.tokenize(sentenca):
    #             #quebra a sentenca em palavras e poe dentro do array
    #             tokens.append(plvr)         
    #     #recupera apenas o radical das palavras
    #     tokens_stem = self.stemming_all_tokens(tokens)
    #     return tokens_stem
    
    def _tokenize_tf_idf(self, texto):
        """
        quebra o texto em sentencas, quebra as sentencas em palavras, e reduz
        as palavras a seu radical
        """
        tokens = []
        #coloca todas palavras do texto em um array
        for sentenca in self.sent_tokenize(texto):
            #quebra o texto em sentencas
            for plvr in self.tokenize(sentenca):
                #quebra a sentenca em palavras e poe dentro do array
                tokens.append(plvr)         
      
        return tokens
    
    def _get_stop_words_stemming(self):
        """
        retorna as stop words com seu radical
        """
        if self.__stop_words_stemming is None:
            self.__stop_words_stemming = self.stemming_all_tokens(self.get_stop_words())
        return self.__stop_words_stemming
    
    
    def _get_simple_ponto_sentenca_tf_idf(self, sentencas):
        """
        Retorna as sentencas com suas pontuacoes tf-idf.
        os pre-tratamentos feitos no _tokenize_tf_idf, devem ser feitos tambem as 
        stop words
        """
        #a parte q tokeniza estava tendo tendo problema com as aspas, que estavam ficando do
        #jeito q esta do lado das stop-words, entao eu apenas as inclui no array de stop-words
        stops = self.get_stop_words() + ['``']
        #Converte um texto em uma matriz de recursos do TF-IDF
        tfidf = TfidfVectorizer(analyzer='word', tokenizer=self._tokenize_tf_idf, stop_words=stops, decode_error='ignore')
        #construindo matriz do termo frequencia
        tdm = tfidf.fit_transform([self.get_texto()])
        #palavras com pontuacao
        feature_names = tfidf.get_feature_names()

        ranking = defaultdict(int)
        # Eu quero q a primeira sentenca seja retornada, por eu jogo um valor alto para ela.
        #Para garantir q ela seja retornada
        ranking[0] = 10000000000
        pontos_sentenca = []#array que ira conter a sentenca e sua pontuacao
        for mtf_idx in tdm:
            indice_tdm = mtf_idx.shape[0] - 1#indice do doc do qual recuperar o score tf-idf
            for i, sent in enumerate(sentencas):
                pontuacao = 0
                tokens = self.tokenize(sent)
                #calculando uma pontuação para cada frase 
                # somando os valores de TF-IDF para cada palavra que aparece na frase. 
                for token in (word for word in tokens if word in feature_names):
                    pontuacao += tdm[indice_tdm, feature_names.index(token)]
                #Normalizando a pontuacao da frase
                #dividindo pelo número de tokens na frase (para evitar viés a favor de frases mais longas)
                pontos_sentenca.append((sent, pontuacao / len(tokens)))
                ranking[i] += pontuacao / len(tokens)
        
        return (pontos_sentenca, ranking)

   
class Texto:

    def __init__(self):
        self.ranking    = None
        self.sentencas  = None
        self.texto      = None
        self.frequencia = None
        self.sent_score = None#um array de tuplas com a sentenca e sua pontuacao



#Alguns exemplos de como os resumos podem ser feitos

# t = "O Cons\u00f3rcio Nordeste informou que vai formalizar a compra de 39 milh\u00f5es de doses da vacina Sputnik V, nesta sexta-feira (12). A assinatura do contrato com o Fundo Soberano Russo acontecer\u00e1 em parceria com o Minist\u00e9rio da Sa\u00fade. Segundo o governo do Piau\u00ed, ser\u00e3o entregues 10 milh\u00f5es de doses de forma emergencial.  De acordo com o governador Wellington Dias (PT-PI), presidente do Cons\u00f3rcio Nordeste, a negocia\u00e7\u00e3o pelo Cons\u00f3rcio Nordeste para compras de 50 milh\u00f5es de doses de vacinas da R\u00fassia come\u00e7ou ainda em agosto do ano passado.  Contudo, com a demora para a formaliza\u00e7\u00e3o da compra, est\u00e3o dispon\u00edveis no momento 39 milh\u00f5es, que ser\u00e3o adquiridas em uma a\u00e7\u00e3o conjunta entre o governo federal e os estados.  A compra aconteceu depois que o  a comprar e a distribuir vacinas contra a Covid-19. A decis\u00e3o do STF foi tomada de forma un\u00e2nime.  O governo brasileiro estima contar com , \"podendo chegar a 38 milh\u00f5es\", fornecidas pelo Butantan e pela Oxford/Astrazeneca. A quantidade \u00e9 menor do que a . A redu\u00e7\u00e3o \u00e9 a quinta feita nas previs\u00f5es de doses a serem entregues no m\u00eas de mar\u00e7o.  . O n\u00famero representa 4,39% da popula\u00e7\u00e3o brasileira. Os dados s\u00e3o do cons\u00f3rcio de ve\u00edculos de imprensa. . "

# p = Pipeline()
# p.set_texto("O Cons\u00f3rcio Nordeste informou que vai formalizar a compra de 39 milh\u00f5es de doses da vacina Sputnik V, nesta sexta-feira (12). A assinatura do contrato com o Fundo Soberano Russo acontecer\u00e1 em parceria com o Minist\u00e9rio da Sa\u00fade. Segundo o governo do Piau\u00ed, ser\u00e3o entregues 10 milh\u00f5es de doses de forma emergencial.  De acordo com o governador Wellington Dias (PT-PI), presidente do Cons\u00f3rcio Nordeste, a negocia\u00e7\u00e3o pelo Cons\u00f3rcio Nordeste para compras de 50 milh\u00f5es de doses de vacinas da R\u00fassia come\u00e7ou ainda em agosto do ano passado.  Contudo, com a demora para a formaliza\u00e7\u00e3o da compra, est\u00e3o dispon\u00edveis no momento 39 milh\u00f5es, que ser\u00e3o adquiridas em uma a\u00e7\u00e3o conjunta entre o governo federal e os estados.  A compra aconteceu depois que o  a comprar e a distribuir vacinas contra a Covid-19. A decis\u00e3o do STF foi tomada de forma un\u00e2nime.  O governo brasileiro estima contar com , \"podendo chegar a 38 milh\u00f5es\", fornecidas pelo Butantan e pela Oxford/Astrazeneca. A quantidade \u00e9 menor do que a . A redu\u00e7\u00e3o \u00e9 a quinta feita nas previs\u00f5es de doses a serem entregues no m\u00eas de mar\u00e7o.  . O n\u00famero representa 4,39% da popula\u00e7\u00e3o brasileira. Os dados s\u00e3o do cons\u00f3rcio de ve\u00edculos de imprensa. . ")
# otexto_idf = p.process_tf_idx()


# sentencas_idf = otexto_idf.sentencas
# ranking_idf   = otexto_idf.ranking
# sent_score    = otexto_idf.sent_score

# # qtd_sent_resu = self._get_num_sentencas_resumo(len(sentencas))

# idx_sentencas_importantes_idf = nlargest(3, ranking_idf, key=ranking_idf.get)
# resumo_tipo1_tf_idf = " ".join(
#     [sentencas_idf[i] for i in sorted(idx_sentencas_importantes_idf)]
# )


# summary_length = int(3)
# sent_score.sort(key=lambda sent: sent[1], reverse=True)

# resumo_tipo2_tf_idf = " ".join(
#     [sent[0] for sent in sent_score[:summary_length]]
# )


# oTexto = p.process()
# sentencas = oTexto.sentencas
# ranking   = oTexto.ranking

# # qtd_sent_resu = self._get_num_sentencas_resumo(len(sentencas))

# idx_sentencas_importantes = nlargest(3, ranking, key=ranking.get)
# resumo_sem_tf_idf = " ".join(
#     [sentencas[i] for i in sorted(idx_sentencas_importantes)]
# )

# print('resumo sem tf-idf: ')
# print(resumo_sem_tf_idf)
# print('\n\n\n')
# print('resumo com tf-idf tipo 1: ')
# print(resumo_tipo1_tf_idf)
# print('\n\n\n')
# print('resumo com tf-idf tipo 2: ')
# print(resumo_tipo2_tf_idf)