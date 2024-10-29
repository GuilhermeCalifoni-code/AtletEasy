import mysql.connector
from flask import flash
from mysql.connector import Error
from config import db_config

def get_db_connection():
    try:
        conexao = mysql.connector.connect(**db_config)
        if conexao.is_connected():
            return conexao
    except Error as err:
        print(flash(f'Erro ao conectar ao banco de dados: {err}', 'danger'))
    return None
