import json
from flask import Blueprint, request, current_app, jsonify
from datetime import datetime
from app.data.google_sheet_connection import GoogleSheetDb
from app.decorators.security import signature_required
from app.utils.message import Message
from app.utils.message_sender import MessageSender
from app.config import log_config

logger = log_config('app.routes.webhook_listener')
webhook_listener = Blueprint("webhook", __name__)

def verify_post():
    """ Verifica se o webhook está funcionando e orquestra e executa ações a partir da mensagem """
    request_data = request.get_json()

    # Check if it's a WhatsApp status update
    if (request_data.get('entry')[0].get('changes')[0].get('value').get('statuses')):
        infos_status_alterado = request_data.get('entry')[0].get('changes')[0].get('value').get('statuses')[0]
        logger.info("Status alterado: %s", jsonify(infos_status_alterado))
        logger.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200


    try:
        # Mensagem recebida
        # Salva no sheets a partir da mensagem
        sheet = GoogleSheetDb(sheet_name="Dados_Whast_App_Bot")
        message = Message(request_data, sheet)
        message.process_message_data()
        logger.info("Request recebido: %s", request_data)
        logger.info("Mensagem tratada: %s", message.get_message_infos())

        # Processa mensagem -> envia retorno
        if is_valid_whatsapp_message(request_data):
            sender = MessageSender()

            parameters = sender.get_parameters_message_sender(current_app.config["PHONE_NUMBER_TO"], "TESTE DE RETORNO") # Aqui vale entrar uma função que trata a mensagem
            sender.send_message(parameters=parameters)
            
            return jsonify({"status": "ok"}), 200
        else:
            return (
                jsonify({"status": "error", "message": "Not a WhatsApp API event"}),
                404,
            )
        
    except json.JSONDecodeError:
        logger.error("Failed to decode JSON")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400

# GraphAPI requer determinado retorno para validar autenticidade
def verify_get(): # a qualquer momento eles podem mandar um get e precisa ser validado conforme https://developers.facebook.com/docs/graph-api/webhooks/getting-started/
    """ Valida o servidor e a autenticidade da aplicação """
    hub_token = request.args.get("hub.verify_token")
    hub_mode = request.args.get("hub.mode")
    hub_challenge = request.args.get("hub.challenge") # An int you must pass back to us.
    # logger.info(f"Recebido hub_token: {hub_token}")
    # logger.info(f"Esperado VERIFY_TOKEN: {current_app.config['VERIFY_TOKEN']}")

    if hub_mode and hub_token:
        # Check the mode and token sent are correct
        if hub_mode == "subscribe" and hub_token == current_app.config["VERIFY_TOKEN"]:
            # Devolver o challenge INT da requisição
            logger.info("WEBHOOK_VERIFIED")
            return hub_challenge
        else:
            # Token não correspondido
            logger.info("VERIFICATION_FAILED")
            return jsonify({"status": "error_get_verification", "message": "Token does not match"}), 403
    else:
        # '400 Bad Request'
        logger.info("MISSING_PARAMETER")
        return jsonify({"status": "error_get_verification", "message": "No hub.mode or hub.verify token"}), 400

@webhook_listener.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    return verify_post()

@webhook_listener.route("/webhook", methods=["GET"])
def webhook_get():
    return verify_get()

def is_valid_whatsapp_message(request_data):
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