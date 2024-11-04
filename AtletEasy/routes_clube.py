import datetime
from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from db import get_db_connection
from mysql.connector import Error

clube_bp = Blueprint('clube', __name__)

#EXCLUIR PENEIRA
@clube_bp.route('/excluir-peneira/<int:idPeneira>', methods=['POST'])
def excluir_peneira(idPeneira):
    try:
        with get_db_connection() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute("DELETE FROM peneira WHERE idPeneira = %s", (idPeneira,))
                conexao.commit()
                flash('Peneira excluída com sucesso!', 'success')
    except Error as err:
        flash(f'Erro ao excluir a peneira: {err}', 'danger')
    return redirect(url_for('clube.gerenciar_peneira'))

#INICIAR PENEIRA
@clube_bp.route('/encerrar-iniciar-peneira/<int:idPeneira>', methods=['POST'])
def encerrar_iniciar_peneira(idPeneira):
    novo_status = 'Fechado' if request.form.get('status') == 'Aberto' else 'Aberto'
    try:
        with get_db_connection() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute("UPDATE peneira SET status = %s WHERE idPeneira = %s", (novo_status, idPeneira))
                conexao.commit()
                flash(f'Peneira {novo_status.lower()} com sucesso!', 'success')
    except Error as err:
        flash(f'Erro ao alterar status da peneira: {err}', 'danger')
    return redirect(url_for('clube.gerenciar_peneira'))

#EDITAR PENEIRA
@clube_bp.route('/editar-peneira/<int:idPeneira>', methods=['GET', 'POST'])
def editar_peneira(idPeneira):
    if request.method == 'POST':
        # Atualiza os dados da peneira
        esporte_peneira = request.form.get('esportePeneira')
        endereco = request.form.get('Endereco')
        data_inicio = request.form.get('DataInicio')
        data_final = request.form.get('DataFinal')
        horario = request.form.get('Horario') + ":00" if request.form.get('Horario') else None
        quantidade_maxima = int(request.form.get('QuantidadeMaxima'))
        estado = request.form.get('Estado')
        cidade = request.form.get('Cidade')
        status = request.form.get('status')  # Adicionando campo status

        try:
            with get_db_connection() as conexao:
                with conexao.cursor() as cursor:
                    query = """
                    UPDATE peneira SET esportePeneira=%s, Endereco=%s, DataInicio=%s, DataFinal=%s, 
                                        Horario=%s, QuantidadeMaxima=%s, Estado=%s, Cidade=%s, status=%s
                    WHERE idPeneira=%s
                    """
                    cursor.execute(query, (esporte_peneira, endereco, data_inicio, data_final, 
                                           horario, quantidade_maxima, estado, cidade, status, idPeneira))
                    conexao.commit()
                    flash('Peneira editada com sucesso!', 'success')
        except Error as err:
            flash(f'Erro ao editar a peneira: {err}', 'danger')
        return redirect(url_for('clube.gerenciar_peneira'))

    try:
        with get_db_connection() as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM peneira WHERE idPeneira = %s", (idPeneira,))
                peneira = cursor.fetchone()
    except Error as err:
        flash(f'Erro ao carregar a peneira: {err}', 'danger')
        return redirect(url_for('clube.gerenciar_peneira'))
    
    return render_template('editarPeneira.html', peneira=peneira)

#AVALIAR ATLETA
@clube_bp.route('/avaliar-atleta/<int:idPeneira>', methods=['POST'])
def avaliar_atleta(idPeneira):
    id_atleta = request.form.get('idAtleta')
    status_avaliacao = request.form.get('statusAvaliacao')  # Aprovado ou Reprovado
    
    try:
        with get_db_connection() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute("UPDATE infoatleta SET status_avaliacao = %s WHERE idAtleta = %s AND idPeneira = %s",
                               (status_avaliacao, id_atleta, idPeneira))
                conexao.commit()
                flash(f'Avaliação do atleta {status_avaliacao} com sucesso!', 'success')
    except Error as err:
        flash(f'Erro ao avaliar o atleta: {err}', 'danger')
    return redirect(url_for('clube.ficha_jogo', idPeneira=idPeneira))

#CADASTRO CLUBE
@clube_bp.route('/cadastro-clube', methods=['GET', 'POST'])
def cadastro_clube():
    if request.method == 'POST':
        # Dados do formulário
        cnpj = request.form.get('CNPJ')
        nome_clube = request.form.get('nomeClube')
        inscricao_estadual = request.form.get('inscricaoEstadual')
        endereco = request.form.get('endereco')
        usuario = request.form.get('usuario')
        nome_fantasia = request.form.get('nomeFantasia')
        numero = request.form.get('numeroEndereco')
        complemento = request.form.get('complemento', '')
        senha = request.form.get('Senha')

        try:
            # Conecta ao banco de dados e executa o comando SQL
            with get_db_connection() as conexao:
                with conexao.cursor() as cursor:
                    query = """
                        INSERT INTO cadclube (
                            Usuario, Senha, NomeClube, Endereco, CNPJ,
                            NumeroEndereco, Complemento, nome_fantasia, inscricao_estadual
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    valores = (usuario, senha, nome_clube, endereco, cnpj, numero, complemento, nome_fantasia, inscricao_estadual)
                    cursor.execute(query, valores)
                    conexao.commit()  # Salva as mudanças no banco
                    flash('Clube cadastrado com sucesso!', 'success')
                    
                    # Redireciona para a página de login
                    return redirect(url_for('login.login'))
        except Error as err:
            # Exibe uma mensagem de erro caso o cadastro falhe
            flash(f'Erro ao cadastrar o clube: {err}', 'danger')
            print(f"Erro ao cadastrar o clube: {err}")

    # Renderiza a página de cadastro de clube
    return render_template('CadClube.html')

# Página de pagamento para clube
@clube_bp.route('/paga-clube')
def paga_clube():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login.login'))
    return render_template('pgclube.html')

@clube_bp.route('/home')
def home_clube():
    if 'usuario_id' not in session or session.get('tipo_usuario') != 'clube':
        flash('Você precisa estar logado como clube para acessar esta página.', 'warning')
        return redirect(url_for('login.login'))
    
    try:
        with get_db_connection() as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                id_clube = session.get('usuario_id')
                
                query_count = "SELECT COUNT(*) as total_abertas FROM peneira WHERE idClube = %s AND status = 'Aberto'"
                cursor.execute(query_count, (id_clube,))
                total_abertas = cursor.fetchone().get('total_abertas', 0)

                query_peneiras = """
                    SELECT p.*, c.NomeClube 
                    FROM peneira p 
                    JOIN cadclube c ON p.idClube = c.idClube 
                    WHERE p.idClube = %s
                """
                cursor.execute(query_peneiras, (id_clube,))
                peneiras = cursor.fetchall()

        return render_template('HomeClube.html', peneiras=peneiras, total_abertas=total_abertas)
    except Error as err:
        flash(f'Erro ao recuperar as peneiras: {err}', 'danger')
        return redirect(url_for('clube.home_clube'))
    
@clube_bp.route('/criar-peneira', methods=['GET', 'POST'])
def criar_peneira():
    if request.method == 'POST':
        id_clube = session.get('usuario_id')
        esporte_peneira = request.form.get('esportePeneira')
        endereco = request.form.get('Endereco')
        data_inicio = request.form.get('DataInicio')
        data_final = request.form.get('DataFinal')
        horario = request.form.get('Horario') + ":00" if request.form.get('Horario') else None
        quantidade_maxima = int(request.form.get('QuantidadeMaxima'))
        status = request.form.get('status')  # 'Aberto' ou 'Fechado'
        estado = request.form.get('Estado')
        cidade = request.form.get('Cidade')

        quantidade_maxima = max(10, min(quantidade_maxima, 50))

        try:
            with get_db_connection() as conexao:
                with conexao.cursor() as cursor:
                    query = """
                        INSERT INTO peneira (
                            idClube, esportePeneira, Endereco, DataInicio, DataFinal, Horario, 
                            QuantidadeMaxima, status, Estado, Cidade
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    valores = (id_clube, esporte_peneira, endereco, data_inicio, 
                               data_final, horario, quantidade_maxima, 
                               status, estado, cidade)
                    cursor.execute(query, valores)
                    conexao.commit()
                    flash('Peneira cadastrada com sucesso!', 'success')
                    return redirect(url_for('clube.gerenciar_peneira'))
        except Error as err:
            flash(f'Erro ao cadastrar a peneira: {err}', 'danger')

    return render_template('criarPeneira.html')

# Rota para gerenciar peneiras
@clube_bp.route('/gerenciar-peneira')
def gerenciar_peneira():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login.login'))
    
    try:
        with get_db_connection() as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                id_clube = session.get('usuario_id')
                
                query_peneiras = "SELECT * FROM peneira WHERE idClube = %s"
                cursor.execute(query_peneiras, (id_clube,))
                peneiras = cursor.fetchall()
                
        return render_template('gerenciarPeneira.html', peneiras=peneiras)
    except Error as err:
        flash(f'Erro ao recuperar as peneiras: {err}', 'danger')
        return redirect(url_for('clube.home_clube'))

# Rota para visualizar ficha de jogo de uma peneira
@clube_bp.route('/ficha-jogo/<int:idPeneira>', methods=['GET', 'POST'])
def ficha_jogo(idPeneira):
    if request.method == 'POST':
        # Processa a avaliação dos atletas
        try:
            with get_db_connection() as conexao:
                with conexao.cursor() as cursor:
                    for key, value in request.form.items():
                        if key.startswith('statusAvaliacao_'):
                            id_atleta = key.split('_')[1]
                            status_avaliacao = value
                            cursor.execute("""
                                UPDATE infoatleta SET status_avaliacao = %s WHERE idAtleta = %s
                            """, (status_avaliacao, id_atleta))
                    conexao.commit()
                    flash('Avaliações salvas com sucesso!', 'success')
        except Error as err:
            flash(f'Erro ao salvar as avaliações: {err}', 'danger')
        return redirect(url_for('clube.ficha_jogo', idPeneira=idPeneira))

    # Método GET: renderiza a página
    try:
        with get_db_connection() as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Substitua este comentário pelo código que busca os dados de peneira e atletas
                cursor.execute("""
                    SELECT c.NomeClube, p.DataInicio, p.esportePeneira, p.Endereco, p.Estado, p.Cidade 
                    FROM peneira p 
                    JOIN cadclube c ON p.idClube = c.idClube 
                    WHERE p.idPeneira = %s
                """, (idPeneira,))
                peneira = cursor.fetchone()

                if not peneira:
                    flash('Peneira não encontrada.', 'danger')
                    return redirect(url_for('clube.home_clube'))

                cursor.execute("""
                    SELECT a.idAtleta, a.Nome, a.Sobrenome, i.NumeroCamisa, i.Posicao, i.status_avaliacao
                    FROM cadatleta a
                    JOIN infoatleta i ON a.idAtleta = i.idAtleta
                    WHERE i.idPeneira = %s
                """, (idPeneira,))
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
    
@clube_bp.route('/confirmar-logout')
def confirmar_logout():
    return render_template('confirmar_logout_clube.html')

@clube_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('usuario_id', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login.login'))
