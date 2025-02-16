from flask import Flask
from app.config import log_config, Config
from app.routes.webhook_listener import webhook_listener

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config) # Usando a classe Config
    log_config("app.__init__")

    app.register_blueprint(webhook_listener)

    return app