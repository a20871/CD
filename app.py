from flask import Flask

import json, os, shutil
from flask.helpers import send_from_directory, send_file
from flask import Flask, jsonify, abort, request, make_response, render_template
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from werkzeug.utils import secure_filename
from utils import escrever_ficheiro, ler_ficheiro, verificar_ficheiro

app = Flask(__name__)


#@app.route('/')
#def hello_world():  # put application's code here
#    return 'Hello World!'


#if __name__ == '__main__':
#    app.run()



UPLOAD_PATH = "FicheirosCarregados/"

app = Flask(__name__, static_url_path="", template_folder='templates')
CORS(app)
app.config['SECRET_KEY'] = 'secret'
auth = HTTPBasicAuth()


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# Ler os dados dos ficheiros
canais = ler_ficheiro('canais')
mensagens = ler_ficheiro('mensagens')
utilizadores = ler_ficheiro('utilizadores')


# Página Principal
@app.route('/', methods=['GET'])
def root():
    if auth.current_user() != None:
        return send_from_directory("templates", "menu.html")
    return render_template("login.html")


# Obtem ficheiros
@app.route('/templates/<string:file_name>', methods=['GET'])
def get_template_file(file_name):
    return send_from_directory("templates", file_name)


# Página após o login
@app.route('/login', methods=['GET'])
@auth.login_required
def login():
    return render_template("menu.html")


# region 1 - MENSAGENS PERSISTENTES

# Enviar mensagem persistente
@app.route('/mensagens/enviar_mensagens', methods=['POST'])
@auth.login_required
def enviar_mensagem():
    username = auth.current_user()
    if not request.json or 'mensagem' and 'recetor' not in request.json:
        abort(400)

    dic = json.loads(request.json)

    pedido = str(dic['recetor'])
    recetores = pedido.split(',')

    if len([utilizador for utilizador in utilizadores if utilizador['username'] == username]) == 0:
        abort(404)
    # Adicionar os utilizadores a quem deve enviar a mensagem
    for recetor in recetores:
        if [utilizador for utilizador in utilizadores if utilizador['username'] == recetor]:
            nova_mensagem = {
                'id_mensagem': len(mensagens) + 1,
                'mensagem': str(dic['mensagem']),
                'remetente': username,
                'recetor': recetor,
                'status': 'Nao Lida',
            }
            # Adiciona a estrutura principal
            mensagens.append(nova_mensagem)
    # Escreve em ficheiros
    escrever_ficheiro('mensagens', mensagens)
    return jsonify(mensagens), 201


# Obtem lista de mensagens
@app.route('/mensagens/ver_mensagens', methods=['GET'])
@auth.login_required
def ver_mensagens():
    username = auth.current_user()

    todas_mensagens = []
    # Verificar se existe mensagens para o utilizador
    for mensagem in mensagens:
        if mensagem['recetor'] == username and mensagem['status'] != 'Removida':
            # Lista de todas as mensagens (tanto lidas como nao)
            todas_mensagens.append({'id_mensagem': mensagem['id_mensagem'], 'mensagem': mensagem['mensagem'],
                                    'remetente': mensagem['remetente'], 'status': mensagem['status']})
    return jsonify(todas_mensagens), 201


# Obtem mensagem especifica e torna-a lida
@app.route('/mensagens/ver_mensagens/<int:id_mensagem>', methods=['GET'])
@auth.login_required
def ver_mensagem(id_mensagem):
    username = auth.current_user()
    # Verificar se existe mensagens para o utilizador
    for mensagem in mensagens:
        if mensagem['recetor'] == username and mensagem['status'] != 'Removida' and mensagem[
            'id_mensagem'] == id_mensagem:
            # Alterar o estado para lido
            mensagem['status'] = 'Lida'
            # Lista de todas as mensagens (tanto lidas como nao)
            return jsonify({'id_mensagem': mensagem['id_mensagem'], 'mensagem': mensagem['mensagem'],
                            'remetente': mensagem['remetente']}), 201

    abort(404)


# Remover uma Mensagem
@app.route('/mensagens/remover_mensagem/<int:id_mensagem>', methods=['DELETE'])
@auth.login_required
def remover_mensagens(id_mensagem):
    username = auth.current_user()
    # Verificar se Existe Mensagens
    for mensagem in mensagens:
        if mensagem['id_mensagem'] == id_mensagem:
            if mensagem['recetor'] == username and mensagem['status'] != 'Eliminada':
                # Remover Mensagem Enviada
                mensagem['status'] = 'Eliminada'
                return jsonify(mensagens), 201
            else:
                abort(404)
    abort(404)


# Parte II - Serviço de Troca de Mensagens de Texto Instantâneas

# Registar Utilizador num Canal
@app.route('/canais/inserir_utilizador', methods=['POST'])
@auth.login_required
def inserir_utilizador():
    username = auth.current_user()
    if not request.json or 'id_canal' not in request.json:
        abort(400)

    dic = json.loads(request.json)
    # Verificar se Existe Canal
    canal = [canal for canal in canais if int(canal['id_canal']) == int(dic['id_canal'])]
    # Caso Não Exista o Canal
    if len(canal) != 1:
        abort(404)

    utilizador = [utilizador for utilizador in canal[0]['utilizadores'] if utilizador == username]
    # Caso Não Exista o Utilizador
    if len(utilizador) != 0:
        abort(404)

    for canal in canais:
        if canal['id_canal'] == int(dic['id_canal']):
            # Adiciona Utilizador ao Canal
            canal['utilizadores'].append(username)

    escrever_ficheiro('canais', canais)
    return jsonify(canais), 201


# Remover Utilizador de um Canal
@app.route('/canais/remover_utilizador/<int:id_canal>', methods=['DELETE'])
@auth.login_required
def remover_utilizador_canal(id_canal):
    username = auth.current_user()

    # Verifica se Existe o Canal
    canal = [canal for canal in canais if canal['id_canal'] == id_canal]
    if len(canal) == 0:
        abort(404)

    for utilizador in canal[0]['utilizadores']:
        if utilizador == username:
            # Remover Utilizador
            canal[0]['utilizadores'].remove(utilizador)

            escrever_ficheiro('canais', canais)
            return jsonify(canais), 201

    # Caso Não Exista o Utilizador
    abort(404)


# Parte III -  Serviço de Transferência de Ficheiros

# Carregar Ficheiro
@app.route('/ficheiros/carregar', methods=['POST'])
@auth.login_required
def carregar():
    if 'ficheiro' not in request.files:
        abort(400)

    username = auth.current_user()
    path = UPLOAD_PATH + username
    if not os.path.exists(path):
        os.makedirs(path)

    f = request.files['ficheiro']
    f.save(os.path.join(path, secure_filename(f.filename)))
    return jsonify("Ficheiro Guardado!"), 201


# Descarregar Ficheiro
@app.route('/ficheiros/download/<string:nome_ficheiro>', methods=['GET'])
@auth.login_required
def download(nome_ficheiro):
    username = auth.current_user()
    path = UPLOAD_PATH + username + "/" + nome_ficheiro
    if not verificar_ficheiro(path):
        abort(404)

    return send_file(path + "/" + nome_ficheiro, as_attachment=True, attachment_filename='')


# Lista de Ficheiros
@app.route('/ficheiros/lista', methods=['GET'])
@auth.login_required
def lista_ficheiros():
    username = auth.current_user()
    path = UPLOAD_PATH + username
    if not os.path.exists(path):
        abort(404)

    ficheiros = []
    for f in os.listdir(path):
        if verificar_ficheiro(path + "/" + f):
            ficheiros.append(f)

    return jsonify(ficheiros), 200


# Apagar Ficheiro
@app.route('/ficheiros/remover/<string:nome_ficheiro>', methods=['DELETE'])
@auth.login_required
def remover(nome_ficheiro):
    username = auth.current_user()
    path = UPLOAD_PATH + username + "/" + nome_ficheiro
    if not verificar_ficheiro(path):
        abort(404)

    os.remove(path)

    return jsonify("Ficheiro Removido!"), 200


# Parte IV -  Serviço de Gestão de Utilizadores

@auth.get_password
def get_password(username):
    for utilizador in utilizadores:
        if username == utilizador['username']:
            return utilizador['password']
    return None


# Criar Utilizador
@app.route('/utilizadores/criar_conta', methods=['POST'])
def criar_conta():
    if not request.json or 'username' and 'password' not in request.json:
        abort(400)

    dic = json.loads(request.json)
    # Verificar se Já Existe
    utilizador = [utilizador for utilizador in utilizadores if utilizador['username'] == str(dic['username'])]
    # Se Existir Emite Erro
    if len(utilizador) != 0 and str(dic['username']) != "" and str(dic['password']) != "":
        abort(404)
    # Cria Utilizador
    novo_utilizador = {
        'username': str(dic['username']),
        'password': str(dic['password']),
        'admin': False,
    }

    utilizadores.append(novo_utilizador)
    escrever_ficheiro('utilizadores', utilizadores)
    return jsonify('Inserido com Sucesso!'), 201


# Alterar Password
@app.route('/utilizadores/alterar_password', methods=['PUT'])
@auth.login_required
def alterar_password():
    username = auth.current_user()
    permissao = obter_permissao(username)

    if not request.json or 'username' and 'password' not in request.json or not permissao:
        abort(400)

    dic = json.loads(request.json)
    # Verificar se Existe Utilizador
    utilizador = [utilizador for utilizador in utilizadores if utilizador['username'] == str(dic['username'])]
    # Alterar Password
    if len(utilizador) != 0 and str(dic['password']) != "":
        utilizador[0]['password'] = str(dic['password'])
    else:
        abort(404)

    escrever_ficheiro('utilizadores', utilizadores)
    return jsonify('Alterado com Sucesso!'), 201


# Remover de Conta
@app.route('/utilizadores/remover', methods=['DELETE'])
@auth.login_required
def remover_utilizador():
    username = auth.current_user()
    permissao = obter_permissao(username)

    if not request.json or 'username' not in request.json or not permissao:
        abort(400)

    dic = json.loads(request.json)

    for utilizador in utilizadores:
        if utilizador['username'] == str(dic['username']):
            utilizadores.remove(utilizador)
            path = UPLOAD_PATH + username
            if os.path.exists(path):
                shutil.rmtree(path)
            escrever_ficheiro('utilizadores', utilizadores)
            return jsonify('Removido com Sucesso'), 201
    abort(404)


# Criar Canal
@app.route('/canais/criar_canal', methods=['POST'])
@auth.login_required
def criar_canal():
    username = auth.current_user()
    permissao = obter_permissao(username)

    if not request.json or 'nome' not in request.json or not permissao:
        abort(400)

    dic = json.loads(request.json)
    novo_canal = {
        'id_canal': len(canais) + 1,
        'nome': str(dic['nome']),
        'utilizadores': [],
    }

    # Adiciona Novo Canal
    canais.append(novo_canal)
    escrever_ficheiro('canais', canais)
    return jsonify(canais), 201


def obter_permissao(username):
    for utilizador in utilizadores:
        if username == utilizador['username']:
            return utilizador['admin']


if __name__ == '__main__':
    app.run(debug=True)