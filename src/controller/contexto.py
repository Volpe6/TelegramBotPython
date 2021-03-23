from util.mensagem import Mensagem

DEBUG = True

class Contexto:
    __update        = None
    __texto_analise = None
    __termo         = ''
    __notices       = None
    __configuracao  = None
    __resultado     = None
    __chat_id       = None
    __message_id    = None
    __bot           = None
    __user          = None#nome do usuario com o qual estou falando

    def get_user_name(self):
        #nome do usuario com o qual estou falando
        if self.get_user() is None:
            return 
        return self.get_user().first_name

    def set_user(self, user):
        self.__user = user
    
    def get_user(self):
        return self.__user

    def set_chat_id(self, chat_id):
        self.__chat_id = chat_id
    
    def get_chat_id(self):
        return self.__chat_id

    def set_bot(self, bot):
        self.__bot = bot

    def get_bot(self):
        return self.__bot

    @staticmethod
    def print_console(nome, msg):
        if not DEBUG:
            return
        Mensagem.print_console(nome, msg)
    
    def new_bot_message(self, msg):
        message = self.get_update().message.reply_text(msg)
        self.__message_id = message.message_id
        self.__chat_id = message.chat_id

    def _new_bot_message(self, msg):
        message = self.get_update().message.reply_text(msg)
        self.__message_id = message.message_id
        self.__chat_id = message.chat_id


    def bot_message(self, msg, edit_message=False):
        """
        quando "edit_message" é "true" a ultima mensagem enviada é alterada
        """
        if self.get_update() is None:
            return

        if edit_message:
            
            if self.__message_id is None or self.__chat_id is None:
                self._new_bot_message(msg)
            
            if self.get_bot() is None:
                raise Exception(Mensagem.get_mensagem(500))
        
            try:
                self.get_bot().edit_message_text(chat_id=self.get_chat_id(), message_id=self.__message_id, text=msg)
            except:
                self.get_bot().edit_message_text(chat_id=self.get_chat_id(), message_id=self.__message_id, text=f'{msg}.')
            return 
        
        self._new_bot_message(msg)            

    def set_update(self, update):
        self.__update = update
    
    def get_update(self):
        return self.__update

    def set_texto_analise(self, texto):
        self.__texto_analise = texto

    def get_texto_analise(self):
        return self.__texto_analise

    def set_termo_busca(self, termo):
        self.__termo = termo

    def get_termo_busca(self):
        return self.__termo

    def set_notices(self, notices):
        self.__notices = notices
    
    def get_all_notices(self):
        return self.__notices

    def set_configuracao(self, conf):
        self.__configuracao = conf
    
    def get_configuracao(self):
        return self.__configuracao

    def set_resultado(self, resu):
        self.__resultado = resu

    def get_resultado(self):
        return self.__resultado