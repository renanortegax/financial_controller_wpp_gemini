from app import create_app
from app.config import log_config
import os
from dotenv import load_dotenv
import argparse

load_dotenv()

logger = log_config("app.utils.message_sender")

app = create_app()
application = app  # usar o gunicorn

@app.route('/')
def home():
    return "Aplicação pessoal para controle financeiro. @renanortegax!"

def register_telegram_webhook(dev_run=False):
    import requests

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    webhook_url = os.getenv("WEBHOOK_URL") if not dev_run else os.getenv("WEBHOOK_URL_DEV")

    if not webhook_url:
        logger.warning("WEBHOOK_URL não definida no .env — webhook não registrado")
        return

    url = f"https://api.telegram.org/bot{token}/setWebhook"
    response = requests.post(url, json={"url": webhook_url})
    result = response.json()

    if result.get("ok"):
        logger.info("Webhook registrado com sucesso: %s", webhook_url)
    else:
        logger.error("Falha ao registrar webhook: %s", result)

# Registra o webhook sempre que a aplicação sobe (gunicorn ou python run.py)
# Em produção, DEV_RUN não estará definida, então usará WEBHOOK_URL normalmente
dev_run = os.getenv("DEV_RUN", "false").lower() == "true"
register_telegram_webhook(dev_run)

if __name__ == "__main__":
    logger.info("Aplicação iniciada")

    parser = argparse.ArgumentParser(description='Run flask app')
    parser.add_argument('--dev', action='store_true')
    args = parser.parse_args()

    # debug só roda localmente via python run.py
    app.run(host="0.0.0.0", port=8000, debug=args.dev)