#%% python -m app.utils.auth
from app.utils.utils import connect_sheet_auth
from app.utils.message import Message
from app.data.google_sheet_connection import GoogleSheetDb
from app.config import log_config
from datetime import datetime
import os

logger = log_config('app.utils.auth')

auth_sheet = connect_sheet_auth()
pending_auth = set()
verified_auth = set()

def load_verified_auth(auth_sheet: GoogleSheetDb):
    """Carrega os chat_ids verificados da planilha para o cache em memória"""
    global verified_auth
    auth_sheet.refresh_data()
    verified_auth = set(int(i.get('chat_id')) for i in auth_sheet.data if i.get('chat_id'))
    logger.info("Cache carregado: %s chat_ids verificados", len(verified_auth))


class AuthService():
    def __init__(self, message: Message, auth_sheet: GoogleSheetDb):
        self.auth_sheet = auth_sheet
        self.message = message
        self.chat_id = str(message.sender_number)

    def check_header_auth(self):
        if not self.auth_sheet.data:
            self.auth_sheet.append_row(['chat_id','sender_name','username','verified_at'])

    def check_chatid_verified(self) -> bool:
        return int(self.chat_id) in verified_auth

    def register_chat_id(self):
        """Salva o chat_id na planilha e atualiza o cache"""
        global verified_auth
        self.check_header_auth()
        row = [
            self.chat_id,
            self.message.sender_name,
            self.message.username,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ]
        self.auth_sheet.append_row(row)
        verified_auth.add(int(self.chat_id))
        logger.info("chat_id %s autorizado e salvo", self.chat_id)

    def is_pending(self) -> bool:
        return self.chat_id in pending_auth

    def add_to_pending(self):
        pending_auth.add(self.chat_id)
        logger.info("chat_id %s, username %s adicionado ao pending_auth", self.chat_id, self.message.username)

    def remove_from_pending(self):
        pending_auth.discard(self.chat_id)

    def handle_auth(self):
        if self.is_pending():
            password = os.getenv("SENHA_PRA_ENTRAR")
            if self.message.text.lower() == password.lower(): 
                self.register_chat_id()
                self.remove_from_pending()
                self.message.reply_message("✅ Acesso autorizado")
            else:
                self.message.reply_message("❌ Senha incorreta.")
        else:
            self.add_to_pending()
            self.message.reply_message("🔒 Esse é um chat privado - digite a senha.")
        
