from app import create_app
from app.config import log_config
import os
from dotenv import load_dotenv

load_dotenv()
logger = log_config("app.utils.message_sender")
app = create_app()

application = app

@app.route('/')
def home():
    return "Aplicação pessoal para controle financeiro. @renanortegax!"

def register_telegram_webhook():
    import requests
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    webhook_url = os.getenv("WEBHOOK_URL_DEV")
    # webhook_url = os.getenv("WEBHOOK_URL")

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

if __name__ == "__main__":
    logger.info("Aplicação iniciada")
    register_telegram_webhook()
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=8000, debug=True)