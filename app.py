import sqlite3
from flask import Flask, request, jsonify, g
from Globals import DATABASE_NAME

DATABASE_NAME = "controlestoque.sqlite"

app = Flask(__name__)


def get_db_connection():
    #Aqui, cria uma conexão com o banco de dados SQLite.
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE_NAME)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    #Essa é a rota raiz que retorna a versão da API.
    return (jsonify({"versao": 1}), 200)


def get_usuarios():
    #O get recupera todos os usuários do banco de dados.

    cur = get_db_connection().cursor()
    #conn = get_db_connection()
    #cursor = conn.cursor()
    resultset = cur.execute('SELECT * FROM tb_usuario').fetchall()
    usuarios = []
    for linha in resultset:
        id = linha[0]
        nome = linha[1]
        nascimento = linha[2]
        # usuarioObj = Usuario(nome, nascimento)
        usuarioDict = {
            "id": id,
            "nome": nome,
            "nascimento": nascimento
        }
        usuarios.append(usuarioDict)
    cur.close()
    #conn.close()
    return usuarios


def set_usuario(data):
    #O set faz a inserçãode um novo usuário no banco de dados.
    # Criação do usuário.
    nome = data.get('nome')
    nascimento = data.get('nascimento')
    # Persistir os dados no banco.
    cur = get_db_connection().cursor()
    #conn = get_db_connection()
    #cursor = conn.cursor()
    cur.execute(
        f'INSERT INTO tb_usuario(nome, nascimento) values ("{nome}", "{nascimento}")')
    cur.commit()
    id = cur.lastrowid
    data['id'] = id
    cur.close()
    # Retornar o usuário criado.
    return data


@app.route("/usuarios", methods=['GET', 'POST'])
def usuarios():
    #Aqui é a rota para listar ou criar usuários.
    if request.method == 'GET':
        # Listagem dos usuários
        usuarios = get_usuarios()
        return jsonify(usuarios), 200
    elif request.method == 'POST':
        # Recuperar dados da requisição: json.
        data = request.json
        data = set_usuario(data)
        return jsonify(data), 201


def get_usuario_by_id(id):
    # Esse get recupera um usuário pelo ID.
    usuarioDict = None
    conn = get_db_connection()
    cursor = conn.cursor()
    linha = cursor.execute(
        f'SELECT * FROM tb_usuario WHERE id = {id}').fetchone()
    if linha is not None:
        id = linha[0]
        nome = linha[1]
        nascimento = linha[2]
        # usuarioObj = Usuario(nome, nascimento)
        usuarioDict = {
            "id": id,
            "nome": nome,
            "nascimento": nascimento
        }
    conn.close()
    return usuarioDict


def update_usuario(id, data):
    # O update atualiza as informações de um usuário pelo ID.
    # Criação do usuário.
    nome = data.get('nome')
    nascimento = data.get('nascimento')

    # Persistir os dados no banco.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE tb_usuario SET nome = ?, nascimento = ? WHERE id = ?', (nome, nascimento, id))
    conn.commit()

    rowupdate = cursor.rowcount

    conn.close()
    # Retornar a quantidade de linhas.
    return rowupdate


@app.route("/usuarios/<int:id>", methods=['GET', 'DELETE', 'PUT'])
def usuario(id):
    #Essa rota é para pegar, deletar ou atualizar um usuário pelo ID.
    if request.method == 'GET':
        usuario = get_usuario_by_id(id)
        if usuario is not None:
            return jsonify(usuario), 200
        else:
            return {}, 404
    elif request.method == 'PUT':
        # Recuperar dados da requisição: json.
        data = request.json
        rowupdate = update_usuario(id, data)
        if rowupdate != 0:
            return (data, 201)
        else:
            return (data, 304)