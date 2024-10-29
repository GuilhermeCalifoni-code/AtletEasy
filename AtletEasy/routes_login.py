import mysql.connector
from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from db import get_db_connection
from mysql.connector import Error


login_bp = Blueprint('login', __name__)

@login_bp.route('/')
def home():
    return render_template('login.html')

# Página de login
@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['senha']
        
        try:
            with mysql.connector.connect(get_db_connection) as conexao:
                with conexao.cursor(dictionary=True) as cursor:
                    # Verificando o login do atleta
                    query_atleta = "SELECT idAtleta, Usuario FROM cadatleta WHERE Usuario = %s AND Senha = %s"
                    cursor.execute(query_atleta, (username, password))
                    atleta = cursor.fetchone()
                    
                    if atleta:
                        session['usuario'] = atleta['Usuario']  # Armazena o nome do usuário na sessão
                        session['usuario_id'] = atleta['idAtleta']  # Armazena o idAtleta na sessão
                        session['tipo_usuario'] = 'atleta'
                        flash('Login como atleta realizado com sucesso!', 'success')
                        return redirect(url_for('home_atleta'))
                    
                    # Verificando o login do clube
                    query_clube = "SELECT idClube, Usuario FROM cadclube WHERE Usuario = %s AND Senha = %s"
                    cursor.execute(query_clube, (username, password))
                    clube = cursor.fetchone()
                    
                    if clube:
                        session['usuario'] = clube['Usuario']  # Armazena o nome do usuário na sessão
                        session['usuario_id'] = clube['idClube']  # Armazena o idClube na sessão
                        session['tipo_usuario'] = 'clube'
                        flash('Login como clube realizado com sucesso!', 'success')
                        return redirect(url_for('home_clube'))
                    
                    flash('Usuário ou senha incorretos!', 'danger')
                    return redirect(url_for('login'))
                
        except Error as err:
            flash(f'Erro ao tentar fazer login: {err}', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')