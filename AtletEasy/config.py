# config.py
import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()  # Carrega as variáveis do arquivo .env

db_config = {
    'host': os.getenv("DB_HOST"),
    'database': os.getenv("DB_DATABASE"),
    'port': os.getenv("DB_PORT"),
    'user': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'ssl_disabled': True
}
