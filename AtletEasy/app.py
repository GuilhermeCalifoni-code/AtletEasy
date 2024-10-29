from flask import Flask, render_template, request, redirect, flash, url_for, session
import mysql.connector
from mysql.connector import Error
from datetime import datetime, timedelta
from config.py import db_config # type: ignore



app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Certifique-se de que a secret key está configurada

@app.route('/quem-voce')
def quem_voce():
    # Definindo o título e a mensagem dinamicamente
    titulo = "Quem é você?"
    mensagem = "Escolha uma das opções abaixo para continuar o cadastro."

    # Renderizando o template HTML e passando os valores de título e mensagem
    return render_template('QuemVoce.html', titulo=titulo, mensagem=mensagem)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)