import logging
import json
from flask import Blueprint, request, current_app, jsonify
from datetime import datetime
from app.config import log_config
from app.utils.message_sender import MessageSender

logger = log_config("app.utils.message")

class Message:
    def __init__(self, request_data, sheet=None):
        """Inicializa a mensagem extraindo os dados do request_data"""
        self.request_data = request_data
        self.sheet = sheet
        self.data = self.get_message_infos()
        self.sender_name = self.data.get("sender_name", 'Não encontrei seu nome')
        self.sender_time = self.data.get("sender_time")
        self.sender_number = self.data.get("sender_number", None)
        self.text = self.data.get("text", None)
    
    def get_message_infos(self) -> dict:
        """Pega as informações da mensagem recebida e retorna um dicionário"""
        data = {}
        try:
            entry = self.request_data.get('entry', [])[0]
            changes = entry.get('changes', [])[0]
            value = changes.get('value', {})
            message = value.get('messages', [])[0]
            contact = value.get('contacts', [])[0]

            if self.sheet:
                last_id = self.sheet.get_all_records()[-1].get('id', 0)
                data['id'] = last_id + 1 if isinstance(last_id, int) else 1

            data['sender_time'] = datetime.fromtimestamp(int(message.get('timestamp'))).strftime('%Y-%m-%d %H:%M:%S')
            data['sender_name'] = contact.get('profile', {}).get('name', 'Desconhecido')
            data['sender_number'] = message.get('from', '')
            data['direction'] = 'received'
            data['message_type'] = message.get('type', '')
            data['text'] = message.get('text', {}).get('body', '')

        except (IndexError, AttributeError, TypeError) as e:
            logger.error(f"Erro ao extrair mensagem: {e}")
            return {}
        return data

    def __save_to_google_sheets(self):
        """Salva os dados no Google Sheets"""
        if self.sheet:
            row_data = list(self.data.values())
            self.sheet.append_row(row_data)

    def process_message_data(self):
        """ Salva as mensagens na planilha sheets """
        self.__save_to_google_sheets()

    def reply_message(self, text):
        sender = MessageSender() # informações para inciar são conhecidas da aplicação
        logger.info("Enviando resposta para: %s", self.sender_number)
        response = sender.send_message(text, self.sender_number) 

        return response
    
