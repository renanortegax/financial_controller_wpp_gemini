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
    - Rode o arquivo /start/start.py -> assim que receber a mensagem no seu numero, responda com qualquer texto

### Configurando a planilha sheets
- Libs utilizadas: gspread, oauth2client
- Logar/Criar conta no google cloud para ativar a Google Sheets API
- Criar um projeto ou utilizar algum que ja possui
- Entrar em: APIs e servicos > Biblioteca
- Localizar Google Sheets API e Google Drive -> Ativar as duas
- Depois de ativado, sera necessario criar uma conta de servico:
    - Localizar: IAM e administrador > Contas de servico
        - Criar conta de servico (insira um nome e continue ate gerar a conta)
        - Em seguida, estara visivel a conta de servico na mesma pagina
- Agora, precisamos adicinoar uma chave:
    - "Adicionar chave" -> formato .json
    - Armazenar o json em ./secret_files_config
    - Precisa que o arquivo tenha o nome "config_key_google.json", ou altere para o nome que seu arquivo foi gerado e ajuste o codigo no modulo /data/google_sheet_connection.py
- Por fim, compartilhar sua planilha sheets com o email da credencial:
    - Em "Detalhes" da chave, copiar o email que foi gerado e, em sua planilha sheets, compartilhar com este email
    - A aba de index=0, sera registrada a mensagem bruta do usuario
    - A aba de index=1, sera registrada o que a IA retornou de classificacao da mensagem
    - IMPORTANTE: a planilha sheets sera conectada a partir do nome, ao chamar a classe sheet_name="Dados_Whast_App_Bot"

### Configurando a API doo Gemini
...

### Atualizacao de desenvolvimento:
#### Gemini:
- Estou com restricao à API do Gemini, possivelmente por terem alterado as políticas. Log:
```
* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0, model: gemini-2.0-flash
```
- Por isso, alterei o código para passar a só devolver uma mensagem pra tentar subir novamente, mas tomei o erro da Meta:
#### Meta:
- Integração com a API da Meta foi **restringido o uso dessa forma no Brasil para teste**. Log:
```bash
026-03-01 20:10:50,833 - verify_post - app.routes.webhook_listener - INFO - Status alterado-update completo: {'object': 'whatsapp_business_account', 'entry': [{'id': '3269397279904197', 'changes': [{'value': {'messaging_product': 'whatsapp', 'metadata': {'display_phone_number': '15551662388', 'phone_number_id': '949481414922924'}, 'statuses': [{'id': 'wamid.HBgNNTUxNDk5NzM5NDg5MhUCABEYEkJFMDU5RDZENUUyRjhDQUJDMwA=', 'status': 'failed', 'timestamp': '1772406581', 'recipient_id': '5514997394892', 'errors': [{'code': 130497, 'title': 'Business account is restricted from messaging users in this country.', 'message': 'Business account is restricted from messaging users in this country.', 'error_data': {'details': 'Business account is restricted from messaging users in this country.'}, 'href': 'https://developers.facebook.com/docs/whatsapp/cloud-api/support/error-codes/'}]}]}, 'field': 'messages'}]}]}
2026-03-01 20:10:50,834 - verify_post - app.routes.webhook_listener - INFO - Received a WhatsApp status update.
2026-03-01 20:10:50,835 - verify_post - app.routes.webhook_listener - ERROR - Mensagem falhou | code: 130497 | motivo: Business account is restricted from messaging users in this country. | destinatario: 5514997394892
```
#### Solucao:
- **Possivelmente, migrarei para Telegram #TODO**


## Estrutura:
```C.:
├── .git
├── .gitignore
├── README.md
├── app
│   ├── __init__.py
│   ├── config.py
│   ├── data
│   │   └── google_sheet_connection.py
│   ├── decorators
│   │   └── security.py
│   ├── routes
│   │   └── webhook_listener.py
│   └── utils
│       ├── ai_service.py
│       ├── message.py
│       ├── message_processor.py
│       ├── message_sender.py
│       └── utils.py
├── example.env
├── logs
│   └── app.log
├── requirements.txt
├── run.py
├── secret_files_config
│   └── config_key_google.json
├── start
│   └── quick_start.py
└── venv
```