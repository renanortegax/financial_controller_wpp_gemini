from flask import Flask
from app.config import log_config, Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config) # Usando a classe Config
    log_config()
    return app