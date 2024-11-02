from flask import Flask, render_template
from routes_login import login_bp
from routes_atleta import atleta_bp
from routes_clube import clube_bp

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_super_segura'

# Registrando blueprints
app.register_blueprint(login_bp)
app.register_blueprint(atleta_bp, url_prefix='/atleta')  
app.register_blueprint(clube_bp, url_prefix='/clube')  # Prefixo '/clube' para as rotas do clube

@app.route('/quem-voce')
def quem_voce():
    titulo = "Quem é você?"
    mensagem = "Escolha uma das opções abaixo para continuar o cadastro."
    return render_template('QuemVoce.html', titulo=titulo, mensagem=mensagem)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
