import logging
import json
from flask import Blueprint, request, current_app, jsonify
from datetime import datetime

webhook_listener = Blueprint("webhook", __name__)

def verify_post():
    """ Verifica se o webhook está funcionando """
    request_data = request.get_json()
    logging.info("POST JSON: %s", request_data)
    message = get_message_infos(request_data)
    logging.info("Campos extraídos: %s", message)

    return "ok", 200

# GraphAPI requer determinado retorno para validar autenticidade
def verify_get(): # a qualquer momento eles podem mandar um get e precisa ser validado conforme https://developers.facebook.com/docs/graph-api/webhooks/getting-started/
    """ Valida o servidor e a autenticidade da aplicação """
    hub_token = request.args.get("hub.verify_token")
    hub_mode = request.args.get("hub.mode")
    hub_challenge = request.args.get("hub.challenge") # An int you must pass back to us.

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
def webhook_post():
    return verify_post()

@webhook_listener.route("/webhook", methods=["GET"])
def webhook_get():
    return verify_get()

def get_message_infos(request_data) -> dict:
    """ Pega as informações da mensagem recebida e retorna um dicionario """
    data = {}
    data["text"] = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('text').get('body')
    data["sender_name"] = request_data.get('entry')[0].get('changes')[0].get('value').get('contacts')[0].get('profile').get('name')
    data["sender_number"] = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('from')
    timestamp_sender = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('timestamp')
    data["sender_time"] = datetime.fromtimestamp(int(timestamp_sender)).strftime('%Y-%m-%d %H:%M:%S')
    data["message_type"] = request_data.get('entry')[0].get('changes')[0].get('value').get('messages')[0].get('type')
    return data


def mesage_formating(request_data):
    """ Trata a mensagem recebida """
    mesage_text, mesage_name_from, mesage_number_from, mesage_time_from, mesage_type_from = get_message_infos(request_data)
    return logging.info(f"Message infos: {mesage_name_from} - {mesage_number_from} - {mesage_time_from} - {mesage_type_from} - {mesage_text}")
