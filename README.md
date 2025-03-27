# WhatsApp bot para controle financeiro pessoal integrado com Gemini (gemini-2.0-flash) - Projeto Pessoal 100% Free

Essa aplicação tem por objetivo auxiliar no controle de gastos pessoais. Utiliza API da Meta (https://developers.facebook.com/docs/?locale=en_US) para integrar com o WhatsApp, Gemini para classificação das mensagems e demais funcionalidades extras. Desenvolvido em Flask para integrar com eventos de webhook em tempo real.
- Para aplicação local e testes, hospedado em um servidor local ngrok. 
- Deploy no pythonanywhere no modelo free

> Repositório útil: https://github.com/daveebbelaar/python-whatsapp-bot <br>
> Youtube video: https://www.youtube.com/watch?v=3YPeh-3AFmM&t=11s&ab_channel=DaveEbbelaar

## Necessário:
1. Conta de Meta developer 
2. Criar um Business App - https://developers.facebook.com/docs/development/create-an-app/
3. pip install -r requirements.txt


## Passo a passo:
> Documentação oficial: https://developers.facebook.com/docs/whatsapp/cloud-api/get-started
- Acesse https://developers.facebook.com/?no_redirect=1
- Faça o login
- "My Apps" -> Create App -> "Other" -> Business -> Insira email e nome para o app -> Em "Business portfolio", selecione sua conta
- Com o App criado, adicione o Whatsapp em "Set up"
Em API Setup, embaixo de "WhatsApp", ao abrir a tela terá o 'Test number', que será o número que receberemos e enviaremos mensagens. Adicione seu número em "To -> Manage Phone Number List"
- Comece com o start/quick_start.py, depois de adicionar o .env com as chaves necessarias, para enviar um template de mensagem teste para seu número. É importante responder qualquer coisa para o número que lhe enviou a mensagem para que seja possível enviar qualquer mensagem e não somente mensagens de template.
    - Código 'quick_start.py' retirado do repositório: https://github.com/daveebbelaar/python-whatsapp-bot/tree/main?tab=readme-ov-file
- Se deu certo receber a mensagem, podemos ir para a próxima etapa de configuração do webhook.

### Configurando Webhook
#### Baixando o ngrok e rodando a aplicação
- Para o teste local, com ngrok, rode o notebook via 'python .\run.py' na porta 8000 (conforme linha comentada)
- Crie uma conta em https://dashboard.ngrok.com/
- Baixe o ngrok
- Crie um domain: https://ngrok.com/blog-post/free-static-domains-ngrok-users
- Abra o ngrok e rodar o seguinte: ngrok http 8000 --domain <nome_do_seu_dominio>. Ex.: 'ngrok http 8000 --domain saving-something-something.ngrok-free.app' 
- É necessário rodar na mesma porta (8000) que o flask está rodando

#### Configurando o webhook no app
- No painel do aplicativo, vá em WhatsApp -> Config
- Adicione em URL de callback o seu "https://" + domain + "/webhook", que é o endpoint que espera o webhook e faz a validação com o seu VERIFY_TOKEN. Em seguida, coloque o mesmo VERIFY_TOKEN embaixo que está configurado em sua .env. 
- Em seguida, na lista de "Campos do webhook", habilite a opção "messages".
- Se tudo tiver certo, pode clicar em "Test" ao lado da opção "messages". Você receberá um status code 200 no terminal do ngrok, e isso indica que está devidamente configurado. Agora, pode enviar a mensagem para o número.

## Configurando a planilha sheets
...

## Configurando a API
...

## Estrutura:
```C.:
│   📁 .git
│   📁 .env
│   📁 app
│   │   📁 data
│   │   │   📄 google_sheet_connection.py
│   │   📁 decorators
│   │   │   📄 security.py
│   │   📁 routes
│   │   │   📄 webhook_listener.py
│   │   📁 utils
│   │   │   📄 ai_service.py
│   │   │   📄 message.py
│   │   │   📄 message_processor.py
│   │   │   📄 message_sender.py
│   │   │   📄 utils.py
│   │   📄 config.py
│   │   📄 __init__.py
│   📁 logs
│   │   📄 app.log
│   📁 secret_files_config
│   │   📄 config_key_google.json
│   📁 start
│   │   📄 quick_start.py
│   📄 .env
│   📄 .gitignore
│   📄 exemple_env.env
│   📄 README.md
│   📄 requirements.txt
│   📄 run.py
│   📄 testes.ipynb
│   📄 testing.py
```