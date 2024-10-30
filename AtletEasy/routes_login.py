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
            with get_db_connection() as conexao:
                with conexao.cursor(dictionary=True) as cursor:
                    query_atleta = "SELECT idAtleta, Usuario FROM cadatleta WHERE Usuario = %s AND Senha = %s"
                    cursor.execute(query_atleta, (username, password))
                    atleta = cursor.fetchone()
                    
                    if atleta:
                        session['usuario'] = atleta['Usuario']
                        session['usuario_id'] = atleta['idAtleta']
                        session['tipo_usuario'] = 'atleta'
                        flash('Login como atleta realizado com sucesso!', 'success')
                        return render_template('HomeAtleta.html') # Alteração feita aqui
                    
                    query_clube = "SELECT idClube, Usuario FROM cadclube WHERE Usuario = %s AND Senha = %s"
                    cursor.execute(query_clube, (username, password))
                    clube = cursor.fetchone()
                    
                    if clube:
                        session['usuario'] = clube['Usuario']
                        session['usuario_id'] = clube['idClube']
                        session['tipo_usuario'] = 'clube'
                        flash('Login como clube realizado com sucesso!', 'success')
                        return redirect(url_for('clube.home_clube'))  # Alteração feita aqui
                    
                    flash('Usuário ou senha incorretos!', 'danger')
                    return redirect(url_for('login.login'))
                
        except Error as err:
            flash(f'Erro ao tentar fazer login: {err}', 'danger')
            return redirect(url_for('login.login'))

    return render_template('login.html')


