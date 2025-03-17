from app.data.google_sheet_connection import GoogleSheetDb

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
    
def create_list_transaction_to_insert(detail_transaction, message, transaction_type):
    total_gasto = get_total_gasto(detail_transaction)
    return [
        [message.data.get('id'), message.sender_time, message.sender_name, transaction_type,item.get('categoria'), item.get('item'), item.get('valor'), item.get('detalhes'), total_gasto] 
        for item in detail_transaction.get("categorias")
    ]

def create_spent_return_message(detail_transaction):
    total_gasto = get_total_gasto(detail_transaction)
    formated_list_items = get_spent_categories_formated(detail_transaction)
    formated_message = "Gastos adicionados:\n"+"\n----------------------------------\n".join(formated_list_items)
    formated_message += f"\n-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n*Total gasto:* R${total_gasto:.2f}"
    return formated_message

def get_spent_categories_formated(detail_transaction):
    categories = detail_transaction.get('categorias')
    formated_items = [i for i in [f"Registro {i+1}: \n *Categoria:* {cat.get('categoria')}\n *Item:* {cat.get('item')}\n *Valor:* R${cat.get('valor'):.2f}\n *Detalhes:* {cat.get('detalhes')}" for i, cat in enumerate(categories)]]
    return formated_items

def get_total_gasto(detail_transaction):
    return detail_transaction.get('total_gasto')

def connect_sheet_transaction():
    return GoogleSheetDb(sheet_name="Dados_Whast_App_Bot", worksheet_index=1)

def insert_values_into_sheet_transaction(message, detail_transaction, transaction_type):
    sheet_transaction = connect_sheet_transaction()
    list_to_insert = create_list_transaction_to_insert(detail_transaction, message, transaction_type)
    
    sheet_transaction.append_multiple_rows(list_to_insert)
    
def create_message_transactions_filtered(filtered_data, json_filter):
    message_init = create_init_message_transactions_filtered(filtered_data, json_filter)
    
    return message_init + "\n" + "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-\n" + "-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-".join([f"*-Registro {i+1}:* \n - Data: {d.get('time')} \n - Categoria: {d.get('categoria')} \n - Item: {d.get('item')} \n - Valor: R$ {d.get('valor_item')} \n - Obs: {d.get('detalhes_adicionais')}\n" for i, d in enumerate(filtered_data)])

def create_init_message_transactions_filtered(filtered_data, json_filter):
    total_gasto = 0
    for _ in filtered_data:
        total_gasto += _.get('valor_item')
    
    message = f"Você gastou *R$ {total_gasto}* de {json_filter.get('data_inicial')} até {json_filter.get('data_final')}, para:"
    if json_filter.get("categorias"):
        message += "\n - Categoria(s): " + ", ".join(json_filter.get('categorias'))
    if json_filter.get("itens"):
        message += "\n - Itens: " + ", ".join(json_filter.get('itens'))
    
    return message
    
    