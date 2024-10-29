# config.py
import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

db_config = {
    'host': os.getenv("DB_HOST", "default_host"),
    'database': os.getenv("DB_DATABASE", "default_database"),
    'port': int(os.getenv("DB_PORT", 3307)),  # Converte para inteiro
    'user': os.getenv("DB_USER", "default_user"),
    'password': os.getenv("DB_PASSWORD", "default_password")
}
