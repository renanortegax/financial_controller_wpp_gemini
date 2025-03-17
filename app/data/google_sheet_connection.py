import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Any, Dict
import os
from app.config import log_config
from datetime import datetime
import random

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
        # Seleciona aba pelo índice ou pelo nome
        self.worksheet = self.spreadsheet.get_worksheet(worksheet_index)
        self.data = []
        self.refresh_data()


    def refresh_data(self):
        """
        Atualiza os dados armazenados na instância da classe
        """
        self.data = self.get_all_records()

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
        data['id'] = self.data[-1].get('id') + 1
        data['sender_time'] = datetime.fromtimestamp(int(timestamp_sender)).strftime('%Y-%m-%d %H:%M:%S')
        data['sender_name'] = request_data.get('entry')[0].get('changes')[0].get('value').get('contacts')[0].get('profile').get('name')
        data['sender_number'] = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('from')
        data['direction'] = 'received'
        data['message_type'] = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('type')
        data['text'] = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('text').get('body')
        return data

    def get_random_lines(self, n=2):
        if len(self.data) < n:
            return self.data
        return random.sample(self.data, n)

    def get_sheet_unique_items(self):
        categorias = []
        items = []
        times = []
        for i in self.data:
            if not i.get('categoria') in categorias:
                categorias.append(i.get('categoria'))
            if not i.get('item') in items:
                items.append(i.get('item'))
            if not i.get('time') in times:
                times.append(i.get('time'))
                
        datas_convertidas = [datetime.strptime(data, '%Y-%m-%d %H:%M:%S') for data in times]
        times = [datetime.strftime(min(datas_convertidas), '%Y-%m-%d'), datetime.strftime(max(datas_convertidas), '%Y-%m-%d')]
            
        return categorias, items, times
    
    def filter_sheet_by_conditions(self, filter_conditions):
        """ Retorna o dicionario de registros filtrados """
        return list(filter(lambda transacao: self.define_line_in_filter(transacao, filter_conditions), self.data))
        
    def define_line_in_filter(self, transacao: Dict[str, Any], filter_conditions: Dict[str, Any]) -> bool:
        """ Filtra o dicionario e retorna True se a transacao passar pelo filtro """
        
        if filter_conditions.get("categorias") and transacao.get("categoria") not in filter_conditions["categorias"]:
            return False

        if filter_conditions.get("itens") and transacao.get("item") not in filter_conditions["itens"]:
            return False

        transacao_data = datetime.strptime(transacao.get("date", ""), "%Y/%m/%d")

        data_inicial = filter_conditions.get("data_inicial")
        data_final = filter_conditions.get("data_final")

        if data_inicial:
            data_inicial = datetime.strptime(data_inicial, "%Y-%m-%d")
            if transacao_data < data_inicial:
                return False

        if data_final:
            data_final = datetime.strptime(data_final, "%Y-%m-%d")
            if transacao_data > data_final:
                return False

        return True