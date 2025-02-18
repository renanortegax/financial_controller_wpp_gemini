from app.config import log_config
from app.utils.ai_service import AIService
from app.data.google_sheet_connection import GoogleSheetDb
import json
from IPython.display import Markdown 

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
        # json_response_ai = json.loads(detail_transaction)
        insert_values_into_sheet_transaction(message, detail_transaction, transaction_type)
        # message.reply_message(f"IA classificou os gastos conforme: {detail_transaction}. \nO retorno seria {create_return_message(detail_transaction)}.\nSua transação foi gravada na sua planilha.") #TODO criar uma resposta personalizada dizendo o que foi gravado
        message.reply_message(f"{create_return_message(detail_transaction)}.\n\nFique a vontade para me mandar qualquer mensage =).") #TODO criar uma resposta personalizada dizendo o que foi gravado
    
    elif transaction_type == 'consulta':
        message.reply_message("Você quer consultar seus gastos, certo? \nEssa função ainda não está implementada... cena dos próximos capítulos") #TODO
    
    elif transaction_type == 'alteracao':
        message.reply_message("Você quer alterar algum registro, certo? \nEssa função ainda não está implementada... cena dos próximos capítulos") #TODO
    
    elif transaction_type == 'nao-identificado':
        message.reply_message("Não entendi muito bem o que disse, por isso, não farei nenhuma ação. Poderia me explicar melhor ?\n A mensagem não se encaixa nas tarefas que eu costumo fazer por aqui :)")
        
    else:
        message.reply_message("Não entendi bem o que você quis dizer. (TODO)")
        
def create_list_transaction_to_insert(detail_transaction, message, transaction_type):
    total_gasto = get_total_gasto(detail_transaction)
    return [
        [message.data.get('id'), message.sender_time, message.sender_name, transaction_type,item.get('categoria'), item.get('item'), item.get('valor'), item.get('detalhes'), total_gasto] 
        for item in detail_transaction.get("categorias")
    ]

def create_return_message(detail_transaction):
    total_gasto = get_total_gasto(detail_transaction)
    categorias = detail_transaction.get('categorias')
    formated_list_items = [i for i in [f"Registro {i+1}: \n *Categoria:* {cat.get('categoria')}\n *Item:* {cat.get('item')}\n *Valor:* R${cat.get('valor'):.2f}\n *Detalhes:* {cat.get('detalhes')}" for i, cat in enumerate(categorias)]]
    formated_message = "O seu pedido é uma ordem. Estou adicionando na sua planilha conforme abaixo:\n"+"\n----------------------------------\n".join(formated_list_items)
    formated_message += f"\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n*Total gasto:* R${total_gasto:.2f}"
    return formated_message

def get_total_gasto(detail_transaction):
    return detail_transaction.get('total_gasto')

def connect_sheet_transaction():
    return GoogleSheetDb(sheet_name="Dados_Whast_App_Bot", worksheet_index=1)

def insert_values_into_sheet_transaction(message, detail_transaction, transaction_type):
    sheet_transaction = connect_sheet_transaction()
    list_to_insert = create_list_transaction_to_insert(detail_transaction, message, transaction_type)
    
    sheet_transaction.append_multiple_rows(list_to_insert)
    