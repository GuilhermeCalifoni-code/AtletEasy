import datetime
from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from db import get_db_connection
from mysql.connector import Error

clube_bp = Blueprint('clube', __name__)

@clube_bp.route('/cadastro-clube', methods=['GET', 'POST'])
def cadastro_clube():
    if request.method == 'POST':
        # Dados do formulário
        cnpj = request.form.get('CNPJ')
        nome_clube = request.form.get('nomeClube')
        inscricao_estadual = request.form.get('inscricaoEstadual')
        cep = request.form.get('cep')
        endereco = request.form.get('endereco')
        usuario = request.form.get('usuario')
        nome_fantasia = request.form.get('nomeFantasia')
        numero = request.form.get('numeroEndereco')
        complemento = request.form.get('complemento', '')
        senha = request.form.get('Senha')
        tipo_usuario = 'clube'

        try:
            # Conecta ao banco de dados e executa o comando SQL
            with get_db_connection() as conexao:
                with conexao.cursor() as cursor:
                    query = """
                        INSERT INTO cadclube (
                            Usuario, Senha, NomeClube, Endereco, CNPJ,
                            CEP, NumeroEndereco, Complemento, nome_fantasia, inscricao_estadual, tipo_usuario
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    valores = (usuario, senha, nome_clube, endereco, cnpj, cep, numero, complemento, nome_fantasia, inscricao_estadual, tipo_usuario)
                    cursor.execute(query, valores)
                    conexao.commit()  # Salva as mudanças no banco
                    flash('Clube cadastrado com sucesso!', 'success')
                    
                    # Redireciona para a página de login
                    return redirect(url_for('login.login'))
        except Error as err:
            # Exibe uma mensagem de erro caso o cadastro falhe
            flash(f'Erro ao cadastrar o clube: {err}', 'danger')

    # Renderiza a página de cadastro de clube
    return render_template('CadClube.html')


# Página de pagamento para clube
@clube_bp.route('/paga-clube')
def paga_clube():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login.login'))
    return render_template('pgclube.html')

# Página Home do Clube

@clube_bp.route('/home-clube')
def home_clube():
    # Verifica se o usuário está logado
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login.login'))

    try:
        with get_db_connection() as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Conta o número total de peneiras
                query_count = "SELECT COUNT(*) as total_peneiras FROM peneira WHERE NomeClube = %s"
                cursor.execute(query_count, (session['usuario'],))
                result = cursor.fetchone()
                total_peneiras = result['total_peneiras'] if result else 0

                # Seleciona as peneiras associadas ao clube
                query_peneiras = "SELECT * FROM peneira WHERE NomeClube = %s"
                cursor.execute(query_peneiras, (session['usuario'],))
                peneiras = cursor.fetchall()

                return render_template('HomeClube.html', peneiras=peneiras, total_peneiras=total_peneiras)
    except Error as err:
        flash(f'Erro ao recuperar as peneiras: {err}', 'danger')
        return redirect(url_for('clube.home_clube'))  # Redireciona em caso de erro

# Rota para criar uma peneira
@clube_bp.route('/criar-peneira', methods=['GET', 'POST'])
def criar_peneira():
    if request.method == 'POST':
        if 'usuario' not in session:
            flash('Você precisa estar logado para criar uma peneira.', 'warning')
            return redirect(url_for('login.login'))

        # Dados do formulário
        nome_clube = session['usuario']
        esporte_peneira = request.form['esportePeneira']
        local_peneira = request.form['localPeneira']
        data_inicio = request.form['dataInicio']
        horario = request.form['horario']
        quantidade_maxima = int(request.form['quantidadeMaxima'])
        status = int(request.form['status'])
        cep = request.form['cep']

        # Conversão de data e hora para o formato DATETIME
        try:
            data_inicio_formatada = datetime.strptime(data_inicio, '%Y-%m-%d')
            datetime_horario = datetime.strptime(f'{data_inicio} {horario}', '%Y-%m-%d %H:%M')
        except ValueError as e:
            flash(f"Erro no formato de data ou hora: {e}", 'danger')
            return redirect(url_for('clube.criar_peneira'))

        try:
            with get_db_connection() as conexao:
                with conexao.cursor() as cursor:
                    query = """
                        INSERT INTO peneira (
                            NomeClube, esportePeneira, Local, DataInicio, Horario, 
                            QuantidadeMaxima, status, CEP
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    valores = (nome_clube, esporte_peneira, local_peneira, data_inicio_formatada, datetime_horario, quantidade_maxima, status, cep)
                    cursor.execute(query, valores)
                    conexao.commit()
                    flash('Peneira cadastrada com sucesso!', 'success')
                    return redirect(url_for('clube.home_clube'))
        except Error as err:
            flash(f'Erro ao cadastrar a peneira: {err}', 'danger')

    return render_template('criarPeneira.html')

# Rota para gerenciar peneiras
@clube_bp.route('/gerenciar-peneira')
def gerenciar_peneira():
    try:
        with get_db_connection() as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                query = "SELECT * FROM peneira"
                cursor.execute(query)
                peneiras = cursor.fetchall()

                for peneira in peneiras:
                    if isinstance(peneira['Horario'], datetime.timedelta):
                        horas, resto = divmod(peneira['Horario'].seconds, 3600)
                        minutos, _ = divmod(resto, 60)
                        peneira['Horario'] = f'{horas:02}:{minutos:02}'

                return render_template('gerenciarPeneira.html', peneiras=peneiras)
    except Error as err:
        flash(f'Erro ao recuperar as peneiras: {err}', 'danger')
        return redirect(url_for('clube.home_clube'))

# Rota para visualizar ficha de jogo de uma peneira
@clube_bp.route('/ficha-jogo/<int:idPeneira>')
def ficha_jogo(idPeneira):
    try:
        with get_db_connection() as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                query_peneira = """
                    SELECT NomeClube, DataInicio, esportePeneira, Local, CEP 
                    FROM peneira 
                    WHERE idPeneira = %s
                """
                cursor.execute(query_peneira, (idPeneira,))
                peneira = cursor.fetchone()

                if not peneira:
                    flash('Peneira não encontrada.', 'danger')
                    return redirect(url_for('clube.home_clube'))

                query_atletas = """
                    SELECT a.Nome, a.Sobrenome, i.NumeroCamisa, i.Posicao, i.atletaAvaliacao
                    FROM cadatleta a
                    JOIN infoatleta i ON a.idAtleta = i.idAtleta
                    WHERE i.idPeneira = %s
                """
                cursor.execute(query_atletas, (idPeneira,))
                atletas = cursor.fetchall()

        return render_template('fichaJogo.html', peneira=peneira, atletas=atletas)
    except Error as err:
        flash(f'Erro ao buscar a ficha de jogo: {err}', 'danger')
        return redirect(url_for('clube.home_clube'))

# Rota para visualizar atletas inscritos em uma peneira específica
@clube_bp.route('/atletas-inscritos/<int:idPeneira>')
def atletas_inscritos(idPeneira):
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'clube':
        flash('Você precisa estar logado como clube para acessar esta página.', 'warning')
        return redirect(url_for('login.login'))

    try:
        with get_db_connection() as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                query = """
                SELECT a.Nome, a.Sobrenome, a.DataDeNascimento, a.CPF, i.Posicao, i.Altura, i.Peso, i.Experiencia, 
                       i.Velocidade, i.Tecnica, i.VisaoDeJogo, i.Gols, i.Assistencias, i.Cartoes
                FROM inscricoes ins
                JOIN cadatleta a ON ins.idAtleta = a.idAtleta
                LEFT JOIN infoatleta i ON a.idAtleta = i.idAtleta
                WHERE ins.idPeneira = %s
                """
                cursor.execute(query, (idPeneira,))
                atletas = cursor.fetchall()

                if not atletas:
                    flash('Nenhum atleta inscrito nesta peneira.', 'info')
                    return redirect(url_for('clube.home_clube'))

                return render_template('atletasInscritos.html', atletas=atletas)
    except Error as err:
        flash(f'Erro ao recuperar os atletas inscritos: {err}', 'danger')
        return redirect(url_for('clube.home_clube'))
    


