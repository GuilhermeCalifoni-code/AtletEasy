import mysql.connector
from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from db import get_db_connection
from mysql.connector import Error
import timedelta # type: ignore
import datetime

clube_bp = Blueprint('clube', __name__)




@clube_bp.route('/cadastro-clube', methods=['GET', 'POST'])
def cadastro_clube():
    if request.method == 'POST':
        try:
            # Coleta os dados do formulário para cadastro do clube
            cnpj = request.form.get('CNPJ')
            nome_clube = request.form.get('nomeClube')
            inscricao_estadual = request.form.get('inscricaoEstadual')
            cep = request.form.get('cep')
            endereco = request.form.get('endereco')
            usuario = request.form.get('usuario')  # Correspondência correta com o formulário HTML
            nome_fantasia = request.form.get('nomeFantasia')  # Correspondência correta com o formulário HTML
            numero = request.form.get('numeroEndereco')
            complemento = request.form.get('complemento', '')
            senha = request.form.get('Senha')  # Correspondência correta com o formulário HTML
            tipo_usuario = 'clube'  # Definindo tipo de usuário como 'clube'

            # Adicionando verificação para os campos
            if not (cnpj and nome_clube and inscricao_estadual and cep and endereco and usuario and nome_fantasia and numero and senha):
                flash('Todos os campos obrigatórios devem ser preenchidos!', 'warning')
                return redirect(url_for('cadastro_clube'))

            # Log dos valores para garantir que estão corretos
            print(f"Dados recebidos: CNPJ={cnpj}, Nome Clube={nome_clube}, Usuário={usuario}, Senha={senha}")

            # Inserção no banco de dados
            with mysql.connector.connect(get_db_connection) as conexao:
                with conexao.cursor() as cursor:
                    query = """
                        INSERT INTO cadclube (
                            Usuario, Senha, NomeClube, Endereco, CNPJ,
                            CEP, NumeroEndereco, Complemento, nome_fantasia, inscricao_estadual, tipo_usuario
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    valores = (
                        usuario, senha, nome_clube, endereco, cnpj,
                        cep, numero, complemento, nome_fantasia, inscricao_estadual, tipo_usuario
                    )
                    cursor.execute(query, valores)
                    conexao.commit()

                    flash('Clube cadastrado com sucesso!', 'success')
                    return redirect(url_for('login'))

        except Error as err:
            flash(f'Erro ao cadastrar o clube: {err}', 'danger')

    return render_template('CadClube.html')



# Página de pagamento para clube
@clube_bp.route('/paga-clube')
def paga_clube():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    return render_template('pgclube.html')



# Página Home Clube
@clube_bp.route('/home-clube')
def home_clube():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    try:
        with mysql.connector.connect(get_db_connection) as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Contar o número total de peneiras
                query_count = "SELECT COUNT(*) as total_peneiras FROM peneira WHERE NomeClube = %s"
                cursor.execute(query_count, (session['usuario'],))
                result = cursor.fetchone()
                total_peneiras = result['total_peneiras'] if result else 0

                # Selecionar as peneiras associadas ao clube
                query_peneiras = "SELECT * FROM peneira WHERE NomeClube = %s"
                cursor.execute(query_peneiras, (session['usuario'],))
                peneiras = cursor.fetchall()  # Buscar todas as peneiras

                # Renderizar o template e passar os dados das peneiras
                return render_template('HomeClube.html', peneiras=peneiras, total_peneiras=total_peneiras)

    except Error as err:
        flash(f'Erro ao recuperar as peneiras: {err}', 'danger')
        return redirect(url_for('home'))




# Rota para ficha de jogo
@clube_bp.route('/ficha-jogo/<int:idPeneira>')
def ficha_jogo(idPeneira):
    conexao = get_db_connection()
    if not conexao:
        return redirect(url_for('home_clube'))

    try:
        with conexao.cursor(dictionary=True) as cursor:
            # Consultar detalhes da peneira (jogo)
            query_peneira = """
                SELECT NomeClube, DataInicio, esportePeneira, Local, CEP 
                FROM peneira 
                WHERE idPeneira = %s
            """
            cursor.execute(query_peneira, (idPeneira,))
            peneira = cursor.fetchone()

            if not peneira:
                flash('Peneira não encontrada.', 'danger')
                return redirect(url_for('home_clube'))

            # Consultar avaliações dos atletas na peneira
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
    finally:
        if conexao.is_connected():
            conexao.close()

    return redirect(url_for('home_clube'))



# Rota para gerenciar peneira
@clube_bp.route('/gerenciar-peneira', methods=['GET'])
def gerenciar_peneira():
    try:
        # Conectando ao banco de dados
        with mysql.connector.connect(get_db_connection) as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Buscando todas as peneiras cadastradas no banco de dados
                query = "SELECT * FROM peneira"
                cursor.execute(query)
                peneiras = cursor.fetchall()

                # Formatando o horário para string (HH:MM) para evitar erro com timedelta
                for peneira in peneiras:
                    if isinstance(peneira['Horario'], timedelta):
                        horas, resto = divmod(peneira['Horario'].seconds, 3600)
                        minutos, _ = divmod(resto, 60)
                        peneira['Horario'] = f'{horas:02}:{minutos:02}'
                
                # Renderiza a página HTML passando os dados das peneiras
                return render_template('gerenciarPeneira.html', peneiras=peneiras)

    except Error as err:
        flash(f'Erro ao recuperar as peneiras: {err}', 'danger')
        return redirect(url_for('home'))




@clube_bp.route('/criar-peneira', methods=['GET', 'POST'])
def criar_peneira():
    if request.method == 'POST':
        # Verifique se o nome do clube está na sessão
        if 'usuario' not in session:
            flash('Você precisa estar logado para criar uma peneira.', 'warning')
            return redirect(url_for('login'))

        # Coletando dados do formulário
        nome_clube = session['usuario']
        esporte_peneira = request.form['esportePeneira']
        local_peneira = request.form['localPeneira']
        data_inicio = request.form['dataInicio']
        horario = request.form['horario']
        quantidade_maxima = int(request.form['quantidadeMaxima'])
        status = int(request.form['status'])
        cep = request.form['cep']

        # Conversão explícita da data e do horário para o formato DATETIME
        try:
            data_inicio_formatada = datetime.strptime(data_inicio, '%Y-%m-%d')
            # Combine a data e a hora para criar um valor de DATETIME
            datetime_horario = datetime.strptime(f'{data_inicio} {horario}', '%Y-%m-%d %H:%M')
        except ValueError as e:
            flash(f"Erro no formato de data ou hora: {e}", 'danger')
            return redirect(url_for('criar_peneira'))

        # Inserção no banco de dados
        conexao = get_db_connection()
        if conexao is None:
            flash('Erro ao conectar ao banco de dados.', 'danger')
            return redirect(url_for('criar_peneira'))

        try:
            with conexao.cursor() as cursor:
                query = """
                    INSERT INTO peneira (
                        NomeClube, esportePeneira, Local, DataInicio, Horario, 
                        QuantidadeMaxima, status, CEP
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (
                    nome_clube, esporte_peneira, local_peneira, data_inicio_formatada, datetime_horario, 
                    quantidade_maxima, status, cep
                )
                cursor.execute(query, valores)
                
                # Fazendo o commit para confirmar as alterações no banco de dados
                conexao.commit()

                flash('Peneira cadastrada com sucesso!', 'success')
                return redirect(url_for('criar_peneira'))

        except Error as err:
            # Exibe o erro no console para facilitar o debug
            print(f'Erro ao cadastrar a peneira: {err}')
            flash(f'Erro ao cadastrar a peneira: {err}', 'danger')
        finally:
            if conexao.is_connected():
                conexao.close()

    return render_template('criarPeneira.html')



@clube_bp.route('/atletas-inscritos/<int:idPeneira>')
def atletas_inscritos(idPeneira):
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'clube':
        flash('Você precisa estar logado como clube para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    try:
        # Conectando ao banco de dados
        with mysql.connector.connect(get_db_connection) as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Buscando todos os atletas inscritos na peneira específica
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

            # Se não houver atletas inscritos, informar o clube
            if not atletas:
                flash('Nenhum atleta inscrito nesta peneira.', 'info')
                return redirect(url_for('home_clube'))

            # Renderizar a página de visualização dos atletas inscritos
            return render_template('atletasInscritos.html', atletas=atletas)

    except Error as err:
        flash(f'Erro ao recuperar os atletas inscritos: {err}', 'danger')
        return redirect(url_for('home_clube'))

