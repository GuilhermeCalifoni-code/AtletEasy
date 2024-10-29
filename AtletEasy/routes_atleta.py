from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from db import get_db_connection
import mysql.connector
from mysql.connector import Error

atleta_bp = Blueprint('atleta', __name__)

# Rota para cadastro de atleta
@atleta_bp.route('/cadastro-atleta', methods=['GET', 'POST'])
def cadastro_atleta():
    if request.method == 'POST':
        nome = request.form['nomeAtleta']
        sobrenome = request.form['sobrenome']
        cpf = request.form['cpf']
        data_nascimento = request.form['dataNascimento']
        cep = request.form['cep']
        endereco = request.form['endereco']
        numero = request.form['numeroEndereco']
        complemento = request.form.get('complemento', '')
        usuario = request.form['usuario']
        senha = request.form['senha']

        try:
            with mysql.connector.connect(get_db_connection) as conexao:
                with conexao.cursor() as cursor:
                    query = """
                        INSERT INTO cadatleta (
                            Nome, Sobrenome, CPF, DataDeNascimento, CEP, 
                            Endereco, NumeroEndereco, Complemento, Usuario, Senha
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    valores = (
                        nome, sobrenome, cpf, data_nascimento, cep, 
                        endereco, numero, complemento, usuario, senha
                    )
                    cursor.execute(query, valores)
                    conexao.commit()

                    # Redireciona para a tela de login após o cadastro com sucesso
                    flash('Atleta cadastrado com sucesso! Faça login para continuar.', 'success')
                    return redirect(url_for('login'))

        except Error as err:
            flash(f'Erro ao cadastrar o atleta: {err}', 'danger')
            return redirect(url_for('cadastro_atleta'))

    return render_template('cadatleta.html')

# Página de pagamento para atleta
@atleta_bp.route('/paga-atleta')
def paga_atleta():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    return render_template('pgatleta.html')

# Página Home Atleta
@atleta_bp.route('/home-atleta')
def home_atleta():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    print(f"Usuário ID: {session['usuario_id']}")  # Verifica se o usuário está logado
    return render_template('HomeAtleta.html')

# Página de perfil do atleta (visualização)
@atleta_bp.route('/perfil-atleta')
def perfil_atleta():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']

    try:
        # Conectando ao banco de dados
        with mysql.connector.connect(get_db_connection) as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Query para buscar os dados do perfil do atleta
                query = """
                SELECT c.Nome, c.Sobrenome, c.DataDeNascimento, c.Endereco, c.CPF, c.CEP,
                       i.Posicao, i.Altura, i.Peso, i.Experiencia, i.SobreMim, 
                       i.Velocidade, i.Tecnica, i.VisaoDeJogo, i.Gols, i.Assistencias, i.Cartoes
                FROM cadatleta c
                LEFT JOIN infoatleta i ON c.idAtleta = i.idAtleta
                WHERE c.idAtleta = %s
                """
                cursor.execute(query, (usuario_id,))
                atleta = cursor.fetchone()

            if not atleta:
                flash('Atleta não encontrado.', 'danger')
                return redirect(url_for('home'))

            # Renderizando o template do perfil do atleta com os dados do banco
            return render_template('perfilAtleta.html', atleta=atleta)

    except Error as err:
        flash(f'Erro ao recuperar o perfil do atleta: {err}', 'danger')
        return redirect(url_for('home'))

# editar o perfil
@atleta_bp.route('/editar-perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']

    if request.method == 'POST':
        # Coleta dos dados do formulário para atualizar no banco
        posicao = request.form['Posicao']
        altura = request.form['Altura']
        peso = request.form['Peso']
        experiencia = request.form['Experiencia']
        sobre_mim = request.form['SobreMim']
        velocidade = int(request.form['Velocidade'])
        tecnica = int(request.form['Tecnica'])
        visao_de_jogo = int(request.form['VisaoDeJogo'])
        gols = int(request.form['Gols'])
        assistencias = int(request.form['Assistencias'])
        cartoes = int(request.form['Cartoes'])

        try:
            # Conectando ao banco de dados
            with mysql.connector.connect(get_db_connection) as conexao:
                with conexao.cursor() as cursor:
                    # Atualizando as informações do atleta na tabela infoatleta
                    query = """
                    UPDATE infoatleta 
                    SET Posicao=%s, Altura=%s, Peso=%s, Experiencia=%s, 
                        SobreMim=%s, Velocidade=%s, Tecnica=%s, VisaoDeJogo=%s, 
                        Gols=%s, Assistencias=%s, Cartoes=%s
                    WHERE idAtleta = %s
                    """
                    valores = (posicao, altura, peso, experiencia, sobre_mim, velocidade, tecnica, visao_de_jogo, gols, assistencias, cartoes, usuario_id)
                    cursor.execute(query, valores)
                    conexao.commit()

                    flash('Perfil atualizado com sucesso!', 'success')

                    # Redireciona o usuário para a página de perfil após salvar as alterações
                    return redirect(url_for('perfil_atleta'))

        except Error as err:
            flash(f'Erro ao atualizar o perfil: {err}', 'danger')
            return redirect(url_for('editar_perfil'))

    # Se for um GET, exibe o formulário com os dados atuais
    try:
        # Conectando ao banco de dados para carregar os dados do atleta no formulário
        with mysql.connector.connect(get_db_connection) as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                query = """
                SELECT Posicao, Altura, Peso, Experiencia, SobreMim, 
                       Velocidade, Tecnica, VisaoDeJogo, Gols, Assistencias, Cartoes
                FROM infoatleta WHERE idAtleta = %s
                """
                cursor.execute(query, (usuario_id,))
                atleta = cursor.fetchone()

            return render_template('editarPerfil.html', atleta=atleta)

    except Error as err:
        flash(f'Erro ao carregar o perfil para edição: {err}', 'danger')
        return redirect(url_for('perfil_atleta'))

# aqui o atleta ira se inscrever em peneiras criadas pelo CLUBE
@atleta_bp.route('/inscrever-peneira', methods=['POST'])
def inscrever_peneira():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para se inscrever em uma peneira.', 'warning')
        return redirect(url_for('login'))

    idPeneira = request.form.get('idPeneira')  # Pega o ID da peneira selecionada

    if not idPeneira:
        flash('Nenhuma peneira selecionada.', 'warning')
        return redirect(url_for('visualizar_peneiras'))

    try:
        # Conectando ao banco de dados
        with mysql.connector.connect(get_db_connection) as conexao:
            with conexao.cursor() as cursor:
                # Inscreve o usuário na peneira
                query = """
                INSERT INTO inscricoes (idAtleta, idPeneira)
                VALUES (%s, %s)
                """
                cursor.execute(query, (session['usuario_id'], idPeneira))
                conexao.commit()

        flash('Inscrição realizada com sucesso!', 'success')
        return redirect(url_for('visualizar_peneiras'))

    except Error as err:
        flash(f'Erro ao realizar a inscrição: {err}', 'danger')
        return redirect(url_for('visualizar_peneiras'))


@atleta_bp.route('/visualizar-peneiras')
def visualizar_peneiras():
    try:
        # Conectando ao banco de dados
        with mysql.connector.connect(get_db_connection) as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Selecionando todos os registros da tabela de peneiras
                query = "SELECT * FROM peneira"
                cursor.execute(query)
                peneiras = cursor.fetchall()  # Busca todos os resultados

                # Verificando se há peneiras disponíveis
                if not peneiras:
                    flash('Nenhuma peneira cadastrada.', 'info')
                    return redirect(url_for('home_atleta'))

                # Passa a lista de peneiras para o template
                return render_template('visualizarPeneiras.html', peneiras=peneiras)

    except Error as err:
        flash(f'Erro ao recuperar as peneiras: {err}', 'danger')
        return redirect(url_for('home_atleta'))


