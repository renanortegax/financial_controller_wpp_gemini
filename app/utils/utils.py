from flask import current_app
import google.generativeai as genai
from IPython.display import HTML, Markdown, display # usar para retornar a mensagem com formatação
import typing_extensions as typing
# from app.config import log_config

# logger = log_config('app.utils.utils')

import logging
from dotenv import load_dotenv
import os
load_dotenv()

logging.basicConfig(
    level=logging.INFO,  # Define o nível mínimo para INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]  # Garante que a saída vai para stdout
)

def check_wpp_message(request_data):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        request_data.get("object")
        and request_data.get("entry")
        and request_data["entry"][0].get("changes")
        and request_data["entry"][0]["changes"][0].get("value")
        and request_data["entry"][0]["changes"][0]["value"].get("messages")
        and request_data["entry"][0]["changes"][0]["value"]["messages"][0]
    )

class TipoTransacao(typing.TypedDict):
    tipo: str  # "registro", "consulta", "alteracao"
class Categoria(typing.TypedDict):
    categoria: str
    valor: float
    detalhes: list[str]
class GastoFinanceiro(typing.TypedDict):
    categorias: list[Categoria]
    total_gasto: float
    tipo: str

def get_google_api_key():
    # GOOGLE_API_KEY = current_app.config["GOOGLE_API_KEY"]
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    return GOOGLE_API_KEY

def create_type_transaction(text_input):
    return f"""
            Vamos falar em português.

            Eu tenho um sistema de controle financeiro. Vou te enviar uma mensagem que pode ser um **registro**, uma **consulta** ou uma **alteração** de gastos.

            ### Regras para classificar:
            - **Registro**: O usuário descreve um novo gasto que ele quer adicionar. Exemplo: "Fui ao mercado e gastei 50 reais em compras."
            - **Consulta**: O usuário quer ver um resumo dos gastos já registrados. Exemplo: "Quanto eu gastei esse mês?"
            - **Alteração**: O usuário quer modificar um gasto existente. Exemplo: "Quero corrigir o valor do Uber que registrei antes."

            Sua tarefa é classificar a mensagem corretamente e **retornar APENAS o seguinte JSON**, sem explicações adicionais:
            ```json
            {{
                "tipo": "registro"  # ou "consulta" ou "alteracao"
            }}"""

def create_register_prompt(text_input, request_type):
    return  f"""
    Vamos falar em português.

    Esta é uma operação do tipo **{request_type}**.

    Se for um **registro**, sua tarefa é identificar corretamente os valores monetários e categorizá-los da forma mais adequada. Se houver mais de um gasto, classifique cada um separadamente e some os valores de cada categoria.

    Se for uma **consulta**, retorne um resumo dos gastos registrados, organizados por categoria.

    Se for uma **alteração**, forneça instruções para modificar um gasto já existente.


    Vou te enviar um texto descrevendo meus gastos do dia. Sua tarefa é identificar corretamente os valores monetários e categorizá-los da forma mais adequada. Se houver mais de um gasto, classifique cada um separadamente e some os valores de cada categoria.

    Regras para a categorização:
    - Transporte: Uber, táxi, ônibus, gasolina, aluguel de veículos, passagens, etc.
    - Alimentação: Restaurantes, lanchonetes, supermercados (se alimentos), cafés, bares, etc.
    - Vestuário: Roupas, calçados, acessórios.
    - Entretenimento: Cinema, teatro, shows, jogos, lazer.
    - Compras Gerais: Eletrônicos, móveis, produtos diversos.
    - Outros: Qualquer item que não se encaixe nas categorias acima.

    Segue minha mensagem de hoje: {text_input}
    """

def connecting_with_genai(text_input):
    GOOGLE_API_KEY = get_google_api_key()
    genai.configure(api_key=GOOGLE_API_KEY)

    flash = genai.GenerativeModel('gemini-2.0-flash', #'gemini-1.5-flash' #gemini-1.5-flash-8b #gemini-2.0-flash
                                  generation_config=genai.GenerationConfig(
                                    max_output_tokens = 500,
                                    top_k = 40, # dentre as próximas palavras, ele escolhe a 1ª mais provável. quanto mais baixo, mais previsível
                                    top_p = 0.9, # [0.0, 1.0]: limite de confianca a partir das palavras definidas por top_k. Se top_p = 0.9, o modelo escolhe tokens até que a soma das probabilidades atinja 90%.
                                    response_mime_type="application/json",
                                    response_schema=GastoFinanceiro,
    )) 
    
    prompt_type_transaction = create_type_transaction(text_input)

    response = flash.generate_content(prompt_type_transaction, 
                                      generation_config=genai.GenerationConfig(
                                          max_output_tokens=50,
                                          response_mime_type="application/json",
                                          response_schema=TipoTransacao
                                        )
                                    )
    logging.info("IA classificou como: %s", response.text)

    register_prompt = create_register_prompt(text_input, 'registro')
    response = flash.generate_content(register_prompt)
    logging.info("Retorno da IA: %s", response.text)
    # logging.info("Retorno da IA em Markdown: \n%s", Markdown(response.text))
    

if __name__ == '__main__':
    connecting_with_genai("Fui no shopping hoje de uber, paguei 15 reais no uber. Na volta também voltei de uber, foi 17 reais. Lá no shopping, comi um lanche por 30 reais e comprei uma camiseta de 150 reais")