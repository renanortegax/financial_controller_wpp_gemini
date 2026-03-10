import json
from flask import Blueprint, request, current_app, jsonify
from datetime import datetime
from app.data.google_sheet_connection import GoogleSheetDb
from app.utils.message import Message
from app.config import log_config
from app.utils.message_processor import process_incoming_message
import traceback

logger = log_config('app.routes.webhook_listener')
webhook_listener = Blueprint("webhook", __name__)

def verify_post():
    """Recebe updates do Telegram e orquestra as ações"""
    request_data = request.get_json()

    # Ignora updates que não são mensagens de texto (ex: edições, callbacks)
    if not request_data.get('message') or not request_data['message'].get('text'):
        logger.info("Update ignorado (não é mensagem de texto): %s", request_data)
        return jsonify({"status": "ok"}), 200

    try:
        sheet = GoogleSheetDb(sheet_name="Dados_Whast_App_Bot")
        message = Message(request_data, sheet)
        message.process_message_data()
        logger.info("Mensagem tratada: %s", message.get_message_infos())

        process_incoming_message(message)

        return jsonify({"status": "ok"}), 200

    except json.JSONDecodeError:
        logger.error("Failed to decode JSON")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400

    except Exception as e:
        logger.error("Erro inesperado: %s", e)
        logger.error("Traceback: %s", traceback.format_exc())
        return jsonify({"status": "error", "message": str(e)}), 200 # pro telegram/wpp nao ficar enviando infinito

@webhook_listener.route("/webhook", methods=["POST"])
def webhook_post():
    return verify_post()