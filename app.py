import sqlite3
from flask import Flask, request, jsonify, g
from Globals import DATABASE_NAME


app = Flask(__name__)


def get_db_connection():
    # Aqui, cria uma conexão com o banco de dados SQLite.
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
    # Essa é a rota raiz que retorna a versão da API.
    return (jsonify({"versao": 1}), 200)


def get_usuarios():
    # O get recupera todos os usuários do banco de dados.

    cur = get_db_connection().cursor()
    result_set = cur.execute('SELECT * FROM tb_usuario').fetchall()
    usuarios = []
    for linha in result_set:
        id = linha[0]
        nome = linha[1]
        nascimento = linha[2]
        # usuarioObj = Usuario(nome, nascimento)
        usuario_dict = {
            "id": id,
            "nome": nome,
            "nascimento": nascimento
        }
        usuarios.append(usuario_dict)
    cur.close()
    # conn.close()
    return usuarios


def set_usuario(data):
    # O set faz a inserçãode um novo usuário no banco de dados.
    # Criação do usuário.
    # não alterei de acordo com a de cima porque estava dando erro do jeito antigo
    nome = data.get('nome')
    nascimento = data.get('nascimento')
    # Persistir os dados no banco.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f'INSERT INTO tb_usuario(nome, nascimento) values ("{nome}", "{nascimento}")')
    conn.commit()
    id = cursor.lastrowid
    data['id'] = id
    cursor.close()
    # Retornar o usuário criado.
    return data


@app.route("/usuarios", methods=['GET', 'POST'])
def usuarios():
    # Aqui é a rota para listar ou criar usuários.
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
    usuario_dict = None
    conn = get_db_connection()
    cursor = conn.cursor()
    linha = cursor.execute(
        f'SELECT * FROM tb_usuario WHERE id = {id}').fetchone()
    if linha is not None:
        id = linha[0]
        nome = linha[1]
        nascimento = linha[2]
        # usuarioObj = Usuario(nome, nascimento)
        usuario_dict = {
            "id": id,
            "nome": nome,
            "nascimento": nascimento
        }
    conn.close()
    return usuario_dict


def update_usuario(id, data):
    # O update atualiza as informações de um usuário pelo ID.
    # Criação do usuário.
    nome = data.get('nome')
    nascimento = data.get('nascimento')

    # Persistir os dados no banco.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'UPDATE tb_usuario SET nome = ?, nascimento = ? WHERE id = ?',
        (nome, nascimento, id)
    )
    conn.commit()

    row_update = cursor.rowcount

    conn.close()
    # Retornar a quantidade de linhas.
    return row_update


def delete_usuario(id):
    # Esse deleta um usuário pelo ID.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'DELETE FROM tb_usuario WHERE id = {id}')
    conn.commit()
    conn.close()
    return cursor.rowcount


@app.route("/usuarios/<int:id>", methods=['GET', 'DELETE', 'PUT'])
def usuario(id):
    # Essa rota é para pegar, deletar ou atualizar um usuário pelo ID.
    if request.method == 'GET':
        usuario = get_usuario_by_id(id)
        if usuario is not None:
            return jsonify(usuario), 200
        else:
            return jsonify({}), 404
    elif request.method == 'PUT':
        # Recuperar dados da requisição: json.
        data = request.json
        row_update = update_usuario(id, data)
        if row_update != 0:
            return jsonify(data, 201)
        else:
            return jsonify(data, 304)
    elif request.method == 'DELETE':
        # Deletar dados da requisição: json.
        row_count = delete_usuario(id)
        if row_count != 0:
            return jsonify(
                {"message": f"Usuário {id} excluído com sucesso"}
            ), 200

        elif row_count == 0:
            # return ({"message": f"Usuário {id} Não econtrado"}), 304
            return jsonify("Usuário Não encontrado")

        else:
            return jsonify({"message": f"Usuário {id} Não foi excluído"}), 404
