import requests
from app.config import log_config
from dotenv import load_dotenv
import os
from flask import current_app, jsonify
import json 

logger = log_config("app.utils.message_sender")
load_dotenv()

class MessageSender:
    def __init__(self):
        self.endpoint = "messages"
        self.phone_numer_id = current_app.config['PHONE_NUMBER_ID']
        self.headers = {
            "Content-type": "application/json",
            "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
        }
        self.url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/{self.endpoint}"

        # logger.info('Classe MessageSender inicializada com os parâmetros %s', vars(MessageSender))

    def get_parameters_message_sender(self, text, send_to):
        return json.dumps(
            {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to":"+" + send_to,
                "type": "text",
                "text": {"preview_url": False, "body": text},
            }
        )

    def send_message(self, text, send_to):
        url = self.url
        headers = self.headers
        parameters = self.get_parameters_message_sender(text, send_to)

        logger.info("Parametros de chamada: %s", parameters)
        # logger.info("URL: %s", self.url)
        # logger.info("Headers: %s", self.headers)
        try:
            response = requests.post(url, data=parameters, headers=headers, timeout=10)
            response.raise_for_status()
        
        except requests.Timeout:
            logger.error("Timeout enquanto respondia a mensagem")
            return jsonify({"status":"error", "message":"Timeout"}), 400

        except (requests.RequestException) as e:
            logger.error("Request error: %s", e)
            return jsonify({"status":"error", "message":"Failed"}), 500
        
        else: # Se passar
            logger.info("Status: %s", response.status_code)
            # logger.info("Response sent: %s", response.json())
            return response