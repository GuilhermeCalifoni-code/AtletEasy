# db.py
import mysql.connector
from mysql.connector import Error
from config import db_config

def get_db_connection():
    try:
        # Cria a conexão usando os parâmetros do arquivo de configuração
        connection = mysql.connector.connect(
            host=db_config['host'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password'],
            port=db_config['port'],
            ssl_disabled=True  # Desabilita SSL para evitar erros relacionados
        )
        if connection.is_connected():
            print("Conexão com o banco de dados estabelecida.")
            return connection
        else:
            print("Falha ao conectar ao banco de dados.")
            return None
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None