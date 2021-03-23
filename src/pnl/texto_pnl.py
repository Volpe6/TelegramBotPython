import numpy as np
import sklearn

from sklearn.feature_extraction.text import CountVectorizer


def verifica_similaridade(txt1, txt2):
    #Numero de n-gram
    n = 1
    #instancia contador de n-gramas
    counts = CountVectorizer(analyzer='word', ngram_range=(n, n))
    #cria uma matriz de contagem de n-gram para os dois textos
    n_grams = counts.fit_transform([txt1, txt2])
    #cria um dict de n-gramas
    dict_palavras = counts.fit([txt1, txt2]).vocabulary_

    n_grams_array = n_grams.toarray()

    intersection_list = np.amin(n_grams.toarray(), axis = 0)
    intersection_count = np.sum(intersection_list)

    index_A = 0
    A_count = np.sum(n_grams.toarray()[index_A])
    #valor de similaridade
    val_sim = intersection_count/A_count
    
    return val_sim
