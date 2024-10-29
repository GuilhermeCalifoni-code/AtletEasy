# db.py
import mysql.connector
from mysql.connector import Error
from config import db_config

def get_db_connection():
    try:
        conexao = mysql.connector.connect(**db_config)
        if conexao.is_connected():
            print("Conexão com o banco de dados estabelecida.")
            return conexao
    except Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
    return None
