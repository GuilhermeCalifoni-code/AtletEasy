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
            # Tenta obter a conexão com o banco de dados
            conexao = get_db_connection()
            if conexao is None:
                flash('Erro ao conectar ao banco de dados.', 'danger')
                return redirect(url_for('login.login'))
            
            with conexao.cursor(dictionary=True) as cursor:
                # Consulta para buscar atleta
                query_atleta = "SELECT idAtleta, Usuario FROM cadatleta WHERE Usuario = %s AND Senha = %s"
                cursor.execute(query_atleta, (username, password))
                atleta = cursor.fetchone()
                
                if atleta:
                    session['usuario'] = atleta['Usuario']
                    session['usuario_id'] = atleta['idAtleta']
                    session['tipo_usuario'] = 'atleta'
                    print("Sessão configurada após login como atleta:", session)  # Adiciona esta linha para depuração
                    flash('Login como atleta realizado com sucesso!', 'success')
                    return redirect(url_for('atleta.home_atleta'))
                
                # Consulta para buscar clube
                query_clube = "SELECT idClube, Usuario FROM cadclube WHERE Usuario = %s AND Senha = %s"
                cursor.execute(query_clube, (username, password))
                clube = cursor.fetchone()
                
                if clube:
                    session['usuario'] = clube['Usuario']
                    session['usuario_id'] = clube['idClube']
                    session['tipo_usuario'] = 'clube'
                    print("Sessão configurada após login como clube:", session)  # Adiciona esta linha para depuração
                    flash('Login como clube realizado com sucesso!', 'success')
                    return redirect(url_for('clube.home_clube'))
                
                flash('Usuário ou senha incorretos!', 'danger')
                return redirect(url_for('login.login'))
        
        except Error as err:
            flash(f'Erro ao tentar fazer login: {err}', 'danger')
            return redirect(url_for('login.login'))
        
        finally:
            if conexao and conexao.is_connected():
                conexao.close()  # Certifique-se de fechar a conexão ao final

    return render_template('login.html')