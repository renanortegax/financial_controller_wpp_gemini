import os
from dotenv import load_dotenv
import logging
import sys

load_dotenv()

class Config:
    """ Pega as variáveis de ambiente para aplicação """
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    APP_ID = os.getenv('APP_ID')
    APP_SECRET = os.getenv('APP_SECRET')
    PHONE_NUMBER_TO = os.getenv('PHONE_NUMBER_TO')
    PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
    VERSION = os.getenv('VERSION')
    VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ASSISTANT_ID = os.getenv('OPENAI_ASSISTANT_ID')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

def log_config():
    """ Configura e inicia os logs da aplicação """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(funcName)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)])

    logging.getLogger().info("Log configurado")

    return logging.getLogger(__name__)
