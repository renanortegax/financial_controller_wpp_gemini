# Telegram Bot para Controle Financeiro Pessoal com Gemini

Bot pessoal para controle de gastos via Telegram, integrado com Gemini (Google AI) para classificação de mensagens e Google Sheets para armazenamento. Desenvolvido em Flask para lidar com webhooks em tempo real. **Projeto pessoal**.

- **Para testes locais**: Servidor local exposto via ngrok.
- **Deploy gratuito**: Hospedado no [Koyeb](https://app.koyeb.com/) (requer cartão de crédito para verificação, sem cobranças reais no uso normal).

> Repositório de inspiração: [python-whatsapp-bot](https://github.com/daveebbelaar/python-whatsapp-bot) (adaptado para Telegram).

## Tecnologias Utilizadas
- **Telegram API**: Comunicação via bot.
- **Gemini (Google AI)**: Modelos gratuitos para processamento de linguagem natural.
- **Google Sheets**: Armazenamento e consulta de transações financeiras.
- **Flask**: Framework web para webhooks.
- **Gunicorn**: Servidor WSGI para produção.
- **Ngrok**: Exposição de porta local para testes.
- **Koyeb**: Plataforma de deploy gratuita.

## Funcionalidades
- **Classificação de Mensagens**: IA identifica se a mensagem é um registro, consulta ou alteração de gasto.
- **Registro de Gastos**: Extrai categorias, itens, valores e detalhes da mensagem e salva no Google Sheets.
- **Consulta de Gastos**: Filtra e exibe transações por data, categoria e item.
- **Fallback de Modelos**: `ModelManager` gerencia múltiplos modelos Gemini, alternando automaticamente em caso de limite de quota.
- **Notificações**: Alerta o usuário via Telegram quando um modelo atinge o limite e tenta o próximo.

## Pré-requisitos
1. Conta no Google Cloud para ativar APIs (Sheets e Gemini).
2. Conta no Telegram para criar o bot.
3. Python 3.8+ e pip.
4. Instalar dependências: `pip install -r requirements.txt`.

## Passo a Passo de Configuração

### 1. Configurando o Bot no Telegram
- Acesse o [@BotFather](https://t.me/botfather) no Telegram.
- Crie um novo bot com `/newbot`, defina nome e username.
- Copie o **TOKEN** gerado e adicione ao `.env` como `TELEGRAM_BOT_TOKEN=seu_token_aqui`.
- Inicie uma conversa com seu bot e envie `/start` para testá-lo.

### 2. Configurando o Google Sheets
- Acesse [Google Cloud Console](https://console.cloud.google.com/).
- Crie um projeto ou use um existente.
- Ative as APIs: **Google Sheets API** e **Google Drive API** (em "APIs e Serviços" > "Biblioteca").
- Crie uma conta de serviço:
  - Vá para "IAM e Administrador" > "Contas de Serviço" > "Criar Conta de Serviço".
  - Gere uma chave JSON e baixe o arquivo.
  - Para uso local, salve como `config_key_google.json` em `./secret_files_config/`.
  - Para produção (Koyeb), cole o conteúdo do JSON inteiro como variável de ambiente `GOOGLE_CREDENTIALS_JSON` em uma única linha:
    ```
    GOOGLE_CREDENTIALS_JSON={"type": "service_account", "project_id": "seu-projeto", "private_key_id": "abc123", "private_key": "-----BEGIN PRIVATE KEY-----\nSUA_CHAVE_AQUI\n-----END PRIVATE KEY-----\n", "client_email": "sua-conta@seu-projeto.iam.gserviceaccount.com", "client_id": "123456789", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/sua-conta%40seu-projeto.iam.gserviceaccount.com", "universe_domain": "googleapis.com"}
    ```
- Compartilhe sua planilha Google Sheets com o email da conta de serviço.
- O nome da planilha no código é `"Dados_Whast_App_Bot"` — ajuste se necessário.
  - Aba 0: Mensagens brutas do usuário.
  - Aba 1: Dados processados pela IA.

### 3. Configurando a API do Gemini
- No Google Cloud Console, ative a **Generative Language API**.
- Gere uma chave de API em "APIs e Serviços" > "Credenciais" > "Criar Credenciais" > "Chave de API".
- Adicione ao `.env` como `GOOGLE_API_KEY=sua_chave_aqui`.
- O projeto usa modelos gratuitos com fallback automático via `ModelManager`.

### 4. Configurando o Webhook

**Produção (Koyeb):**
- O webhook é registrado automaticamente ao subir a aplicação, desde que `WEBHOOK_URL` esteja definida no `.env` do Koyeb.
- O valor deve ser a URL pública gerada pelo Koyeb + `/webhook`. Ex.: `https://seu-app.koyeb.app/webhook`.

**Testes locais (ngrok):**
- Instale o [ngrok](https://ngrok.com/) e crie um domínio estático gratuito.
- Rode: `ngrok http 8000 --domain seu-dominio.ngrok-free.app`
- Defina `WEBHOOK_URL_DEV=https://seu-dominio.ngrok-free.app/webhook` no `.env`.
- Rode a aplicação com: `python run.py --dev`

### 5. Arquivo `.env`
Crie um arquivo `.env` na raiz conforme o `example.env` disponível no repositório.

## Deploy no Koyeb
1. Crie uma conta no [Koyeb](https://app.koyeb.com/) e conecte seu repositório GitHub.
2. Crie um novo serviço:
   - Selecione o repositório e a branch desejada.
   - Escolha **Buildpack** como builder — ele detecta Python automaticamente.
   - O `Procfile` na raiz já configura o gunicorn corretamente, sem necessidade de ajustes manuais de build ou start command.
3. Adicione as variáveis de ambiente (as do `.env`).
4. Faça o deploy. A URL pública gerada pelo Koyeb deve ser adicionada como `WEBHOOK_URL` nas variáveis de ambiente. (f"{url}/webhook")
5. A partir daí, cada push na branch configurada dispara um novo deploy automaticamente.

> **Nota sobre gratuidade**: O Koyeb exige cartão de crédito para verificação, mas não cobra nada no uso normal dentro do plano gratuito. O serviço **não dorme** por inatividade, diferente de outras plataformas.

## Estrutura do Projeto
```
├── app
│   ├── data
│   │   └── google_sheet_connection.py  # Conexão com Google Sheets
│   ├── decorators
│   ├── routes
│   │   └── webhook_listener.py         # Listener de webhooks do Telegram
│   ├── utils
│   │   ├── ai_service.py               # Serviço de IA com Gemini e fallbacks
│   │   ├── auth.py                     # Serviço de autenticacao - via senha no .env
│   │   ├── message.py                  # Classe para mensagens do Telegram
│   │   ├── message_processor.py        # Processamento de mensagens
│   │   ├── message_sender.py           # Envio de mensagens
│   │   ├── model_manager.py            # Gerenciamento de modelos com fallback
│   │   └── utils.py                    # Utilitários diversos
│   ├── __init__.py                     # Inicialização do app Flask
│   └── config.py                       # Configurações gerais
├── secret_files_config                 # Credenciais locais (não subir para o git)
├── example.env                         # Exemplo de variáveis de ambiente
├── Procfile                            # Configuração do gunicorn para produção
├── requirements.txt                    # Dependências do projeto
├── run.py                              # Ponto de entrada principal
└── README.md
```

## Limitações e Notas
- **Limites gratuitos do Gemini**: Quotas diárias (ex.: 15 RPM, 1500 RPD). O `ModelManager` alterna entre modelos automaticamente para mitigar interrupções.
- **Segurança**: Nunca suba chaves de API ou o `config_key_google.json` para o repositório público.
- **Contribuições**: Sinta-se à vontade