from flask import Blueprint, Flask, render_template 
from routes_login import login_bp
from routes_atleta import atleta_bp
from routes_clube import clube_bp



app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Certifique-se de definir uma chave segura

# Registrando blueprints
app.register_blueprint(login_bp, url_prefix='/')
app.register_blueprint(atleta_bp, url_prefix='/atleta')  # Registra o Blueprint com um prefixoa
app.register_blueprint(clube_bp, url_prefix='/clube')    # Use apenas o prefixo '/clube'


@app.route('/quem-voce')
def quem_voce():
    titulo = "Quem é você?"
    mensagem = "Escolha uma das opções abaixo para continuar o cadastro."
    return render_template('QuemVoce.html', titulo=titulo, mensagem=mensagem)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
