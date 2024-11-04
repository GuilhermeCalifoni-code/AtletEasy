from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from db import get_db_connection
from mysql.connector import Error
import re  # Importa o módulo para usar expressões regulares

atleta_bp = Blueprint('atleta', __name__)

# Rota para cadastro de atleta
@atleta_bp.route('/cadastro-atleta', methods=['GET', 'POST'])
def cadastro_atleta():
    if request.method == 'POST':
        # Lógica para capturar e salvar os dados do formulário no banco de dados
        nome = request.form['nomeAtleta']
        sobrenome = request.form['sobrenome']
        data_nascimento = request.form['dataNascimento']
        cpf = request.form['cpf']
        usuario = request.form['usuario']
        cep = request.form['cep']
        endereco = request.form['endereco']
        numero = request.form['numeroEndereco']
        complemento = request.form.get('complemento', '')
        senha = request.form['senha']

        try:
            with get_db_connection() as conexao:
                with conexao.cursor() as cursor:
                    query = """
                        INSERT INTO cadatleta (
                            Usuario, Senha, Nome, Sobrenome, DataDeNascimento, Endereco, CPF, CEP, NumeroEndereco, Complemento
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    valores = (usuario, senha, nome, sobrenome, data_nascimento, endereco, cpf, cep, numero, complemento)
                    cursor.execute(query, valores)
                    conexao.commit()
                    flash('Cadastro de atleta realizado com sucesso!', 'success')
                    return redirect(url_for('login.login'))
        except Error as err:
            flash(f'Erro ao cadastrar atleta: {err}', 'danger')

    return render_template('cadAtleta.html')

# Rota para a página de pagamento do atleta
@atleta_bp.route('/paga-atleta')
def paga_atleta():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login.login'))
    return render_template('pgatleta.html')


@atleta_bp.route('/home')
def home_atleta():
    return render_template('HomeAtleta.html')

# Rota para visualizar o perfil do atleta
@atleta_bp.route('/perfil-atleta')
def perfil_atleta():
    print("Acessando perfil do atleta. Sessão atual:", session)  # Depuração da sessão
    
    if 'usuario_id' not in session:
        print("Usuário não autenticado, redirecionando para login.")  # Depuração de redirecionamento
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login.login'))

    usuario_id = session['usuario_id']

    try:
        with get_db_connection() as conexao:
            with conexao.cursor(dictionary=True) as cursor:
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
                return redirect(url_for('atleta.home_atleta'))

            return render_template('perfilAtleta.html', atleta=atleta)
    except Error as err:
        flash(f'Erro ao recuperar o perfil do atleta: {err}', 'danger')
        return redirect(url_for('atleta.home_atleta'))

# Rota para editar o perfil do atleta
@atleta_bp.route('/editar-perfil', methods=['GET', 'POST'])
def editar_perfil():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para acessar esta página.', 'warning')
        return redirect(url_for('login.login'))

    usuario_id = session['usuario_id']

    if request.method == 'POST':
        # Captura os dados do formulário
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
            with get_db_connection() as conexao:
                with conexao.cursor() as cursor:
                    # Verifica se o registro existe antes de atualizar
                    cursor.execute("SELECT * FROM infoatleta WHERE idAtleta = %s", (usuario_id,))
                    registro = cursor.fetchone()
                    
                    if registro:
                        # Atualiza o registro existente
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
                    else:
                        # Cria um novo registro se não existir
                        query = """
                        INSERT INTO infoatleta (idAtleta, Posicao, Altura, Peso, Experiencia, 
                                                SobreMim, Velocidade, Tecnica, VisaoDeJogo, 
                                                Gols, Assistencias, Cartoes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        valores = (usuario_id, posicao, altura, peso, experiencia, sobre_mim, velocidade, tecnica, visao_de_jogo, gols, assistencias, cartoes)
                        cursor.execute(query, valores)
                        conexao.commit()
                        flash('Perfil criado com sucesso!', 'success')

                    return redirect(url_for('atleta.perfil_atleta'))
        except Error as err:
            flash(f'Erro ao atualizar o perfil: {err}', 'danger')
            return redirect(url_for('atleta.editar_perfil'))

    # Carrega os dados para edição
    try:
        with get_db_connection() as conexao:
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
        return redirect(url_for('atleta.perfil_atleta'))

#INCREVER-SE NA PENEIRA
@atleta_bp.route('/inscrever-peneira/<int:idPeneira>', methods=['POST'])
def inscrever_peneira(idPeneira):
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para se inscrever em uma peneira.', 'warning')
        return redirect(url_for('login.login'))

    try:
        with get_db_connection() as conexao:
            with conexao.cursor() as cursor:
                query = "INSERT INTO inscricoes (idAtleta, idPeneira) VALUES (%s, %s)"
                cursor.execute(query, (session['usuario_id'], idPeneira))
                conexao.commit()
                flash('Inscrição realizada com sucesso!', 'success')
    except Error as err:
        flash(f'Erro ao realizar a inscrição: {err}', 'danger')
    return redirect(url_for('atleta.visualizar_peneiras'))

#SAIR DA PENEIRA
@atleta_bp.route('/sair-peneira/<int:idPeneira>', methods=['POST'])
def sair_peneira(idPeneira):
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para sair de uma peneira.', 'warning')
        return redirect(url_for('login.login'))

    try:
        with get_db_connection() as conexao:
            with conexao.cursor() as cursor:
                cursor.execute("DELETE FROM inscricoes WHERE idAtleta = %s AND idPeneira = %s",
                               (session['usuario_id'], idPeneira))
                conexao.commit()
                flash('Inscrição cancelada com sucesso!', 'success')
    except Error as err:
        flash(f'Erro ao cancelar a inscrição: {err}', 'danger')
    return redirect(url_for('atleta.visualizar_peneiras'))

#RESULTADO DA PENEIRA
@atleta_bp.route('/resultado-peneira')
def resultado_peneira():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para ver o resultado das peneiras.', 'warning')
        return redirect(url_for('login.login'))

    try:
        with get_db_connection() as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                query = """
                SELECT p.esportePeneira, p.DataInicio, a.status_avaliacao
                FROM inscricoes i
                JOIN peneira p ON i.idPeneira = p.idPeneira
                LEFT JOIN infoatleta a ON i.idAtleta = a.idAtleta
                WHERE i.idAtleta = %s
                """
                cursor.execute(query, (session['usuario_id'],))
                resultados = cursor.fetchall()
                if not resultados:
                    flash('Você ainda não foi avaliado em nenhuma peneira.', 'info')
                return render_template('resultadoPeneira.html', resultados=resultados)
    except Error as err:
        flash(f'Erro ao carregar os resultados: {err}', 'danger')
        return redirect(url_for('atleta.home_atleta'))

# Rota para visualizar as peneiras disponíveis para inscrição
@atleta_bp.route('/visualizar-peneiras')
def visualizar_peneiras():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para ver as peneiras.', 'warning')
        return redirect(url_for('login.login'))

    try:
        with get_db_connection() as conexao:
            with conexao.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT p.*, c.NomeClube,
                    EXISTS(
                        SELECT 1 FROM inscricoes i WHERE i.idPeneira = p.idPeneira AND i.idAtleta = %s
                    ) as inscrito
                    FROM peneira p
                    JOIN cadclube c ON p.idClube = c.idClube
                    WHERE p.status = 'Aberto'
                """, (session['usuario_id'],))
                peneiras = cursor.fetchall()

        return render_template('visualizarPeneiras.html', peneiras=peneiras)
    except Error as err:
        flash(f'Erro ao recuperar as peneiras: {err}', 'danger')
        return redirect(url_for('atleta.home_atleta'))

#CONFIRMAR PRA SAIR    
@atleta_bp.route('/confirmar-logout')
def confirmar_logout():
    # Renderiza uma página de confirmação de logout
    return render_template('confirmar_logout.html')

@atleta_bp.route('/logout', methods=['POST'])
def logout():
    # Finaliza a sessão do usuário e redireciona para a página de login
    session.pop('usuario_id', None)
    flash('Você saiu da sua conta.', 'info')
    return redirect(url_for('login.login'))


