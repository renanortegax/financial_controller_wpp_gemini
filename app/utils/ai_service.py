import json
import google.generativeai as genai
import typing_extensions
from dotenv import load_dotenv
import os
from app.config import log_config
# from app.data.google_sheet_connection import GoogleSheetDb.get_sheet_unique_items, GoogleSheetDb.get_random_lines

logger = log_config('app.utils.ai_service')
load_dotenv()

# import logging
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     handlers=[logging.StreamHandler()]
# )

class TipoTransacao(typing_extensions.TypedDict):
    """ Schema de retorno da IA para classificar o tipo de transação """
    tipo: str  # "registro", "consulta", "alteracao"

class Categoria(typing_extensions.TypedDict):
    """ Schema de retorno da IA para as categorias de gasto em uma transação de registro """
    categoria: str
    valor: float
    item: str
    detalhes: str #list[str]

class GastoFinanceiro(typing_extensions.TypedDict):
    """ Schema de retorno da IA para os gastos daquela mensagem """
    categorias: list[Categoria]
    total_gasto: float
    tipo: str

class FiltrosConsulta(typing_extensions.TypedDict):
    """ Schema de retorno da IA para os filtros da consulta """
    categorias: list[str]
    data_inicial: str
    data_final: str
    itens: list[str]

class AIService:
    """ Classe para gerenciar a conexão e uso da IA """
    
    _instance = None  # Singleton para reutilizar a instância

    def __new__(cls):
        """ Garante que só existe uma instância do AIService """ 
        if cls._instance is None:
            cls._instance = super(AIService, cls).__new__(cls)
            cls._instance.configure_api()
            cls._instance.initialize_model()
        return cls._instance
    
    def configure_api(self):
        # GOOGLE_API_KEY = current_app.config["GOOGLE_API_KEY"]
        GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=GOOGLE_API_KEY)

    def initialize_model(self):
        self.model = genai.GenerativeModel(
                model_name='gemini-2.0-flash',
                generation_config=genai.GenerationConfig(
                    max_output_tokens=500,
                    top_k=40,
                    top_p=0.9,
                    response_mime_type="application/json"
                )
            )
        logger.info("Modelo AI inicializado com sucesso.")

    def get_type_message(self, text_input):
        """Classifica a mensagem usando a IA"""
        prompt = self.create_prompt_type_transaction(text_input)
        response = self.model.generate_content(prompt,
                                               generation_config=genai.GenerationConfig(
                                                   max_output_tokens=50,
                                                   response_mime_type="application/json",
                                                   response_schema=TipoTransacao,
                                                   )
                                               )
        logger.info("IA classificou como: %s", response.text)
        
        return json.loads(response.text).get("tipo")

    def create_prompt_type_transaction(self, text_input):
        return f"""
                Vamos falar em português.

                Eu tenho um sistema de controle financeiro. Vou te enviar uma mensagem que pode ser um **registro**, uma **consulta** ou uma **alteração** de gastos.

                ### Regras para classificar:
                - **Registro**: O usuário descreve um novo gasto que ele quer adicionar. Exemplo: "Fui ao mercado e gastei 50 reais em compras."
                - **Consulta**: O usuário quer ver um resumo dos gastos já registrados. Exemplo: "Quanto eu gastei esse mês?"
                - **Alteração**: O usuário quer modificar um gasto existente. Exemplo: "Quero corrigir o valor do Uber que registrei antes."

                Sua tarefa é classificar a mensagem corretamente e **retornar APENAS o seguinte JSON**, sem explicações adicionais. Caso a mensagem que eu te enviar não se encaixe de forma alguma em nenhum dos tipos abaixo, classifique como "nao-identificado"
                ```json
                {{
                    "tipo": "registro"  # ou "consulta" ou "alteracao" ou "nao-identificado"
                }}
                Agora segue a mensagem que estou te enviando:
                {text_input}
                """

    def create_prompt_register_transaction(self, text_input):
        return  f"""
        Vamos falar em português.
        Vou te enviar um texto descrevendo meus gastos do dia. Sua tarefa é identificar corretamente os valores monetários e categorizá-los da forma mais adequada. Se houver mais de um gasto, classifique cada um separadamente e some os valores de cada categoria.

        Regras para a categorização:
        - Transporte: Uber, táxi, ônibus, gasolina, aluguel de veículos, passagens, etc.
        - Alimentação: Restaurantes, lanchonetes, supermercados (se alimentos), cafés, bares, etc.
        - Vestuário: Roupas, calçados, acessórios.
        - Entretenimento: Cinema, teatro, shows, jogos, lazer.
        - Compras Gerais: Eletrônicos, móveis, produtos diversos.
        - Outros: Qualquer item que não se encaixe nas categorias acima.

        Para os casos que identificar, extraia o item que o dinheiro foi gasto e qual categoria ele melhor se encaixa. Além disso, o valor desse item e qualquer informação adicional, coloque em detalhes.

        Segue minha mensagem: {text_input}
        """
        
    def create_prompt_filter_search(self, text_input, sample_data, unique_items):
        """ Cria o prompt que ira me retornar os filtros que o usuário deseja em sua consulta """
        categorias, items, dates = unique_items
        return  f"""
        Vamos falar em português.
        Tenho um grande dicionário de gastos financeiros com algumas informações. Segue abaixo um exemplo dele:

        {sample_data}

        Categorias disponíveis: {", ".join(categorias)}
        Itens disponíveis: {", ".join(items)}
        Período de datas disponível: de {dates[0]} até {dates[-1]}

        Agora, preciso que você analise a seguinte consulta do usuário e retorne um JSON estruturado para que eu possa aplicar os filtros corretamente na minha planilha.

        Regras para a extração de informações:

        Categorias: Identifique quais categorias são mencionadas e retorne-as em uma lista. Caso o usuário não especifique, retorne null. Tenha em vista que o usuário não passará necessariamente o nome exato dos itens, ou categorias. Por isso, faça o julgamento de quais acha que deve incluir de forma consiente.
        Itens: Identifique itens específicos que o usuário deseja buscar. Caso ele não mencione itens específicos, retorne null.
        Período de data: O usuário pode fazer consultas com datas absolutas ou relativas (ex.: "essa semana", "últimos 7 dias", "mês passado"). Interprete corretamente e retorne:
        data_inicial: Data de início do período filtrado.
        data_final: Data de fim do período filtrado.
        
        Importante:
        Caso o usuário use períodos relativos, adapte corretamente. Exemplo:
        "esse mês" (considerando que estamos em março de 2025) → data_inicial: "2025-03-01", data_final: "2025-03-31"
        "última semana" → Se hoje for 15/03/2025, então data_inicial: "2025-03-10", data_final: "2025-03-16" (segunda a domingo).
        "mês passado" → Se estamos em março, então data_inicial: "2025-02-01", data_final: "2025-02-28". {text_input}
        """

    def send_prompt(self, text_input):
        response = self.model.generate_content(text_input, generation_config=genai.GenerationConfig())
        return response.text
    
    
    def get_register_transaction_ai_flow(self, text_input):
        """ Método deve ser chamado quando se sabe que é um caso de registro. Passa para a IA classificar as categorias e retorna o json categorizado """
        prompt = self.create_prompt_register_transaction(text_input)
        response = self.model.generate_content(prompt,
                                               generation_config=genai.GenerationConfig(
                                                   response_schema=GastoFinanceiro,
                                                   )
                                               )
        
        logger.info("O retorno do registro pela IA foi: %s", response.text)
        
        return json.loads(response.text)

    def get_consulting_transaction_ai_flow(self, text_input, sample_data, unique_items):
        """ Método deve ser chamado quando se sabe que é um caso de consulta. A IA retornará os filtros que o usuário deseja
            unique_items = [categorias, items, dates]
        """
        prompt = self.create_prompt_filter_search(text_input, sample_data, unique_items)
        response = self.model.generate_content(prompt,
                                               generation_config=genai.GenerationConfig(
                                                   response_schema=FiltrosConsulta,
                                                   )
                                               )
        
        logger.info("Os filtros que a IA classificou: %s", response.text)
        
        return json.loads(response.text)

