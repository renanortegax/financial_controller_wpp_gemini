import json
from dotenv import load_dotenv
import os
import requests

load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
PHONE_NUMBER_TO = os.getenv('PHONE_NUMBER_TO')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
VERSION = os.getenv('VERSION')
APP_ID = os.getenv('APP_ID')

## Testar a configuração da API e as chaves
def send_text_message_whatsapp_teste():
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": PHONE_NUMBER_TO,
        "type": "text",
        "text": {
            "preview_url": True,
            "body": "Eai, isso é só um teste, ok?!"
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    print(response.status_code)
    print(response.json())
    return response

response = send_text_message_whatsapp_teste()
