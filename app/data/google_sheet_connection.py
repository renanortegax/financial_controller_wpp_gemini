import gspread
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Any, Dict
import logging
import os

class GoogleSheetDb:
    """
    Classe que encapsula a conexão e operações básicas em uma planilha do Google Sheets
    """
    def __init__(self, 
                 sheet_name: str, 
                 credential_file: str = os.path.join(os.getcwd(), "config_key_google.json"), 
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

        # Seleciona a worksheet (página) desejada pelo índice (ou nome, se preferir)
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
        logging.info(f"Linha adicionada: {row_data}")

    def update_cell(self, row: int, col: int, value: Any):
        """
        Atualiza uma célula específica (row, col).
        As linhas e colunas são 1-based (não zero-based).

        :param row: Índice da linha (1-based).
        :param col: Índice da coluna (1-based).
        :param value: Valor a ser gravado na célula.
        """
        self.worksheet.update_cell(row, col, value)

    def find(self, query: str):
        """
        Procura uma célula que contenha o 'query' exato
        Retorna o objeto 'Cell' ou levanta gspread.exceptions.CellNotFound se não achar
        """
        return self.worksheet.find(query)
