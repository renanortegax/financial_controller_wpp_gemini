import logging
import json
from flask import Blueprint, request, current_app, jsonify
from datetime import datetime
from app.data.google_sheet_connection import GoogleSheetDb
from app.decorators.security import signature_required

webhook_listener = Blueprint("webhook", __name__)

def verify_post():
    """ Verifica se o webhook está funcionando e orquestra e executa ações a partir da mensagem """
    request_data = request.get_json()

    if not is_valid_whatsapp_message(request_data):
        logging.info("Requisicao não é uma mensagem válida: %s", request_data)

    message = get_message_infos(request_data)
    logging.info("Campos extraídos: %s", message)

    # Salva no google sheets e no banco de dados
    process_message_data(request_data, message)

    return jsonify({"status": "ok"}), 200

# GraphAPI requer determinado retorno para validar autenticidade
def verify_get(): # a qualquer momento eles podem mandar um get e precisa ser validado conforme https://developers.facebook.com/docs/graph-api/webhooks/getting-started/
    """ Valida o servidor e a autenticidade da aplicação """
    hub_token = request.args.get("hub.verify_token")
    hub_mode = request.args.get("hub.mode")
    hub_challenge = request.args.get("hub.challenge") # An int you must pass back to us.
    logging.info(f"Recebido hub_token: {hub_token}")
    logging.info(f"Esperado VERIFY_TOKEN: {current_app.config['VERIFY_TOKEN']}")

    if hub_mode and hub_token:
        # Check the mode and token sent are correct
        if hub_mode == "subscribe" and hub_token == current_app.config["VERIFY_TOKEN"]:
            # Devolver o challenge INT da requisição
            logging.info("WEBHOOK_VERIFIED")
            return hub_challenge
        else:
            # Token não correspondido
            logging.info("VERIFICATION_FAILED")
            return jsonify({"status": "error_get_verification", "message": "Token does not match"}), 403
    else:
        # '400 Bad Request'
        logging.info("MISSING_PARAMETER")
        return jsonify({"status": "error_get_verification", "message": "No hub.mode or hub.verify token"}), 400

@webhook_listener.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    return verify_post()

@webhook_listener.route("/webhook", methods=["GET"])
def webhook_get():
    return verify_get()

def get_message_infos(request_data, sheet=False) -> dict:
    """ Pega as informações da mensagem recebida e retorna um dicionario """
    data = {}
    timestamp_sender = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('timestamp')
    if sheet:
        last_id = sheet.get_all_records()[-1].get('id')
        data['id'] = last_id + 1 if isinstance(last_id, int) else 1
    data['sender_time'] = datetime.fromtimestamp(int(timestamp_sender)).strftime('%Y-%m-%d %H:%M:%S')
    data['sender_name'] = request_data.get('entry')[0].get('changes')[0].get('value').get('contacts')[0].get('profile').get('name')
    data['sender_number'] = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('from')
    data['direction'] = 'received'
    data['message_type'] = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('type')
    data['text'] = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('text').get('body')
    return data

def process_message_data(request_data, message):
    """ Salva no db e no sheets """
    save_to_google_sheets(request_data)


def save_to_google_sheets(request_data):
    """ Salva no sheets pegando as infos com id """
    sheet = GoogleSheetDb(sheet_name="Dados_Whast_App_Bot")

    # Extrai com o id por conta do google sheets
    row_append_sheet = get_message_infos(request_data, sheet=sheet)
    sheet.append_row(list(row_append_sheet.values()))


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