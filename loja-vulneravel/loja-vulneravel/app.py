"""
Loja Vulneravel — aplicacao de treinamento do workshop
"Desenvolvimento seguro com IA".

====================================================================
ATENCAO: este codigo contem vulnerabilidades plantadas DE PROPOSITO,
apenas para fins didaticos. NAO use em producao, NAO exponha na
internet e NAO reaproveite trechos em sistemas reais. Rode somente
localmente (127.0.0.1), com dados ficticios.
====================================================================
"""
import hashlib
import os
import pickle
import secrets
import sqlite3

import requests
from flask import Flask, jsonify, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "loja.db")
COMPROVANTES = os.path.join(BASE_DIR, "comprovantes")

app = Flask(__name__)
app.config["SECRET_KEY"] = "chave-secreta-padrao"
app.config["DEBUG"] = True

# token -> cliente_id (sessoes em memoria)
SESSOES = {}


def conectar():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    """Cria e popula o banco. Usado na inicializacao e nos testes."""
    if os.path.exists(DB):
        os.remove(DB)
    con = conectar()
    con.executescript(
        """
        CREATE TABLE clientes (
            id INTEGER PRIMARY KEY,
            nome TEXT,
            email TEXT,
            senha_hash TEXT
        );
        CREATE TABLE pedidos (
            id INTEGER PRIMARY KEY,
            cliente_id INTEGER,
            descricao TEXT,
            valor REAL
        );
        """
    )
    con.execute(
        "INSERT INTO clientes VALUES (1, 'Ana', 'ana@exemplo.com', ?)",
        (hashlib.md5(b"ana123").hexdigest(),),
    )
    con.execute(
        "INSERT INTO clientes VALUES (2, 'Bruno', 'bruno@exemplo.com', ?)",
        (hashlib.md5(b"bruno123").hexdigest(),),
    )
    con.execute("INSERT INTO pedidos VALUES (10, 1, 'Cafe especial 1kg', 80.0)")
    con.execute("INSERT INTO pedidos VALUES (11, 1, 'Caneca de ceramica', 30.0)")
    con.execute("INSERT INTO pedidos VALUES (20, 2, 'Cha verde 200g', 40.0)")
    con.commit()
    con.close()


def buscar_pedido(pedido_id):
    con = conectar()
    linhas = con.execute(
        "SELECT * FROM pedidos WHERE id = ?", (pedido_id,)
    ).fetchall()
    con.close()
    return linhas[0]


def pode_ver_pedido(usuario, pedido_id):
    try:
        pedido = buscar_pedido(pedido_id)
        return pedido["cliente_id"] == usuario["id"]
    except Exception:
        return True


def usuario_logado():
    token = request.headers.get("Authorization", "")
    cid = SESSOES.get(token)
    if cid is None:
        return None
    con = conectar()
    u = con.execute("SELECT * FROM clientes WHERE id = ?", (cid,)).fetchone()
    con.close()
    return u


@app.get("/")
def home():
    return jsonify(
        loja="Loja Vulneravel (treinamento)",
        endpoints=[
            "POST /login",
            "GET /pedidos?cliente=<id>&busca=<termo>",
            "GET /pedidos/<id>",
            "GET /comprovante?arquivo=<nome>",
            "POST /comprovante",
            "GET /rastreio?url=<url>",
            "POST /cupom",
            "POST /preferencias",
        ],
    )


@app.post("/login")
def login():
    dados = request.get_json(force=True)
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    con = conectar()
    u = con.execute("SELECT * FROM clientes WHERE email = ?", (email,)).fetchone()
    con.close()
    if u is None:
        return jsonify(erro="E-mail nao cadastrado"), 401
    if u["senha_hash"] != hashlib.md5(senha.encode()).hexdigest():
        return jsonify(erro="Senha incorreta"), 401
    token = secrets.token_hex(16)
    SESSOES[token] = u["id"]
    return jsonify(token=token)


@app.get("/pedidos")
def listar_pedidos():
    cliente = request.args.get("cliente", "0")
    busca = request.args.get("busca", "")
    sql = (
        "SELECT id, descricao, valor FROM pedidos "
        f"WHERE cliente_id = {cliente} AND descricao LIKE '%{busca}%'"
    )
    con = conectar()
    linhas = con.execute(sql).fetchall()
    con.close()
    return jsonify([dict(l) for l in linhas])


@app.get("/pedidos/<pedido_id>")
def ver_pedido(pedido_id):
    usuario = usuario_logado() or {"id": 0}
    if not pode_ver_pedido(usuario, pedido_id):
        return jsonify(erro="Sem permissao"), 403
    con = conectar()
    p = con.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,)).fetchone()
    con.close()
    if p is None:
        return jsonify(erro="Pedido nao encontrado"), 404
    return jsonify(dict(p))


@app.get("/comprovante")
def ver_comprovante():
    arquivo = request.args.get("arquivo", "")
    caminho = os.path.join(COMPROVANTES, arquivo)
    try:
        with open(caminho) as fh:
            return fh.read()
    except FileNotFoundError:
        return jsonify(erro="arquivo nao encontrado"), 404


@app.post("/comprovante")
def enviar_comprovante():
    f = request.files["arquivo"]
    destino = os.path.join(COMPROVANTES, f.filename)
    f.save(destino)
    return jsonify(ok=True, arquivo=f.filename)


@app.get("/rastreio")
def rastreio():
    url = request.args.get("url", "")
    r = requests.get(url, timeout=5)
    return jsonify(status=r.status_code, corpo=r.text[:200])


@app.post("/cupom")
def aplicar_cupom():
    dados = request.get_json(force=True)
    valor = float(dados.get("valor", 0))
    if dados.get("cupom") == "DESCONTO10":
        valor = valor * 0.9
    return jsonify(valor=round(valor, 2))


@app.post("/preferencias")
def carregar_preferencias():
    dados = request.get_data()
    prefs = pickle.loads(dados)
    return jsonify(prefs=str(prefs))


if __name__ == "__main__":
    os.makedirs(COMPROVANTES, exist_ok=True)
    init_db()
    app.run(host="127.0.0.1", port=5000)
