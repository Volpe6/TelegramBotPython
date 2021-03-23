from pathlib import Path
import shutil
import json

class GerenciaArquivo(object):
    '''
       Classe para controlar e gerenciar arquivos.
       Permite salvar, criar, e apagar arquivos.
    '''

    @staticmethod
    def get_path(caminho):
        if not GerenciaArquivo.existe_diretorio(caminho):
            GerenciaArquivo.cria_diretorio(caminho)
        return Path(caminho)

    @staticmethod
    def get_diretorio_atual():
        return Path.cwd()
    
    @staticmethod
    def imprime_diretorio_atual():
        '''
            Printa no console o diretorio atual
        '''
        print(GerenciaArquivo.get_diretorio_atual())


    @staticmethod
    def abrir_aquivo(caminho, modo='r', codificacao='utf-8-sig'):
        '''
            Abri um arquivo no caminho especificado
                Args:
                  caminho: string, com o caminho do diretório ou arquivo.
                  modo: string que define o modo que sera aberto o arquivo. 
                  r = leitura, w = escrita, e tem outras opções
                  codificacao: codificacao na qual abrir o arquivo
                  retorna (object)file
        '''
        return open(caminho, modo, codificacao)

    @staticmethod
    def cria_diretorio(caminho):
        '''
            Cria diretorio no caminho informado
                Args:
                    caminho: string, com o caminho do diretório ou arquivo.
        '''
        if GerenciaArquivo.existe_diretorio(caminho):
            raise Exception('O diretorio que esta tentando criar já existe.')
        Path(caminho).mkdir()

    @staticmethod
    def existe_diretorio(caminho):
        '''
            Verifica se o caminho existe
                Args:
                   caminho: string, com o caminho do diretório ou arquivo.
                   retorna bool
        '''
        return Path(caminho).exists()
    
    @staticmethod
    def is_diretorio(caminho):
        '''
            Verifica se o caminho passado é um diretorio
                Args: 
                   caminho: string, com o caminho do diretório ou arquivo.
                   retorna bool
        '''
        return Path(caminho).is_dir()
    
    @staticmethod
    def remove(caminho):
        '''
            Remove o diretorio ou arquivo no caminho informado. 
            Caso o caminho informado pertencer a um diretorio e o mesmo não 
            estiver vazio ele não sera removido.
        '''
        if not GerenciaArquivo.existe_diretorio(caminho):
            raise Exception('O caminho do diretorio/arquivo informado não existe')

        o_path = Path(caminho)
        if GerenciaArquivo.is_diretorio(caminho):
            #remove diretorio
            try:
                Path.rmdir(o_path)
            except:
                print(f'apagando arquivos do dir: {caminho}')
                shutil.rmtree(caminho)
        else:
            #remove arquivo
            Path.unlink(o_path)

    @staticmethod
    def salva_arquivo_json(nome_arquivo, content=[]):
        if len(nome_arquivo.split('.')) <= 1:
            nome_arquivo = f'{nome_arquivo}.json'
        else:
            ext = nome_arquivo.split('.')[1]
            if ext != 'json':
                temp_name = nome_arquivo.split('.')[0]
                nome_arquivo = f'{temp_name}.json'

        with open(nome_arquivo, 'w') as file:
            json.dump(content, file)
    
    @staticmethod
    def abir_arquivo_json(nome_arquivo):
        if len(nome_arquivo.split('.')) <= 1:
            nome_arquivo = f'{nome_arquivo}.json'
        else:
            ext = nome_arquivo.split('.')[1]
            if ext != 'json':
                temp_name = nome_arquivo.split('.')[0]
                nome_arquivo = f'{temp_name}.json'

        data = []
        with open(nome_arquivo) as file:
            try:
                data = json.load(file)
            except Exception as ex:
                print(f'nao foi possivel abrir o arquivo {nome_arquivo}')
                data = []
        return data

    @staticmethod
    def salva_arquivo_texto(path, extension, content):
        '''
            Salva um arquivo no caminho informado

            Args:
                path: caminho onde salvar o arquivo
                extension: extensao do arquivo
                content: conteudo do arquivo
        '''
        #caminho completo onde salvar o caminho
        s_caminho = f'{path}.{extension}'

        #verifica se existe algo no caminho informado
        if GerenciaArquivo.existe_diretorio(s_caminho):
            GerenciaArquivo.remove(s_caminho)
            
        with open(s_caminho, mode='a', encoding='utf-8-sig') as file:
            file.write(content)

    @staticmethod
    def abrir_arquivo_texto(path):
        '''
        retorna o texto de um arquivo informado

        Args:
            label: o label a ser adicionado no inicio do texto do arquivo aberto
            path : caminho onde se encontra o caminhoa ser aberto 
        '''

        # texto que sera retornado apos a leitura do arquivo
        s_txt = ''

        # metodo facilitado para leitura de arquivo em python, ja que sempre que
        # apos a leitura o aruivo é fechado a declaracao 'with open' ja abstrai isso
        # file => aquivo aberto
        # open => metodo que abre o arquivo
        # mode => se eh leitura escrita ou outra coisa
        # enconding => a codificacao na qual abrir o arquivo
        with open(path, mode='r', encoding='utf-8-sig') as file:
            # array de string que compoem o arquivo
            a_tx = []
            for linha in file:
                # verifica se o comprimento da linha eh 1, se for significa que eh uma linha em 
                # branco e apenas continua
                if len(linha) == 1:
                    continue
                # rstrip, remove espaços em branco excedente no inicio e fim da string
                a_tx.append(linha.rstrip())

                #une todos os valores no array de string, em uma unica string
                # ' ' => string de conexao de todas as strings, pode ser qualquer string
                #join => une um array em uma unica string. Talvez faça outras coisas, ver doc.
                s_txt = ' '.join(a_tx)
        
        return s_txt

