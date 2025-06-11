"""
config.py

Arquivo de configurações globais para o projeto fleet_management.
As configurações são carregadas a partir das variáveis de ambiente.
Utilize um arquivo .env (na raiz do projeto) para definir os parâmetros de produção.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env, se ele existir
BASE_DIR = Path(__file__).resolve().parent
dotenv_path = BASE_DIR / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

# -------------------------------
# Configuração do Banco de Dados
# -------------------------------
DATABASE_NAME = os.getenv("FLEET_DB_NAME", "fleet_management.db")
DATABASE_PATH = BASE_DIR / DATABASE_NAME

# -------------------------------
# Configurações do Google Drive API
# -------------------------------
# Essas variáveis são obrigatórias. Se alguma não estiver definida, o sistema levantará KeyError.
GOOGLE_DRIVE_CONFIG = {
    "client_id": os.environ["GOOGLE_DRIVE_CLIENT_ID"],
    "client_secret": os.environ["GOOGLE_DRIVE_CLIENT_SECRET"],
    "redirect_uri": os.getenv("GOOGLE_DRIVE_REDIRECT_URI", "http://localhost:8080/callback"),
    "api_key": os.getenv("GOOGLE_DRIVE_API_KEY", ""),
    "token": os.getenv("GOOGLE_DRIVE_TOKEN", None)
}

# -------------------------------
# Configurações de E-mail (Gmail)
# -------------------------------
# Estas variáveis são obrigatórias para o envio de e-mails.
EMAIL_CONFIG = {
    "smtp_server": os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("EMAIL_SMTP_PORT", 587)),
    "email_address": os.environ["EMAIL_ADDRESS"],
    "email_password": os.environ["EMAIL_PASSWORD"]
}

# -------------------------------
# Outras Configurações Gerais da Aplicação
# -------------------------------
APP_CONFIG = {
    "debug": os.getenv("APP_DEBUG", "True").lower() in ("true", "1", "t"),
    "secret_key": os.environ["APP_SECRET_KEY"]
}

def print_configurations():
    """
    Exibe as configurações atuais para fins de depuração.
    Atenção: em produção, evite imprimir informações sensíveis.
    """
    print("Configurações do Banco de Dados:")
    print(f"  DATABASE_PATH: {DATABASE_PATH}")
    print("\nConfigurações do Google Drive:")
    for key, value in GOOGLE_DRIVE_CONFIG.items():
        print(f"  {key}: {value}")
    print("\nConfigurações de E-mail:")
    for key, value in EMAIL_CONFIG.items():
        print(f"  {key}: {value}")
    print("\nConfigurações da Aplicação:")
    for key, value in APP_CONFIG.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    print_configurations()
