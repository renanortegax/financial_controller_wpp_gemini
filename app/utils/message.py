import logging
import json
from flask import Blueprint, request, current_app, jsonify
from datetime import datetime
from app.config import log_config
from app.utils.message_sender import MessageSender
from app.data.google_sheet_connection import GoogleSheetDb

logger = log_config("app.utils.message")

class Message:
    def __init__(self, request_data, sheet: GoogleSheetDb | None = None):
        """Inicializa a mensagem extraindo os dados do request_data do Telegram"""
        self.request_data = request_data
        self.sheet = sheet
        self.data = self.get_message_infos()
        self.sender_name = self.data.get("sender_name", 'Não encontrei seu nome')
        self.sender_time = self.data.get("sender_time")
        self.sender_number = self.data.get("sender_number", None)  # no Telegram = chat_id
        self.username = self.data.get("username", None)  # no Telegram = chat_id
        self.text = self.data.get("text", None)

    def get_message_infos(self) -> dict:
        """Pega as informações da mensagem recebida do Telegram e retorna um dicionário"""
        data = {}
        try:
            message = self.request_data.get('message', {})
            chat = message.get('chat', {})
            sender = message.get('from', {})

            if self.sheet:
                last_id = self.sheet.get_all_records()[-1].get('id', 0)
                data['id'] = last_id + 1 if isinstance(last_id, int) else 1

            timestamp = message.get('date', 0)
            data['sender_time'] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

            first = sender.get('first_name', '')
            last = sender.get('last_name', '')
            data['sender_name'] = f"{first} {last}".strip() or 'Desconhecido'

            data['username'] = str(chat.get('username', ''))  # chat_id é o "número" no Telegram
            data['sender_number'] = str(chat.get('id', ''))  # chat_id é o "número" no Telegram
            data['direction'] = 'received'
            data['message_type'] = 'text' if message.get('text') else 'other'
            data['text'] = message.get('text', '')

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
        logger.info("Enviando resposta para chat_id: %s", self.sender_number)
        response = sender.send_message(text, self.sender_number)
        
        logger.info(f"Status do envio: {response.status_code}")
        logger.info(f"Resposta: {response.json()}")

        return response
    
