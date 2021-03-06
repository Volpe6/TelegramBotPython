class Mensagem:
    """
    classe das mensagens:
    400 - erros
    500 - erros internos
    """

    MENSAGEM = {
        '400': 'Hum... Infelizmente o texto informado não contém a quantidade de caracteres esperada.',
        '401': 'Ops... houve um problema. Tente novamente mais tarde',
        '500': 'Bot ausente',
        '501': 'Para carregar o modelo é necessário que "use_model_analise" seja "True"',
        '502': 'Você esta tentando mandar uma mensagem pelo bot do telegram, sendo que você não definiu o "update" que é passado por parametro pela api do telegram'
    }
    
    @staticmethod
    def get_mensagem(cod, *args):
        msg = Mensagem.MENSAGEM[str(cod)]

        for arg in args:
            msg += arg
        return msg
    
    @staticmethod
    def print_console(nome, msg):
        print(f'{nome} > {msg}')