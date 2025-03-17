from app.config import log_config
from app.utils.ai_service import AIService
from app.data.google_sheet_connection import GoogleSheetDb
import json
from IPython.display import Markdown 
from app.utils.utils import create_list_transaction_to_insert,create_spent_return_message,get_spent_categories_formated,get_total_gasto, connect_sheet_transaction, insert_values_into_sheet_transaction, create_message_transactions_filtered

logger = log_config("app.utils.message_processor")
ai_service = AIService()

def process_incoming_message(message):
    """
    Recebe um objeto `Message` (que já contém o texto do usuário) e decide
    o que fazer (classificar, registrar, responder, etc).
    """
    text_input = message.text
    
    transaction_type = ai_service.get_type_message(text_input)
    logger.info("Mensagem classificada como %s pela IA", transaction_type)
    
    if transaction_type == 'registro':
        detail_transaction = ai_service.get_register_transaction_ai_flow(text_input)

        logger.info("Detail transaction: %s", detail_transaction)
        insert_values_into_sheet_transaction(message, detail_transaction, transaction_type)
        message.reply_message(f"{create_spent_return_message(detail_transaction)}.\n\nAtt. Mago")
    
    elif transaction_type == 'consulta':
        message.reply_message("Parece que você quer *consultar* seus gastos.\nEssa função em teste...") #TODO
        sheet_transaction = connect_sheet_transaction()
        filter_conditions = ai_service.get_consulting_transaction_ai_flow(text_input=text_input,
                                                                          sample_data=sheet_transaction.get_random_lines(),
                                                                          unique_items=sheet_transaction.get_sheet_unique_items()
                                                                          )
        message.reply_message(f"Os filtros que a IA classificou: {filter_conditions}")
        filtered_data = sheet_transaction.filter_sheet_by_conditions(filter_conditions)
        message.reply_message(f"{create_message_transactions_filtered(filtered_data, filter_conditions)}\n\nAtt. Mago")        
    
    elif transaction_type == 'alteracao':
        message.reply_message("Você quer *alterar* algum registro, certo? \Função ainda não implementada...") #TODO
    
    elif transaction_type == 'nao-identificado':
        message.reply_message("Parece que o que você deseja não está no meu escopo. Estou disponível para *inserir registros*, *consultar seus gastos* ou *alterar algum registro*.")
        
    else:
        message.reply_message("Acho que tive alguma alucinação...")
        
# def create_list_transaction_to_insert(detail_transaction, message, transaction_type):
#     total_gasto = get_total_gasto(detail_transaction)
#     return [
#         [message.data.get('id'), message.sender_time, message.sender_name, transaction_type,item.get('categoria'), item.get('item'), item.get('valor'), item.get('detalhes'), total_gasto] 
#         for item in detail_transaction.get("categorias")
#     ]

# def create_spent_return_message(detail_transaction):
#     total_gasto = get_total_gasto(detail_transaction)
#     formated_list_items = get_spent_categories_formated(detail_transaction)
#     formated_message = "Gastos adicionados:\n"+"\n----------------------------------\n".join(formated_list_items)
#     formated_message += f"\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n*Total gasto:* R${total_gasto:.2f}"
#     return formated_message

# def get_spent_categories_formated(detail_transaction):
#     categories = detail_transaction.get('categorias')
#     formated_items = [i for i in [f"Registro {i+1}: \n *Categoria:* {cat.get('categoria')}\n *Item:* {cat.get('item')}\n *Valor:* R${cat.get('valor'):.2f}\n *Detalhes:* {cat.get('detalhes')}" for i, cat in enumerate(categories)]]
#     return formated_items

# def get_total_gasto(detail_transaction):
#     return detail_transaction.get('total_gasto')

# def connect_sheet_transaction():
#     return GoogleSheetDb(sheet_name="Dados_Whast_App_Bot", worksheet_index=1)

# def insert_values_into_sheet_transaction(message, detail_transaction, transaction_type):
#     sheet_transaction = connect_sheet_transaction()
#     list_to_insert = create_list_transaction_to_insert(detail_transaction, message, transaction_type)
    
#     sheet_transaction.append_multiple_rows(list_to_insert)
    
