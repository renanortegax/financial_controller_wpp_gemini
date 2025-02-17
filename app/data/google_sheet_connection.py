import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Any, Dict
import os
from app.config import log_config
from datetime import datetime

logger = log_config('app.data.google_sheet_connection')
class GoogleSheetDb:
    """
    Classe que encapsula a conexão e operações básicas na planilha do Google Sheets
    """
    def __init__(self,
                 sheet_name: str,
                 credential_file: str = os.path.join(os.getcwd(), 'secret_files_config', "config_key_google.json"),
                 scope: List[str] = [
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive.file",
                    "https://www.googleapis.com/auth/drive",
                ],
                 worksheet_index: int = 0):
        # Autorizando a conexão
        self.scope = scope
        self.creds = ServiceAccountCredentials.from_json_keyfile_name(credential_file, scope)
        self.client = gspread.authorize(self.creds)

        # Abre a planilha
        self.spreadsheet = self.client.open(sheet_name)

        # Seleciona pelo índice ou pelo nome
        self.worksheet = self.spreadsheet.get_worksheet(worksheet_index)

    def get_all_records(self) -> List[Dict[str, Any]]:
        """
        Retorna todas as linhas da planilha como uma lista de dicionários
        Cada dicionário é uma linha
        """
        return self.worksheet.get_all_records()

    def append_row(self, row_data: List[Any]):
        """
        Adiciona uma linha ao final da planilha
        """
        self.worksheet.append_row(row_data)
        logger.info(f"Linha adicionada: {row_data}")

    def append_multiple_rows(self, rows_data):
        """
        Adiciona N linhas no final da planilha
        """
        self.worksheet.append_rows(rows_data)
        logger.info("Linhas adicionadas: %s", rows_data)

    def update_cell(self, row: int, col: int, value: Any):
        """
        Atualiza uma célula específica (row, col)
        As linhas e colunas começam em 1
        """
        self.worksheet.update_cell(row, col, value)

    def find(self, query: str):
        """
        Procura uma célula que contenha o 'query' exato
        Retorna o objeto 'Cell' ou levanta gspread.exceptions.CellNotFound se não achar
        """
        return self.worksheet.find(query)

    def create_row_to_append(self, request_data):
        """ Pega as informações da mensagem recebida e retorna um dicionario """
        data = {}
        timestamp_sender = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('timestamp')
        data['id'] = self.get_all_records()[-1].get('id') + 1
        data['sender_time'] = datetime.fromtimestamp(int(timestamp_sender)).strftime('%Y-%m-%d %H:%M:%S')
        data['sender_name'] = request_data.get('entry')[0].get('changes')[0].get('value').get('contacts')[0].get('profile').get('name')
        data['sender_number'] = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('from')
        data['direction'] = 'received'
        data['message_type'] = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('type')
        data['text'] = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('text').get('body')
        return data

