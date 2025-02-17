from app.config import log_config
from app.utils.ai_service import AIService

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
        message.reply_message(f"IA classificou os gastos conforme: {detail_transaction}. \nSua transação será gravada na planilha no futuro (Função ainda não implementada)") #TODO
    
    elif transaction_type == 'consulta':
        message.reply_message("Você quer consultar seus gastos, certo? \nEssa função ainda não implementada... cenas dos próximos capítulos") #TODO
    
    elif transaction_type == 'alteracao':
        message.reply_message("Você quer alterar algum registro, certo? \nEssa função ainda não implementada... cenas dos próximos capítulos") #TODO
    
    else:
        message.reply_message("Não entendi bem o que você quis dizer. (TODO)") #TODO