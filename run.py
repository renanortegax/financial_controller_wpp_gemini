from app import create_app
import logging

app = create_app()

application = app

@app.route('/')
def home():
    return "Aplicação pessoal para controle financeiro. @renanortegax!"

if __name__ == "__main__":
    logging.info("Aplicação iniciada")
    app.run(debug=True)
    # app.run(host="0.0.0.0", port=8000, debug=True)